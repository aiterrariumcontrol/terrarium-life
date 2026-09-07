#!/usr/bin/env python3
"""Tests for req_status parsing. The tool decides what I believe I am
authorized to do, so the cases that matter most are the ones where it must
refuse to see an approval that is not there."""
import unittest
from datetime import datetime, timezone
import req_status as R


class TestParseDecision(unittest.TestCase):
    def test_template_form(self):
        d, rid, exp = R.parse_decision(
            "DECISION: APPROVED\nRequest-ID: REQ-0005\n\nExpires: 7 days from this approval.")
        self.assertEqual((d, rid), ("APPROVED", "REQ-0005"))
        self.assertIn("7 days", exp)

    def test_bold_markdown_form(self):
        d, rid, _ = R.parse_decision("**DECISION:** DENIED\n**Request-ID:** REQ-0009")
        self.assertEqual((d, rid), ("DENIED", "REQ-0009"))

    def test_prose_approval_is_not_a_decision(self):
        # §6: informal implication is not approval.
        for body in ("Sure, that's approved by me, go ahead.",
                     "I approve of this direction generally.",
                     "APPROVED" ,  # bare word, no DECISION: key
                     ""):
            self.assertEqual(R.parse_decision(body)[0], None, body)

    def test_unknown_decision_word_rejected(self):
        self.assertEqual(R.parse_decision("DECISION: MAYBE\nRequest-ID: REQ-0001")[0], None)

    def test_complete_recognised(self):
        self.assertEqual(R.parse_decision("DECISION: COMPLETE\nRequest-ID: REQ-0004")[0],
                         "COMPLETE")


class TestExpiry(unittest.TestCase):
    at = datetime(2026, 9, 6, 17, 27, tzinfo=timezone.utc)

    def test_relative_days(self):
        dt, _ = R.expiry_date("7 days from this approval.", self.at)
        self.assertEqual(dt.date().isoformat(), "2026-09-13")

    def test_absolute_date(self):
        dt, _ = R.expiry_date("2026-10-01", self.at)
        self.assertEqual(dt.date().isoformat(), "2026-10-01")

    def test_missing_expiry_is_not_standing(self):
        dt, note = R.expiry_date(None, self.at)
        self.assertIsNone(dt)
        self.assertIn("not standing permission", note)

    def test_unparseable_expiry_yields_no_date(self):
        # Must not silently become "no expiry"; the text is preserved for a human.
        dt, note = R.expiry_date("when the corpus is finished", self.at)
        self.assertIsNone(dt)
        self.assertIn("corpus", note)


if __name__ == "__main__":
    unittest.main()
