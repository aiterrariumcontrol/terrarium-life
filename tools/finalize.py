#!/usr/bin/env python3
"""Finalize and publish wake records without waiting for the next wake.

The runtime launcher writes `runs/<date>/<run-id>.json` after a wake ends, but
nothing regenerates `reports/wake-index.md` until some later wake happens to run
`wake_index.py`. The index was therefore always one wake behind — the newest
completed wake was invisible to a Human observer until another one started
(aiterrariumcontrol/terrarium-life#3, problem 1).

This closes that gap with an ordinary program instead of an LLM wake. A cron job
runs it every few minutes; it does nothing at all unless something changed.

It deliberately never rewrites a recorded observation. It refreshes the local
quota cache, regenerates the derived index, and commits only if the result
differs from what is already published.

Two modes:

  finalize.py                 cron mode: skip while a wake is running, then
                              regenerate, commit and push if content changed.
  finalize.py --stage-only    launcher mode: regenerate and `git add` only.
                              No guards (the launcher already holds the run
                              lock) and no commit/push (the launcher does that
                              itself, in the same commit as the run record).

Launcher mode is the one that actually closes the gap: publication happens in
the launcher's own post-exit commit, so the newest wake is visible the moment
the wake ends, with no second commit and no LLM invocation. Cron mode stays as
a fallback for wakes that die before the launcher reaches its commit.
"""

import fcntl
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
LIFE = HERE.parent
LOCK = pathlib.Path("/tmp/ai-terrarium-finalize.lock")
# The launcher holds this for the whole of every wake; see run-agent.
RUN_LOCK = "/run/lock/ai-terrarium-agent.lock"

sys.path.insert(0, str(HERE))
import collect_usage  # noqa: E402
import wake_index  # noqa: E402


def agent_wake_running():
    """Never race the launcher's own git commit/push at the end of a wake."""
    try:
        rc = subprocess.run(
            ["systemctl", "is-active", "--quiet", "ai-terrarium-agent.service"],
            timeout=30,
        ).returncode
    except (OSError, subprocess.SubprocessError):
        return False  # cannot tell; the flock and `git commit` guard still apply
    return rc == 0


def git(*args, check=True):
    return subprocess.run(
        ["git", "-C", str(LIFE), *args],
        check=check,
        capture_output=True,
        text=True,
        timeout=180,
    )


def regenerate(dry=False):
    """Refresh the quota cache and the index. Returns True if content changed.

    The timestamp in the index is preserved when nothing else changed, so an
    idle invocation writes nothing at all — no diff, no commit, no push.
    """
    # Failure here is not fatal: the index reads the stream logs directly.
    collect_usage.refresh()

    previous = wake_index.OUT.read_text() if wake_index.OUT.exists() else None
    text, changed = wake_index.render_stable(previous)
    if not changed:
        return False
    if dry:
        print("would update", wake_index.OUT)
        return True
    wake_index.OUT.write_text(text)
    return True


def main():
    dry = "--dry-run" in sys.argv
    stage_only = "--stage-only" in sys.argv
    rel = wake_index.OUT.relative_to(LIFE).as_posix()

    if stage_only:
        # Called from inside the launcher, which already holds
        # /run/lock/ai-terrarium-agent.lock for the whole wake. Taking the
        # service-active guard here would be self-defeating: the service *is*
        # active, which is exactly why the earlier cron-shaped script returned
        # immediately when dropped into this position.
        if regenerate(dry) and not dry:
            git("add", rel)
            print("staged", rel)
        return 0

    fh = os.open(LOCK, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return 0  # a previous invocation is still running; not an error

    # Exclusion against a wake is the launcher's own lock, not the service
    # check: a wake could start immediately after `systemctl is-active` says no.
    # Taking that lock non-blocking is what actually establishes exclusion; the
    # service check merely avoids a pointless attempt.
    if agent_wake_running():
        return 0
    try:
        # O_RDONLY is enough: flock(2) locks are independent of open mode,
        # and the file is root-owned and not writable by this account.
        run_lock = os.open(RUN_LOCK, os.O_RDONLY)
    except OSError:
        run_lock = None  # lock file absent: no wake has run since boot
    if run_lock is not None:
        try:
            fcntl.flock(run_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return 0  # a wake holds it; the launcher will publish on its own
        # Held for the rest of this function, released when the process exits.

    if not regenerate(dry) or dry:
        return 0

    git("add", rel)
    if not git("diff", "--cached", "--quiet", check=False).returncode:
        return 0  # staged nothing new

    git("commit", "-m", "Regenerate wake index after wake completion")
    push = git("push", check=False)
    if push.returncode:
        print("push failed:", push.stderr.strip(), file=sys.stderr)
        return 1
    print("published", rel)
    return 0


if __name__ == "__main__":
    sys.exit(main())
