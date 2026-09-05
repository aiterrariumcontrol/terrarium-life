#!/usr/bin/env python3
"""Subscription-quota readings, with the provenance needed to trust them.

The only trustworthy source of subscription rate-limit percentages is the
`rate_limit_event` records inside a wake's own `claude-stream.jsonl`. The
interactive status line does not run during headless `claude -p` wakes, so
`state/claude-usage.json` cannot refresh itself.

Two properties this module exists to preserve, both requested in
aiterrariumcontrol/terrarium-life#3:

1. **A reading's observation time is not the time something read it.** The
   events carry no timestamp of their own, so an exact observation time is not
   recoverable. What *is* recoverable is a bound: an event was written after
   its run started and no later than the last write to its stream file. That
   bound is stable, so re-reading an old event can never make it look fresh.

2. **A "before" value belongs to a specific five-hour window.** Windows are
   identified by their `resetsAt` epoch. Two readings from different windows
   cannot be subtracted, and this module never does.
"""

import json
import os
import pathlib
from datetime import datetime, timezone

RAW = pathlib.Path.home() / "terrarium" / "logs" / "raw"


def _iso(epoch):
    if not isinstance(epoch, (int, float)):
        return None
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pct(window):
    u = (window or {}).get("utilization")
    return round(u * 100, 2) if isinstance(u, (int, float)) else None


def _reading(info, ordinal):
    uw = info.get("unifiedWindows") or {}
    five = uw.get("five_hour") or {}
    seven = uw.get("seven_day") or {}
    return {
        "five_hour_used_percentage": _pct(five),
        "five_hour_resets_at": five.get("resetsAt"),
        "seven_day_used_percentage": _pct(seven),
        "seven_day_resets_at": seven.get("resetsAt"),
        "status": info.get("status"),
        "event_ordinal": ordinal,
    }


def read_events(stream_path):
    """Every rate_limit_event in one stream log, in order. May be empty."""
    out = []
    try:
        fh = open(stream_path, "r", encoding="utf-8", errors="replace")
    except OSError:
        return out
    with fh:
        for line in fh:
            if '"rate_limit_event"' not in line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue  # a truncated final line in a live log is normal
            info = rec.get("rate_limit_info")
            if isinstance(info, dict):
                out.append(_reading(info, len(out)))
    return out


def observation_bounds(stream_path):
    """(not_before, not_after) ISO stamps bounding when events in this log were seen.

    `not_before` is the run's own start, recoverable from the run id.
    `not_after` is the last write to the stream file. Both are properties of the
    recorded run, never of the current clock, so they do not drift on re-read.
    """
    run_id = pathlib.Path(stream_path).parent.name
    not_before = None
    stamp = run_id.split("-", 1)[0]
    try:
        not_before = (
            datetime.strptime(stamp, "%Y%m%dT%H%M%SZ")
            .replace(tzinfo=timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%SZ")
        )
    except ValueError:
        pass
    try:
        not_after = datetime.fromtimestamp(
            os.path.getmtime(stream_path), timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
    except OSError:
        not_after = None
    return not_before, not_after


def run_report(run_id, stream_path=None, prior=None):
    """Full before/after quota picture for one run.

    `prior` is the last reading from the preceding run, if any. It is used as a
    genuine baseline only when it belongs to the *same* five-hour window as this
    run's first own reading; otherwise this run's first own reading is reported
    as `first_observed`, which is a value already reflecting some consumption.
    """
    stream_path = stream_path or (RAW / run_id / "claude-stream.jsonl")
    events = read_events(stream_path)
    not_before, not_after = observation_bounds(stream_path)

    rep = {
        "run_id": run_id,
        "event_count": len(events),
        "observed_not_before": not_before,
        "observed_not_after": not_after,
        "before": None,
        "before_kind": "unavailable",
        "after": None,
        "five_hour_window_changed": None,
        "five_hour_delta": None,
        "seven_day_delta": None,
        "measurement": "no_rate_limit_events",
    }
    if not events:
        return rep

    first, last = events[0], events[-1]
    rep["after"] = last
    win = first.get("five_hour_resets_at")

    if prior and prior.get("five_hour_resets_at") == win and win is not None:
        rep["before"] = prior
        rep["before_kind"] = "baseline_prior_run_same_window"
    else:
        rep["before"] = first
        rep["before_kind"] = (
            "first_observed_during_run" if len(events) > 1 else "single_reading"
        )

    rep["five_hour_window_changed"] = (
        last.get("five_hour_resets_at") != rep["before"].get("five_hour_resets_at")
    )

    if not rep["five_hour_window_changed"]:
        a, b = rep["before"].get("five_hour_used_percentage"), last.get(
            "five_hour_used_percentage"
        )
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            rep["five_hour_delta"] = round(b - a, 2)

    if rep["before"].get("seven_day_resets_at") == last.get("seven_day_resets_at"):
        a, b = rep["before"].get("seven_day_used_percentage"), last.get(
            "seven_day_used_percentage"
        )
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            rep["seven_day_delta"] = round(b - a, 2)

    rep["measurement"] = "complete" if len(events) > 1 else "single_reading_only"
    return rep


def all_run_reports():
    """run_id -> report, oldest run first, chaining each run's baseline."""
    streams = sorted(RAW.glob("*/claude-stream.jsonl"))
    reports = {}
    prior = None
    for stream in streams:
        run_id = stream.parent.name
        rep = run_report(run_id, stream, prior)
        reports[run_id] = rep
        if rep["after"]:
            prior = rep["after"]
    return reports


def latest_reading():
    """(run_id, reading, not_before, not_after) for the newest event anywhere."""
    for stream in sorted(RAW.glob("*/claude-stream.jsonl"), reverse=True):
        events = read_events(stream)
        if events:
            nb, na = observation_bounds(stream)
            return stream.parent.name, events[-1], nb, na
    return None, None, None, None


def window_state(reading, now=None):
    """Is this reading still about the currently running five-hour window?"""
    now = now or datetime.now(timezone.utc).timestamp()
    resets = (reading or {}).get("five_hour_resets_at")
    if not isinstance(resets, (int, float)):
        return "unknown_window"
    return "current_window" if now < resets else "expired_window"
