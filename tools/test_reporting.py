#!/usr/bin/env python3
"""Regression tests for the defects reported in terrarium-life#3.

Each test names the problem it pins. They use real files in a temporary
directory and the real clock, so nothing here passes by mocking away the thing
under test.

Run: python3 tools/test_reporting.py
"""

import datetime as dt
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import collect_usage
import quota
import wake_index


def iso(delta_minutes):
    t = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=delta_minutes)
    return t.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def epoch(delta_minutes):
    return (dt.datetime.now(dt.timezone.utc)
            + dt.timedelta(minutes=delta_minutes)).timestamp()


class TempUsageFile:
    """Point collect_usage.OUT at a temp file holding `doc`."""

    def __init__(self, doc):
        self.doc = doc

    def __enter__(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "claude-usage.json")
        with open(self.path, "w") as fh:
            json.dump(self.doc, fh)
        self.saved, collect_usage.OUT = collect_usage.OUT, self.path
        return self

    def __exit__(self, *exc):
        collect_usage.OUT = self.saved
        self.dir.cleanup()


def run_check():
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = collect_usage.check()
    return rc, buf.getvalue()


class Freshness(unittest.TestCase):
    """Problem 3: age from `observed_not_after` is the MINIMUM age."""

    def test_wide_bounds_are_not_fresh(self):
        # The reported case: observed somewhere in a ~2h window ending 1 min ago.
        # Optimistically that is 1 minute old; it could be 119 minutes old.
        doc = {
            "five_hour_used_percentage": 10,
            "five_hour_resets_at": epoch(+180),
            "observed_not_before": iso(-119),
            "observed_not_after": iso(-1),
            "window_state": "current_window",
        }
        with TempUsageFile(doc):
            rc, out = run_check()
        self.assertEqual(rc, 1, "a possibly-2h-old reading must not pass as fresh")
        self.assertIn("STALE", out)
        self.assertIn("between 1 and 119 min old", out)

    def test_narrow_recent_bounds_are_fresh(self):
        doc = {
            "five_hour_used_percentage": 10,
            "five_hour_resets_at": epoch(+180),
            "observed_not_before": iso(-4),
            "observed_not_after": iso(-2),
            "window_state": "current_window",
        }
        with TempUsageFile(doc):
            rc, out = run_check()
        self.assertEqual(rc, 0, out)
        self.assertIn("FRESH", out)

    def test_missing_lower_bound_is_uncertain_not_fresh(self):
        doc = {
            "five_hour_used_percentage": 10,
            "five_hour_resets_at": epoch(+180),
            "observed_not_after": iso(-2),
            "window_state": "current_window",
        }
        with TempUsageFile(doc):
            rc, out = run_check()
        self.assertEqual(rc, 1)
        self.assertIn("UNCERTAIN", out)


class WindowExpiry(unittest.TestCase):
    """Problem 3, second case: `--check` trusted the cached `window_state`."""

    def test_expired_window_despite_fresh_cache_label(self):
        doc = {
            "five_hour_used_percentage": 90,
            "five_hour_resets_at": epoch(-5),   # reset five minutes ago
            "observed_not_before": iso(-10),
            "observed_not_after": iso(-9),
            "window_state": "current_window",   # stale label, must be ignored
        }
        with TempUsageFile(doc):
            rc, out = run_check()
        self.assertEqual(rc, 1, "a reading from an ended window must fail --check")
        self.assertIn("window that has ended", out)
        self.assertIn("window=expired_window", out)


class IndexIdempotence(unittest.TestCase):
    """Problem 2: the `last regenerated` line alone caused commit-and-push."""

    def test_same_data_different_clock_is_unchanged(self):
        current = wake_index.render()
        # Simulate the file having been generated at some other time.
        previous = "\n".join(
            "from the records in [`runs/`](../runs/); last regenerated "
            "1999-12-31T23:59:59Z." if wake_index.STAMP_MARKER in line else line
            for line in current.splitlines()
        )
        text, changed = wake_index.render_stable(previous)
        self.assertFalse(changed, "timestamp-only difference must not count")
        self.assertEqual(text, previous, "unchanged means byte-identical output")

    def test_real_content_change_is_detected(self):
        current = wake_index.render()
        previous = current.replace("| Run |", "| Runx |", 1)
        _, changed = wake_index.render_stable(previous)
        self.assertTrue(changed)


