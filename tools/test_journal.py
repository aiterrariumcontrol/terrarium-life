#!/usr/bin/env python3
"""Tests for append-only journal publication (terrarium-life#4, #5).

The point under test is that insertion position is mechanical: a wake hands the
helper new prose and the helper puts it at the tail, every time, in both
languages, without the caller saying where.

Run: python3 tools/test_journal.py
"""
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import journal  # noqa: E402


class AppendOnly(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._saved = (journal.ROOT, journal.JOURNAL)
        journal.ROOT = self.tmp
        journal.JOURNAL = os.path.join(self.tmp, "reports", "journal")
        os.makedirs(journal.JOURNAL)

    def tearDown(self):
        journal.ROOT, journal.JOURNAL = self._saved
        shutil.rmtree(self.tmp)

    def read(self, d, lang):
        return open(journal.entry_path(d, lang), encoding="utf-8").read()

    def test_two_sequential_appends_stay_chronological(self):
        d = "2026-09-06"
        for lang in ("en", "ja"):
            journal.append_entry(d, lang, "FIRST wake prose.")
            journal.append_entry(d, lang, "SECOND wake prose.")
            text = self.read(d, lang)
            self.assertIn("FIRST wake prose.", text)
            self.assertIn("SECOND wake prose.", text)
            self.assertLess(text.index("FIRST"), text.index("SECOND"),
                            f"{lang}: second entry landed before the first")

    def test_third_append_goes_after_both(self):
        d = "2026-09-06"
        for n in ("ONE", "TWO", "THREE"):
            journal.append_entry(d, "en", f"{n} body")
        text = self.read(d, "en")
        self.assertLess(text.index("ONE"), text.index("TWO"))
        self.assertLess(text.index("TWO"), text.index("THREE"))

    def test_header_and_nav_survive_appending(self):
        d = "2026-09-06"
        journal.append_entry(d, "en", "FIRST")
        journal.append_entry(d, "en", "SECOND")
        journal.cmd_index()
        text = self.read(d, "en")
        self.assertTrue(text.startswith(f"# {d} — English"))
        self.assertEqual(text.count(journal.NAV_OPEN), 2)
        # nav header above the prose, nav footer below it
        self.assertLess(text.index(journal.NAV_CLOSE), text.index("FIRST"))
        self.assertGreater(text.rindex(journal.NAV_OPEN), text.index("SECOND"))
        self.assertLess(text.index("FIRST"), text.index("SECOND"))

    def test_first_append_creates_the_file(self):
        d = "2026-09-07"
        self.assertFalse(os.path.exists(journal.entry_path(d, "ja")))
        path, created = journal.append_entry(d, "ja", "最初の記録。")
        self.assertTrue(created)
        self.assertTrue(os.path.exists(path))
        _, created2 = journal.append_entry(d, "ja", "二度目の記録。")
        self.assertFalse(created2)

    def test_append_survives_a_reindex_between_wakes(self):
        """The realistic sequence: wake 1 appends, indexes, exits; wake 2 appends."""
        d = "2026-09-06"
        journal.append_entry(d, "en", "FIRST")
        journal.cmd_index()
        journal.append_entry(d, "en", "SECOND")
        journal.cmd_index()
        text = self.read(d, "en")
        self.assertLess(text.index("FIRST"), text.index("SECOND"))
        self.assertEqual(text.count(journal.NAV_OPEN), 2)

    def test_staged_text_with_its_own_title_and_nav_is_not_duplicated(self):
        d = "2026-09-06"
        journal.append_entry(d, "en", "FIRST")
        staged = f"# {d} — English\n\n{journal.NAV_OPEN}\nstale nav\n{journal.NAV_CLOSE}\n\nSECOND\n"
        journal.append_entry(d, "en", staged)
        text = self.read(d, "en")
        self.assertNotIn("stale nav", text)
        self.assertEqual(text.count(f"# {d} — English"), 1)
        self.assertLess(text.index("FIRST"), text.index("SECOND"))

    def test_empty_append_is_refused(self):
        with self.assertRaises(ValueError):
            journal.append_entry("2026-09-06", "en", "   \n\n")

    def test_entries_are_separated_by_a_blank_line(self):
        d = "2026-09-06"
        journal.append_entry(d, "en", "FIRST")
        journal.append_entry(d, "en", "SECOND")
        text = self.read(d, "en")
        self.assertIn("FIRST\n\nSECOND", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
