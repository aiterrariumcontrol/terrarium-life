#!/usr/bin/env python3
"""Check text that is about to be posted to somebody else's repository.

Why this exists
---------------
On 2026-09-11, in REQ-0010, kaz8096 granted standing use of every
`aiterrariumcontrol` repository and attached one exclusion to it:

    外部への不必要な mention/reference 等は極力控えてください
    自分の repository 同士であればいくらでも mention でも reference でも
    かまいませんが、外部へは気を付けてください

and named the concrete example: the Issue I opened at libical/libical#1374
carried an `@` mention, several commit references, and links back to my own
journal and findings. None of those were necessary for the maintainer to
reproduce the bug, and all of them cost the maintainer's repository something:
a notification, a permanent cross-reference event on a commit, or the
impression of a stranger advertising himself in their tracker.

The rule is easy to agree with and easy to forget while writing. So it is
mechanical. Run this on the exact bytes before they are posted, and on the
exact bytes of any request asking permission to post them.

Inside my own repositories none of this applies; pass `--internal` and the
tool says so and exits 0.

Usage
-----
    python3 outbound_lint.py FILE [--internal] [--quiet]
    ... | python3 outbound_lint.py -
    python3 outbound_lint.py --self-test

Exit status is 1 if anything at BLOCK severity is present, else 0. A WARN is
not permission to ignore it; it means the tool cannot tell whether this
particular reference is the point of the message, and I must say why it is.
"""
import argparse
import re
import sys

SELF_ACCOUNT = "aiterrariumcontrol"

# Fenced code blocks and indented shell transcripts are where a maintainer's
# reproduction steps live. `git checkout <sha>` inside a fenced block is the
# instruction itself, not a gratuitous reference -- and GitHub does not create
# a cross-reference event for text inside a code fence. Strip fences before
# scanning so the tool complains about prose, which is where the noise is.
FENCE = re.compile(r"^(```|~~~)")


def strip_fences(text):
    """Blank out fenced code blocks, keeping line numbers intact."""
    out, in_fence = [], False
    for line in text.split("\n"):
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return out


CHECKS = [
    # (name, severity, regex, note)
    ("mention", "BLOCK", re.compile(r"(?<![A-Za-z0-9_/`])@([A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?)\b"),
     "notifies a person. Only mention someone who asked me a question, and only "
     "in the reply to that question."),
    ("self-link", "BLOCK", re.compile(r"https?://(?:www\.)?github\.com/" + SELF_ACCOUNT + r"/\S*"),
     "links my own repository into someone else's tracker. Permitted only when "
     "it is the reproducer they need in order to act; never for a journal, a "
     "findings note, a report, or a repository's front page."),
    ("self-pages", "BLOCK", re.compile(r"https?://" + SELF_ACCOUNT + r"\.github\.io/\S*"),
     "advertises my own site in someone else's tracker."),
    ("commit-ref", "WARN", re.compile(r"(?<![A-Za-z0-9/])(?<!\.)\b[0-9a-f]{7,40}\b(?![A-Za-z0-9])"),
     "a bare commit hash in prose becomes a permanent cross-reference event on "
     "that commit. Name the release or the branch in words unless the exact "
     "commit is the subject."),
    ("issue-ref", "WARN", re.compile(r"(?<![A-Za-z0-9_])(?:[A-Za-z0-9][\w.-]*/[\w.-]+)?#\d+\b"),
     "creates a cross-reference in the referenced thread. Keep only the ones "
     "the reader has to follow."),
]

# A hash-looking token that is actually a date range, a decimal, or a word like
# "added" / "decade" would be noise. Require at least one digit and at least
# one letter for short tokens; a full 40-char hash is unambiguous.
def _plausible_hash(tok):
    if len(tok) == 40:
        return True
    return any(c.isdigit() for c in tok) and any(c.isalpha() for c in tok)


def lint(text, internal=False):
    """Return a list of (severity, line_no, name, matched_text, note)."""
    if internal:
        return []
    findings = []
    for lineno, line in enumerate(strip_fences(text), 1):
        if not line.strip():
            continue
        for name, sev, rx, note in CHECKS:
            for m in rx.finditer(line):
                tok = m.group(0)
                if name == "commit-ref" and not _plausible_hash(tok):
                    continue
                findings.append((sev, lineno, name, tok, note))
    return findings


def report(findings, stream=sys.stdout, quiet=False):
    if not findings:
        print("outbound_lint: clean -- no mentions, self-links, commit or issue "
              "references outside code fences.", file=stream)
        return 0
    order = {"BLOCK": 0, "WARN": 1}
    seen_notes = set()
    for sev, lineno, name, tok, note in sorted(findings, key=lambda f: (order[f[0]], f[1])):
        print(f"{sev:5} line {lineno:>4}  {name:<10} {tok}", file=stream)
        if not quiet and name not in seen_notes:
            print(f"                          -> {note}", file=stream)
            seen_notes.add(name)
    blocks = sum(1 for f in findings if f[0] == "BLOCK")
    warns = len(findings) - blocks
    print(f"\noutbound_lint: {blocks} BLOCK, {warns} WARN.", file=stream)
    if blocks:
        print("Do not post this text to an external repository as written.", file=stream)
    else:
        print("Nothing blocking. For each WARN, state why the reference is "
              "necessary before posting.", file=stream)
    return 1 if blocks else 0


SELF_TEST_CLEAN = """Retested the reproducer against the current release.
All five original cases now pass on both expansion paths.
The corpus went from 8 failures to 0 with no regressions. Thanks for the fix.
"""

SELF_TEST_DIRTY = """@winterz Retested at 4edd39a34a7b67ca6ab68667c84ac19ae890dd43.
Full write-up: https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/019.md
See also #1374 and the live page at https://aiterrariumcontrol.github.io/rruleref/
Reproduction, which is fine because it is fenced:
```
git checkout 48d52b4b868d5adb05aa7b4ba3be95c848066552
```
"""


def self_test():
    """The safeguard is unverified until it is seen to fire. Fire it on the
    real text that prompted the rule, and confirm it stays quiet on text that
    says the same thing without the noise."""
    ok = True

    f = lint(SELF_TEST_CLEAN)
    print("-- clean sample (what the message should have looked like)")
    report(f)
    if f:
        print("FAIL: clean sample produced findings"); ok = False

    print("\n-- dirty sample (reconstructed from libical/libical#1374)")
    f = lint(SELF_TEST_DIRTY)
    report(f)
    names = {n for _, _, n, _, _ in f}
    for want in ("mention", "self-link", "self-pages", "commit-ref", "issue-ref"):
        if want not in names:
            print(f"FAIL: did not detect {want}"); ok = False
    if any(tok.startswith("48d52b4b") for _, _, _, tok, _ in f):
        print("FAIL: flagged a hash inside a code fence"); ok = False

    print("\n-- internal mode (my own repositories)")
    if lint(SELF_TEST_DIRTY, internal=True):
        print("FAIL: internal mode produced findings"); ok = False
    else:
        print("clean, as intended: inside aiterrariumcontrol none of this applies.")

    print("\nself-test: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("file", nargs="?", help="file to check, or - for stdin")
    p.add_argument("--internal", action="store_true",
                   help="destination is one of my own repositories")
    p.add_argument("--quiet", action="store_true", help="omit the explanations")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.file:
        p.error("a file is required (or - for stdin, or --self-test)")
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    return report(lint(text, internal=a.internal), quiet=a.quiet)


if __name__ == "__main__":
    sys.exit(main())
