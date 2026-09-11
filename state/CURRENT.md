# Current State

Updated: 2026-09-11 (fortieth wake)

## The standing grant, and the limit that came with it

[REQ-0010](https://github.com/kaz8096/ai-terrarium-agent-control/issues/11) is
decided. Two things in one comment from `kaz8096`:

1. `DECISION: HUMAN_ACTION` — they enabled Pages on `rruleref` (source `main:/`).
   The record gap is closed.
2. Additional authority: **every repository under `aiterrariumcontrol` is mine
   to use**, explicitly not one-off for `rruleref`. Written as §5 additional
   authority beside a HUMAN_ACTION decision rather than with §9's
   `TYPE: STANDING PERMISSION` marker; §5 governs exactly that case, so I treat
   it as authoritative.

**The limit is the important half.** Internal mentions and cross-references are
unrestricted; references pointing *outward*, into other people's repositories,
must be kept to the necessary minimum. Everything landing in someone else's
repository still needs its own approval under §3. The named example is the
Issue I opened at libical, which carries a mention, commit references, and
links back to my own journal and findings — a stranger advertising himself in a
bug tracker.

Scope and exclusion: [`state/permissions.md`](permissions.md).

Made mechanical rather than remembered: `tools/outbound_lint.py`, run on the
exact bytes before anything external. BLOCK on mentions, self-repo links,
self-Pages links; WARN on bare commit hashes and issue references. Code fences
exempt; `--internal` exempts my own destinations entirely. **Seen to fire on
the real artifact** — 2 BLOCK and 5 WARN on the existing libical Issue body,
including the front-page self-link objected to. 13 tests, both directions.

Not retroactive: the old Issue stays as it is. Its cross-references are already
permanent and its notifications already delivered, so editing buys the
maintainers nothing.

## The debugger answers a fourth question

`web/src/compare.js`, commit `6f51b41`, live and served byte-identical.

**The evidence was a named person's bug report, not my idea list.**
`abhay-codes07` filed against Superset in July: editing an automation with a
multi-time RRULE silently drops runs. The picker reads `BYHOUR=9,17` with
`Number.parseInt`, gets `9`, and re-serialises on any edit — a twice-daily job
becomes once-daily, permanently, with nothing on screen. Both rules look like
reasonable `RRULE`s.

**Compare with** takes a second rule and the same `DTSTART` and answers in
dates: *the second rule drops 12 dates and adds none*, with the dates listed.

The whole difficulty is one line. Both expansions stop at the occurrence count
asked for, so comparing past the earlier of the two last occurrences reports a
rule that merely fires *more often* as one that *gains* dates it does not gain.
The comparison is restricted to the window both lists cover, and the page says
which window. Same old mistake in a new place: **a cap I chose is not a
property of what I am measuring.**

`tests/test_compare.py` generates the edits users actually make — drop a `BY`
part, or keep only the first value of a multi-valued one, which is precisely
the Superset bug — 4717 pairs over the corpus, each required to satisfy
partition and cap-independence. **Seen to fail:** replacing the window with
`Infinity` breaks 4579 of the 4717.

`tools/run_tests.py`: 22 files, 0 failed. Read in a browser in all three
states.

## Where the debugger stands

Version one answers four questions: what dates, what the rule means, why one
date, what an edit changed. The last three each came from a named person's
question. There is no fifth with evidence behind it, and adding one because I
can is what rule 0 exists to stop.

## Nothing is pending with the Human

No open request. The monthly evaluation request is due early October 2026 and
is an obligation, not a plan.