class RunCompletion(unittest.TestCase):
    """Problem 4: >1 event did not justify `measurement: complete`."""

    def make_run(self, tmp, events, run_json=None):
        d = pathlib.Path(tmp) / "20260101T000000Z-1"
        d.mkdir()
        with open(d / "claude-stream.jsonl", "w") as fh:
            for ev in events:
                fh.write(json.dumps({
                    "type": "rate_limit_event",
                    "rate_limit_info": ev,
                }) + "\n")
        if run_json is not None:
            (d / "run.json").write_text(json.dumps(run_json))
        return d / "claude-stream.jsonl"

    @staticmethod
    def ev(five, seven=5, status="allowed", resets=None):
        return {
            "status": status,
            "unifiedWindows": {
                "five_hour": {"utilization": five / 100,
                              "resetsAt": resets or epoch(+60)},
                "seven_day": {"utilization": seven / 100, "resetsAt": epoch(+6000)},
            },
        }

    def test_quota_exhaustion_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.make_run(tmp, [self.ev(90), self.ev(100, status="rejected")],
                              {"exit_status": 1})
            rep = quota.run_report("20260101T000000Z-1", p)
        self.assertEqual(rep["completion"]["status"], "quota_exhausted")
        self.assertTrue(rep["completion"]["quota_rejected"])
        self.assertTrue(rep["completion"]["five_hour_exhausted"])
        self.assertNotEqual(rep["measurement"], "complete")

    def test_nonzero_exit_is_not_a_complete_measurement(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.make_run(tmp, [self.ev(10), self.ev(20)], {"exit_status": 143})
            rep = quota.run_report("20260101T000000Z-1", p)
        self.assertEqual(rep["completion"]["status"], "failed_or_interrupted")
        self.assertEqual(rep["completion"]["exit_status"], 143)

    def test_missing_run_record_is_not_silently_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.make_run(tmp, [self.ev(10), self.ev(20)])
            rep = quota.run_report("20260101T000000Z-1", p)
        self.assertEqual(rep["completion"]["status"], "in_progress_or_no_record")

    def test_after_is_labelled_as_in_run_observation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.make_run(tmp, [self.ev(10), self.ev(20)], {"exit_status": 0})
            rep = quota.run_report("20260101T000000Z-1", p)
        self.assertEqual(rep["after_kind"], "last_observation_during_run")


class CarriedForwardProvenance(unittest.TestCase):
    """Problem 4: a carried-forward baseline must stay traceable to its run."""

    def test_baseline_keeps_its_origin_run_and_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = pathlib.Path(tmp) / "20260101T000000Z-1"
            d.mkdir()
            resets = epoch(+60)
            (d / "claude-stream.jsonl").write_text(json.dumps({
                "type": "rate_limit_event",
                "rate_limit_info": RunCompletion.ev(30, resets=resets),
            }) + "\n")
            prior = {
                "five_hour_used_percentage": 12,
                "five_hour_resets_at": resets,
                "seven_day_used_percentage": 4,
                "seven_day_resets_at": epoch(+6000),
                "from_run": "20251231T235000Z-9",
                "observed_not_before": iso(-90),
                "observed_not_after": iso(-85),
            }
            rep = quota.run_report("20260101T000000Z-1",
                                   d / "claude-stream.jsonl", prior)
        self.assertEqual(rep["before_kind"], "carried_forward_prior_run_same_window")
        self.assertEqual(rep["before"]["from_run"], "20251231T235000Z-9")
        self.assertEqual(rep["before"]["observed_not_after"], prior["observed_not_after"])
        self.assertEqual(rep["five_hour_delta_kind"], "spans_gap_since_prior_run")

    def test_weekly_reset_blocks_subtraction_too(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = pathlib.Path(tmp) / "20260101T000000Z-1"
            d.mkdir()
            a = RunCompletion.ev(30, seven=90)
            b = RunCompletion.ev(40, seven=2)
            b["unifiedWindows"]["seven_day"]["resetsAt"] = epoch(+99999)
            b["unifiedWindows"]["five_hour"]["resetsAt"] = \
                a["unifiedWindows"]["five_hour"]["resetsAt"]
            with open(d / "claude-stream.jsonl", "w") as fh:
                for ev in (a, b):
                    fh.write(json.dumps({"type": "rate_limit_event",
                                         "rate_limit_info": ev}) + "\n")
            rep = quota.run_report("20260101T000000Z-1", d / "claude-stream.jsonl")
        self.assertTrue(rep["seven_day_window_changed"])
        self.assertIsNone(rep["seven_day_delta"])
        self.assertFalse(rep["five_hour_window_changed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
