# Current State

Updated: 2026-09-08 (twenty-seventh wake)

## The corpus now says which of its answers are contested

Finding 018's stated unfinished piece is done, `rruleref` `acc4722`.
`corroborated.json` carries `reading_dependent` on every case and
`reading_alternative` on the 54 where the two readings of RFC 5545 §3.3.10's
first period disagree. `conformance/cases.ndjson` carries the alternative
through; `conformance/score.py` reports a match against it as
`fail_other_reading`, counted apart from `fail`.

Rebuilt into a temp dir per rule 12: all other derived files byte-identical,
every corroborated case identical outside the two new fields, 54 of 677 with no
`FREQ=WEEKLY` — finding 018 reproduces from the builder.

**The safeguard fired the day it was built.** Re-scoring all four live
adapters: 3 of dmfs lib-recur's 76 non-passing cases are the other reading, not
defects. `rrule.js`, `ical4j`, `libical` master: none. Numbers in
[`conformance/RESULTS.md`](https://github.com/aiterrariumcontrol/rruleref/blob/main/conformance/RESULTS.md).

**Unexpected, and probed rather than inferred.** Of the 25 reading-dependent
cases that are also `dtstart_synchronized`, 24 (not 25 — I assumed 25) stop
being synchronized under the other reading, so §3.8.5.3 would make them
unscorable. Kept and marked, not dropped. In `corpus/SCHEMA.md`.

## REQ-0007 came back NEEDS_INFO; the evidence was wrong and is fixed

The Human declined to approve the libical report as drafted. Two supporting
examples used a `DTSTART` that is not an instance of its own recurrence set, so
RFC 5545 §3.8.5.3 leaves those recurrence sets undefined and neither example
was evidence of anything. Retracted in the open, not quietly edited.

Replaced with synchronized examples that were **run**, not predicted, and the
eight `FREQ=WEEKLY` corpus failures were audited rather than assumed: all eight
have `DTSTART` equal to their own first instance.

New: [`findings/repro/019-weekly-bymonth-bysetpos.c`](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/repro/019-weekly-bymonth-bysetpos.c),
depending only on libical, running each case through both
`icalrecur_iterator_new`/`_next` and `icalcomponent_foreach_recurrence` over a
`VEVENT`. Both paths agree; 3 of 5 differ from expected, 2 controls pass.
Pinned at rruleref `4abebd5`.

Revised proposal is
[REQ-0008](https://github.com/kaz8096/ai-terrarium-agent-control/issues/9),
same limits as REQ-0007. **Nothing authorized, nothing posted upstream.**

Standing rule 3b added: DTSTART synchronization is a checkable property, not a
known one. Rule 6 now requires a standalone reproducer before an upstream
report is proposed.

## What is worth doing next — genuinely open

Nothing is queued. A fourth lineage (Go/Rust/C#/Swift) is available but must
**not** win by default; life#6 is exactly about that. Findings 015/016 remain
unreported by choice. The only live thread is REQ-0008 awaiting a decision,
which costs nothing to check.

Quota is the binding constraint: 7d at 82% on 2026-09-08 04:15Z, resets
2026-09-09 21:00Z. Space wakes out and keep them bounded.
