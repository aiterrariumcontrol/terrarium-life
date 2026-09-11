#!/usr/bin/env python3
"""Tests for outbound_lint. The failure that matters is a silent pass: text
that carries a mention or a self-advertisement into a stranger's tracker and
the tool says nothing. Every check therefore has a case that must fire and a
case that must stay quiet."""
import unittest
import outbound_lint as L


def names(text, **kw):
    return sorted({f[2] for f in L.lint(text, **kw)})


class TestFires(unittest.TestCase):
    def test_mention(self):
        self.assertEqual(names("@winterz thanks for the fix."), ["mention"])

    def test_self_repo_link(self):
        self.assertIn("self-link", names("See https://github.com/aiterrariumcontrol/rruleref"))

    def test_self_pages_link(self):
        self.assertIn("self-pages", names("Try https://aiterrariumcontrol.github.io/rruleref/web/"))

    def test_bare_commit_hash_in_prose(self):
        self.assertIn("commit-ref", names("Reproduced at 48d52b4b868d5adb05aa7b4ba3be95c848066552."))

    def test_issue_reference(self):
        self.assertIn("issue-ref", names("Related to #794 and libical/libical#937."))

    def test_real_case_that_prompted_the_rule(self):
        # Reconstructed from the Issue kaz8096 pointed at in REQ-0010.
        got = names(L.SELF_TEST_DIRTY)
        for want in ("mention", "self-link", "self-pages", "commit-ref", "issue-ref"):
            self.assertIn(want, got)


class TestStaysQuiet(unittest.TestCase):
    def test_clean_message(self):
        self.assertEqual(L.lint(L.SELF_TEST_CLEAN), [])

    def test_code_fence_is_not_prose(self):
        # `git checkout <sha>` inside a fence is the reproduction instruction,
        # and GitHub makes no cross-reference for it.
        text = "Reproduce:\n```\ngit checkout 48d52b4b868d5adb05aa7b4ba3be95c848066552\n```\n"
        self.assertEqual(L.lint(text), [])

    def test_email_local_part_is_not_a_mention(self):
        self.assertNotIn("mention", names("Write to someone@example.com about it."))

    def test_ordinary_words_are_not_hashes(self):
        for word in ("added", "decade", "facade", "beefed"):
            self.assertNotIn("commit-ref", names(f"The change {word} nothing."), word)

    def test_third_party_repo_link_is_not_a_self_link(self):
        self.assertEqual(L.lint("https://github.com/libical/libical/blob/master/README.md"), [])

    def test_internal_destination_is_exempt(self):
        # Inside my own repositories the Human placed no restriction at all.
        self.assertEqual(L.lint(L.SELF_TEST_DIRTY, internal=True), [])


class TestExitStatus(unittest.TestCase):
    def test_block_is_nonzero_warn_is_zero(self):
        import io
        self.assertEqual(L.report(L.lint("@winterz hello"), io.StringIO()), 1)
        self.assertEqual(L.report(L.lint("Fixed in #794."), io.StringIO()), 0)
        self.assertEqual(L.report(L.lint("Thanks, that works."), io.StringIO()), 0)


if __name__ == "__main__":
    unittest.main()
