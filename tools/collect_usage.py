#!/usr/bin/env python3
"""Collect real subscription-quota usage from the running wake's own stream log.

Why this exists
---------------
`state/claude-usage.json` used to be written only by the Claude Code status
line (`~/.claude/terrarium-statusline.sh`). The status line is invoked by the
interactive TUI only, so headless `claude -p` wakes never refreshed it. The
file froze at its first-ever reading (5h=1%, 7d=0%) on 2026-09-04 and every
later wake read that as current. Ground truth for the same period: the
five-hour window climbed to 100% and killed the 2026-09-05 08:28Z wake.

The reliable source is the wake's own stream: `claude -p --output-format
stream-json` emits `rate_limit_event` records carrying
`rate_limit_info.unifiedWindows.{five_hour,seven_day}`. This reads the newest
such record and writes it to `state/claude-usage.json` in the shape the
launcher already expects, tagged with `source` and `observed_at` so a stale
reading can never again be mistaken for a current one.

Usage:
  collect_usage.py            # refresh state/claude-usage.json, print summary
  collect_usage.py --check    # only report freshness, exit 1 if stale/missing
  collect_usage.py --history  # per-run quota table across all recorded wakes
"""

import argparse
import datetime as dt
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quota

TERRARIUM = os.path.expanduser("~/terrarium")
RAW = os.path.join(TERRARIUM, "logs", "raw")
OUT = os.path.join(TERRARIUM, "state", "claude-usage.json")

# A reading older than this is not evidence about the current window.
STALE_AFTER_SECONDS = 90 * 60


def runs():
    """(run_id, stream_path) for every recorded run, oldest first."""
    paths = sorted(glob.glob(os.path.join(RAW, "*", "claude-stream.jsonl")))
    return [(os.path.basename(os.path.dirname(p)), p) for p in paths]


def refresh():
    """Write the newest reading anywhere, with a bound on when it was observed.

    The events carry no timestamp, so `observed_at` used to be set to the time
    this script happened to run. Re-reading a day-old event therefore made it
    look brand new. Now the reading is stamped with the bounds recoverable from
    its own run — `observed_not_before` (run start) and `observed_not_after`
    (last write to that run's stream log) — which do not move on re-read.
    `collected_at` records when this script last processed it, separately.
    """
    run_id, reading, not_before, not_after = quota.latest_reading()
    if reading is None:
        return None, "no rate_limit_event found in any stream log"
    doc = dict(reading)
    doc.pop("event_ordinal", None)
    doc.update(
        {
            "source": "stream:rate_limit_event",
            "run_id": run_id,
            "observed_not_before": not_before,
            "observed_not_after": not_after,
            # Kept for the launcher, which reads `.observed_at` from this file.
            # Defined as the latest possible observation time, never as now().
            "observed_at": not_after,
            "collected_at": _now_iso(),
            "window_state": quota.window_state(reading),
        }
    )
    tmp = OUT + ".tmp"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, OUT)
    return doc, None


def _now_iso():
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _age_seconds(doc):
    """Seconds since the reading was *at latest* observed. Conservative: uses
    `observed_not_after`, so a reading is never reported fresher than it is."""
    ts = doc.get("observed_not_after") or doc.get("observed_at")
    if not ts:
        return None
    try:
        when = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (dt.datetime.now(dt.timezone.utc) - when).total_seconds()


def describe(doc):
    age = _age_seconds(doc)
    reset = doc.get("five_hour_resets_at")
    if isinstance(reset, (int, float)):
        left = (reset - dt.datetime.now(dt.timezone.utc).timestamp()) / 60.0
        resets = "%s (%+.0f min)" % (
            dt.datetime.fromtimestamp(reset, dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            left,
        )
    else:
        resets = "unknown"
    return (
        "5h %s%%  7d %s%%  status=%s\n"
        "five-hour window resets %s\n"
        "observed no later than %s (%s), source=%s run=%s, window=%s"
        % (
            doc.get("five_hour_used_percentage"),
            doc.get("seven_day_used_percentage"),
            doc.get("status"),
            resets,
            doc.get("observed_not_after") or doc.get("observed_at"),
            "age unknown" if age is None else "at least %.0f min old" % (age / 60),
            doc.get("source"),
            doc.get("run_id"),
            doc.get("window_state", "unknown"),
        )
    )


def check():
    if not os.path.exists(OUT):
        print("STALE: %s does not exist" % OUT)
        return 1
    with open(OUT, encoding="utf-8") as fh:
        doc = json.load(fh)
    age = _age_seconds(doc)
    print(describe(doc))
    if doc.get("window_state") == "expired_window":
        print("\nSTALE: this reading belongs to a five-hour window that has ended.")
        return 1
    if age is None or age > STALE_AFTER_SECONDS:
        print("\nSTALE: this reading is not evidence about the current window.")
        return 1
    print("\nFRESH.")
    return 0


def history():
    print("%-28s %-12s %-12s %-8s %s" % ("run", "5h start", "5h end", "7d end", "5h resets"))
    for run_id, path in runs():
        evs = _events(path)
        if not evs:
            print("%-28s %-12s" % (run_id, "(no data)"))
            continue
        f0, _ = _windows(evs[0])
        f1, s1 = _windows(evs[-1])
        reset = f1.get("resetsAt")
        print(
            "%-28s %-12s %-12s %-8s %s"
            % (
                run_id,
                _pct(f0),
                _pct(f1),
                _pct(s1),
                dt.datetime.fromtimestamp(reset, dt.timezone.utc).strftime("%m-%d %H:%M")
                if isinstance(reset, (int, float))
                else "?",
            )
        )


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="report freshness only; exit 1 if stale")
    ap.add_argument("--history", action="store_true", help="per-run quota table")
    args = ap.parse_args()

    if args.history:
        history()
        return 0
    if args.check:
        return check()

    doc, err = refresh()
    if err:
        print("FAILED: %s" % err, file=sys.stderr)
        return 1
    print(describe(doc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
