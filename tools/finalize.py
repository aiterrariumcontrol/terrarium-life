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

Usage: finalize.py [--dry-run]
"""

import fcntl
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
LIFE = HERE.parent
LOCK = pathlib.Path("/tmp/ai-terrarium-finalize.lock")

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


def main():
    dry = "--dry-run" in sys.argv

    fh = os.open(LOCK, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return 0  # a previous invocation is still running; not an error

    if agent_wake_running():
        return 0

    # Refresh the quota cache from whatever streams exist. Failure here is not
    # fatal: the index reads the stream logs directly.
    collect_usage.refresh()

    text = wake_index.render()
    if wake_index.OUT.exists() and wake_index.OUT.read_text() == text:
        return 0
    if dry:
        print("would update", wake_index.OUT)
        return 0

    wake_index.OUT.write_text(text)

    rel = wake_index.OUT.relative_to(LIFE).as_posix()
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
