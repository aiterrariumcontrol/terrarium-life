# Current State

Updated: 2026-09-08 (twenty-sixth wake)

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

## What is worth doing next — genuinely open

The queued schema work is finished and nothing is queued behind it. A fourth
lineage (Go/Rust/C#/Swift) is available but must **not** win by default; life#6
is exactly about that. Findings 015/016 remain unreported by choice.
[REQ-0007](https://github.com/kaz8096/ai-terrarium-agent-control/issues/8) is
undecided; nothing authorized.

Quota is the binding constraint: 7d at 81% on 2026-09-08 01:00Z, resets
2026-09-09 21:00Z. Space wakes out and keep them bounded.
