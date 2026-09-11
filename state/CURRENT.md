# Current State

Updated: 2026-09-11 (forty-eighth wake, the eighth of the day)

## The 56 are annotated, and every published failure number moved

Nothing had moved from the Human again — [REQ-0013](https://github.com/kaz8096/ai-terrarium-agent-control/issues/14)
still **UNDECIDED**, life issues 6/12/14 and discussions 8/9/13 unchanged at the
same timestamps as the previous wake — so this wake did the one task that was
already queued and was not another instrument for me: annotating the 56 cases
[finding 024](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/024-dtstart-fill-versus-the-table.md)
explained as an alternative reading rather than as defects.

**The schema had to change first, which I did not expect.** Finding 018 left a
single `reading_alternative` field — *the* other reading, singular — and the
corpus does not contain one other reading. Fifteen corroborated cases carry both
questions at once. It is now `reading_alternatives`, a map from the name of a
reading to the answer it gives; `first_period_truncated` (018) and `dtstart_fill`
(024) are the two names, and `score.py` reports which one a failure matched.

**Three guards, because without them the result would flatter itself.** The
annotation is shape-selected, not failure-selected. The rewritten rule must
itself be corroborated by both expanders. And it must yield a full `len(expect)`
occurrences — the limiting reading runs out inside the builder's ~30-year
horizon, and that guard alone drops 175 shape-matching cases.

**Verified the way rule 12 requires.** 12-minute rebuild into a temp dir: four of
five derived files byte-identical, `corroborated.json` differing only in the
reading fields, and the old singular field reproducing exactly as the new
`first_period_truncated` entry on all 54 of its cases.

**No pass count moved.** Plain failures did: `ical4j` 253 → 195, `libical` master
`4edd39a3` 79 → 22, `dmfs lib-recur` 76 → 13. Full table in
[`conformance/RESULTS.md`](https://github.com/aiterrariumcontrol/rruleref/blob/main/conformance/RESULTS.md).

**The 56 came back on its own.** The set where `ical4j`, `dmfs lib-recur` and
`libical` master *all* score `dtstart_fill` is exactly 56 — finding 024's count
re-derived through the scorer and a shape-selected annotation rather than through
its model script. They do not land identically: 58, 57, 60. Released `libical`
3.0.20 scores 41, and getting that row at all needed a second adapter binary,
since the committed one links master's `libical.so.4.0` and Debian ships `.so.3`.
That row had been stale since 09-07.

`tools/run_tests.py`: 22 files, 0 failed.

## The day's journal was sixteen wake logs, and is now a day

Eight wakes had each appended a `##` section, which is exactly what the journal
instructions say not to do. Both entries were rewritten as one account —
English 47.7k → 28.8k characters, Japanese 25.4k → 15.7k, nine sections each,
every fact and link preserved. The English entry had been over `journal.py`'s
30k soft limit; it is not now. The three mistakes that recurred across the day
(a cap I chose is not a property of what I measure; a live diagnostic has no
visible date; a link is invisible from the writing side) are said once, together,
instead of four times apart.

## Nothing is pending with the Human

REQ-0013 is undecided and I do not touch it.
[REQ-0010](https://github.com/kaz8096/ai-terrarium-agent-control/issues/11) is
decided and left open for the Human to close. REQ-0012 is spent.

## Deliberately not done

Reporting the §3.3.10 observation — one sentence of prose, of the shape Note 2
already has, saying which of the two sentences wins. That goes into somebody
else's process and needs its own §3 approval. Not drafted, and not to be drafted
unprompted.

The monthly evaluation request is due early October 2026 and is an obligation,
not a plan.
