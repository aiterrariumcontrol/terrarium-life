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


def run_completion(run_id, events, stream_path):
    """How this run ended, so a delta is never presented as if the run finished.

    Requested in terrarium-life#3: "having more than one event does not justify
    `measurement: complete`". Completion is a property of the *run*, read from
    the launcher's own `run.json`, and is reported separately from the quality
    of the before/after span.
    """
    out = {
        "exit_status": None,
        "terminal_reason": None,
        "quota_rejected": any(e.get("status") == "rejected" for e in events),
        "five_hour_exhausted": any(
            isinstance(e.get("five_hour_used_percentage"), (int, float))
            and e["five_hour_used_percentage"] >= 100
            for e in events
        ),
        "status": "unknown",
    }
    try:
        rec = json.loads((pathlib.Path(stream_path).parent / "run.json").read_text())
    except (OSError, ValueError):
        # No run.json: either the run is still going or it died before writing one.
        out["status"] = "in_progress_or_no_record"
        return out
    out["exit_status"] = rec.get("exit_status")
    out["terminal_reason"] = (rec.get("claude_run") or {}).get("terminal_reason")
    if out["quota_rejected"] or out["five_hour_exhausted"]:
        out["status"] = "quota_exhausted"
    elif out["exit_status"] == 0:
        out["status"] = "ok"
    elif out["exit_status"] is None:
        out["status"] = "unknown"
    else:
        out["status"] = "failed_or_interrupted"
    return out


def _provenance(reading, run_id, not_before, not_after):
    """Attach where a reading came from, so a carried-forward value stays traceable."""
    if reading is None:
        return None
    out = dict(reading)
    out.setdefault("from_run", run_id)
    out.setdefault("observed_not_before", not_before)
    out.setdefault("observed_not_after", not_after)
    return out


def run_report(run_id, stream_path=None, prior=None):
    """Full before/after quota picture for one run.

    `prior` is the last reading from the preceding run, carrying its own run id
    and observation bounds. It is used as a baseline only when it belongs to the
    *same* five-hour window as this run's first own reading. Even then it is not
    a measurement taken immediately before this run: it is the last observation
    of an *earlier* run, and anything consumed between the two runs is inside the
    difference. The report says so rather than calling it exact.
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
        "after_kind": "unavailable",
        "five_hour_window_changed": None,
        "seven_day_window_changed": None,
        "five_hour_delta": None,
        "seven_day_delta": None,
        "five_hour_delta_kind": "unavailable",
        "seven_day_delta_kind": "unavailable",
        "measurement": "no_rate_limit_events",
        "completion": run_completion(run_id, events, stream_path),
    }
    if not events:
        return rep

    first, last = events[0], events[-1]
    rep["after"] = _provenance(last, run_id, not_before, not_after)
    # There is no post-exit observation available: the stream stops when the CLI
    # does. Name the value for what it is.
    rep["after_kind"] = "last_observation_during_run"
    win = first.get("five_hour_resets_at")

    if prior and prior.get("five_hour_resets_at") == win and win is not None:
        rep["before"] = dict(prior)
        rep["before_kind"] = "carried_forward_prior_run_same_window"
    else:
        rep["before"] = _provenance(first, run_id, not_before, not_after)
        rep["before_kind"] = (
            "first_observed_during_run" if len(events) > 1 else "single_reading"
        )

    def span(unit):
        key = f"{unit}_resets_at"
        pct = f"{unit}_used_percentage"
        changed = last.get(key) != rep["before"].get(key)
        if changed:
            return True, None, "window_reset_within_span"
        a, b = rep["before"].get(pct), last.get(pct)
        if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
            return False, None, "unavailable"
        kind = (
            "lower_bound_baseline_within_run"
            if rep["before_kind"] != "carried_forward_prior_run_same_window"
            else "spans_gap_since_prior_run"
        )
        return False, round(b - a, 2), kind

    for unit, short in (("five_hour", "five_hour"), ("seven_day", "seven_day")):
        changed, delta, kind = span(unit)
        rep[f"{short}_window_changed"] = changed
        rep[f"{short}_delta"] = delta
        rep[f"{short}_delta_kind"] = kind

    # Span quality and run completion are different things and are kept apart.
    if rep["before_kind"] == "carried_forward_prior_run_same_window":
        rep["measurement"] = "spans_gap_since_prior_run"
    elif len(events) > 1:
        rep["measurement"] = "lower_bound_baseline_within_run"
    else:
        rep["measurement"] = "single_reading_only"
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
            # Carries from_run + observation bounds with it.
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
