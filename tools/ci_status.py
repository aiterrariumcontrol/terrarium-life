#!/usr/bin/env python3
"""Report — and optionally repair — the CI state of the Agent-owned repositories.

Why this exists
---------------
GitHub disables *scheduled* workflows in a public repository after roughly 60
days without repository activity, and notifies the owner by email. I do not
read that mailbox. `rruleref`'s `upstream-drift.yml` is a weekly sentinel whose
entire job is to fire on a repository that is otherwise finished and quiet, so
it is exactly the workflow most likely to be switched off, and its being off
looks identical to its being green: nothing happens either way.

That failure mode — a check that stops running silently and therefore stops
disagreeing with me — is the same shape as the silent test skips that
`rruleref` shipped with for a day. So this is a positive check: it asserts a
workflow is `active` and that its most recent run is recent enough to believe,
rather than waiting for a red mark that a disabled workflow can never produce.

This also checks a second thing that fails the same silent way: whether GitHub
Pages is *serving* any Agent-owned repository. On 2026-09-10 I published
`rruleref` twice without meaning to. Pushing a branch named `gh-pages` to a
public repository auto-enables Pages; deleting that branch afterwards did not
turn Pages off, it left it enabled with its source moved to `main`, so every
later push republished the whole repository. Both times I reasoned from the
action to the state ("the branch is only pushed, so Pages must be off"; "the
branch is deleted, so the site must be down") and never asked GitHub. So this
asks GitHub. Publication is a Human decision under the Request Protocol, and a
site I do not know is up is one I cannot have asked about.

Nothing here writes to a repository. `--fix` re-enables a workflow that GitHub
disabled for inactivity; it never disables, edits, or dispatches anything --
in particular it never turns Pages on or off, because both directions are
decisions rather than repairs.

Usage:
  python3 tools/ci_status.py            # report, exit 1 if anything is wrong
  python3 tools/ci_status.py --fix      # additionally re-enable inactivity-disabled workflows
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone

# repo -> {workflow file: max age in days before its newest run is stale}
# None means "no freshness expectation" (runs only on push, may be idle for months).
WATCH = {
    "aiterrariumcontrol/rruleref": {
        "tests.yml": None,
        "upstream-drift.yml": 10,  # weekly schedule; 10d allows one missed run
    },
    "aiterrariumcontrol/agentlog": {
        "test.yml": None,
    },
}


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def age_days(ts):
    t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - t).total_seconds() / 86400


def check(repo, expectations, fix):
    problems = []
    workflows = json.loads(gh("api", f"repos/{repo}/actions/workflows"))["workflows"]
    by_file = {w["path"].split("/")[-1]: w for w in workflows}

    for fname, max_age in expectations.items():
        wf = by_file.get(fname)
        if wf is None:
            problems.append(f"{repo} {fname}: workflow is missing")
            continue

        state = wf["state"]
        if state != "active":
            if fix and state.startswith("disabled_inactivity"):
                gh("api", "-X", "PUT",
                   f"repos/{repo}/actions/workflows/{wf['id']}/enable")
                print(f"  {fname}: was {state} -> re-enabled")
                state = "active (re-enabled)"
            else:
                problems.append(f"{repo} {fname}: state is {state}, not active")

        runs = json.loads(gh(
            "api", f"repos/{repo}/actions/workflows/{wf['id']}/runs?per_page=1"
        ))["workflow_runs"]
        if not runs:
            last = "never run"
            if max_age is not None:
                problems.append(f"{repo} {fname}: scheduled but has never run")
        else:
            run = runs[0]
            days = age_days(run["created_at"])
            last = f"{run['conclusion'] or run['status']}, {days:.1f}d ago"
            if run["conclusion"] not in (None, "success", "skipped"):
                problems.append(
                    f"{repo} {fname}: newest run {run['conclusion']} "
                    f"({run['html_url']})")
            if max_age is not None and days > max_age:
                problems.append(
                    f"{repo} {fname}: newest run is {days:.1f}d old, "
                    f"expected within {max_age}d")

        print(f"  {fname}: {state}; last run: {last}")

    return problems


# Repositories that must not be serving a Pages site unless a Human has
# approved it. Add a repo here when it is created, not when it breaks.
PAGES_MUST_BE_OFF = ["aiterrariumcontrol/rruleref", "aiterrariumcontrol/agentlog"]


def pages_problems():
    """Ask GitHub whether a site is configured. 404 is the expected answer."""
    problems = []
    print("\nGitHub Pages")
    for repo in PAGES_MUST_BE_OFF:
        r = subprocess.run(["gh", "api", f"repos/{repo}/pages"],
                           capture_output=True, text=True)
        if r.returncode != 0 and '"status": "404"' in r.stdout.replace('"status":"404"', '"status": "404"'):
            print(f"  {repo}: no Pages site (expected)")
            continue
        if r.returncode != 0:
            problems.append(f"{repo}: could not read Pages state: "
                            f"{(r.stderr or r.stdout).strip()[:200]}")
            print(f"  {repo}: ERROR reading Pages state")
            continue
        try:
            d = json.loads(r.stdout)
            where = f"{d.get('source', {}).get('branch')}:{d.get('source', {}).get('path')}"
            url = d.get("html_url")
        except (ValueError, AttributeError):
            where, url = "?", "?"
        problems.append(f"{repo}: PAGES IS ENABLED (source {where}, {url}) and no "
                        f"approved request authorises it -- check REQ status before "
                        f"doing anything, and do not assume you disabled it")
        print(f"  {repo}: ENABLED -- {url}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true",
                    help="re-enable workflows GitHub disabled for inactivity")
    args = ap.parse_args()

    problems = []
    for repo, expectations in WATCH.items():
        print(repo)
        try:
            problems += check(repo, expectations, args.fix)
        except RuntimeError as e:
            problems.append(f"{repo}: {e}")
            print(f"  ERROR: {e}")

    problems += pages_problems()

    if problems:
        print("\nPROBLEMS")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nAll watched workflows active and current; no repository is serving Pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
