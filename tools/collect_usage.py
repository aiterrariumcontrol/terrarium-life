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


def _age_bounds(doc):
    """(min_age, max_age) in seconds for how old this reading is, or (None, None).

    The events carry no timestamp, only the bounds recoverable from their run:
    `observed_not_before` (run start) and `observed_not_after` (last write to
    that run's stream log). The reading could have been taken anywhere in
    between, so:

      min_age = now - observed_not_after     (best case)
      max_age = now - observed_not_before    (worst case)

    Freshness must be judged on **max_age**. terrarium-life#3 caught the earlier
    version doing the opposite: with bounds of 10:00-11:59 checked at 12:00 it
    reported "at least 1 min old" and passed a 90-minute threshold, while the
    observation could in fact have been two hours old. `min_age` is still
    reported, but it can never on its own make a reading count as fresh.
    """
    now = dt.datetime.now(dt.timezone.utc)

    def age(ts):
        if not ts:
            return None
        try:
            when = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
        return (now - when).total_seconds()

    return age(doc.get("observed_not_after") or doc.get("observed_at")), age(
        doc.get("observed_not_before")
    )


def _window_state_now(doc):
    """Recompute five-hour window expiry from the reset stamp against the clock.

    Never trust `window_state` cached in the file: it was computed when the file
    was written, and a reset since then would leave it saying `current_window`
    for a window that has ended (terrarium-life#3, problem 3, second test).
    """
    resets = doc.get("five_hour_resets_at")
    if not isinstance(resets, (int, float)):
        return "unknown_window"
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    return "current_window" if now < resets else "expired_window"


def describe(doc):
    min_age, max_age = _age_bounds(doc)
    reset = doc.get("five_hour_resets_at")
    if isinstance(reset, (int, float)):
        left = (reset - dt.datetime.now(dt.timezone.utc).timestamp()) / 60.0
        resets = "%s (%+.0f min)" % (
            dt.datetime.fromtimestamp(reset, dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            left,
        )
    else:
        resets = "unknown"

    if max_age is None and min_age is None:
        age = "age unknown"
    elif max_age is None:
        age = "at least %.0f min old; upper bound unknown" % (min_age / 60)
    elif min_age is None:
        age = "at most %.0f min old" % (max_age / 60)
    else:
        age = "between %.0f and %.0f min old" % (min_age / 60, max_age / 60)

    return (
        "5h %s%%  7d %s%%  status=%s\n"
        "five-hour window resets %s\n"
        "observed within %s .. %s (%s), source=%s run=%s, window=%s"
        % (
            doc.get("five_hour_used_percentage"),
            doc.get("seven_day_used_percentage"),
            doc.get("status"),
            resets,
            doc.get("observed_not_before") or "?",
            doc.get("observed_not_after") or doc.get("observed_at") or "?",
            age,
            doc.get("source"),
            doc.get("run_id"),
            _window_state_now(doc),
        )
    )


def check():
    if not os.path.exists(OUT):
        print("STALE: %s does not exist" % OUT)
        return 1
    with open(OUT, encoding="utf-8") as fh:
        doc = json.load(fh)
    _, max_age = _age_bounds(doc)
    print(describe(doc))
    if _window_state_now(doc) == "expired_window":
        print("\nSTALE: this reading belongs to a five-hour window that has ended.")
        return 1
    if max_age is None:
        print("\nUNCERTAIN: this reading's observation time has no lower bound, so")
        print("its age cannot be established. Treat it as not evidence about now.")
        return 1
    if max_age > STALE_AFTER_SECONDS:
        print("\nSTALE: could be up to %.0f min old, over the %.0f min threshold."
              % (max_age / 60, STALE_AFTER_SECONDS / 60))
        return 1
    print("\nFRESH: at most %.0f min old, in the current five-hour window."
          % (max_age / 60))
    return 0


def history():
    """Per-run quota table. Rebuilt on quota.run_report: the previous version
    still called helpers that had been removed and raised NameError on use."""
    print("%-26s %-22s %-22s %-28s %s"
          % ("run", "5h before -> after", "7d before -> after", "span", "completion"))
    for run_id, rep in sorted(quota.all_run_reports().items()):
        if not rep.get("after"):
            print("%-26s %s" % (run_id, "(no rate_limit_event)"))
            continue

        def pair(unit):
            b = (rep.get("before") or {}).get("%s_used_percentage" % unit)
            a = (rep.get("after") or {}).get("%s_used_percentage" % unit)
            if b is None or a is None:
                return "?"
            if rep.get("%s_window_changed" % unit):
                return "%g%% reset %g%%" % (b, a)
            d = rep.get("%s_delta" % unit)
            return "%g%% -> %g%%%s" % (b, a, "" if d is None else " (%+g)" % d)

        print("%-26s %-22s %-22s %-28s %s"
              % (run_id, pair("five_hour"), pair("seven_day"),
                 rep.get("measurement"), (rep.get("completion") or {}).get("status")))


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
