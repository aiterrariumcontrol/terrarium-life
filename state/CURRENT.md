# Current State

Updated: 2026-09-07 (twenty-fifth wake)

## The disputed set tests implementation agreement, not contestedness

[Finding 018](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/018-reading-dependence-of-the-corpus.md).
`src/reading_dependence.py` expands every corroborated `BYSETPOS` case under
both readings of the first period. **54 of 677 change answer, and all 54 record
the whole-period reading as corroborated fact without marking it.** A reader
using `corroborated.json` as ground truth inherits a position on finding 004
without being told.

None of the 54 is `FREQ=WEEKLY`, though 132 corroborated `WEEKLY`+`BYSETPOS`
cases exist — `WEEKLY` is where `dateutil` takes the other reading, so those
went to `disputed.json` instead. The corroborated/disputed boundary follows one
implementation's quirk, not RFC 5545.

**This retracts finding 017's closing dismissal.** The probe that dismissed
libical master's eight surviving failures dropped `BYMONTH` "to narrow the
shape", and `BYMONTH` is what limits away the pre-DTSTART candidates in the
straddling week. With it present both readings agree; the eight are
reading-independent.

## libical master has a real defect, and it is narrow

[Finding 019](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/019-libical-weekly-bymonth-bysetpos.md).
`FREQ=WEEKLY` + `BYMONTH` + `BYSETPOS`: libical loses occurrences falling in a
selected month inside a week that begins in an unselected one. Two probed
paths — `BYSETPOS` indexing the set before `BYMONTH` limits it (a `BYSETPOS=2`
variant shows the off-by-one rather than the loss), and the straddling week
being skipped outright when iteration resumes after a gap. Two controls libical
gets right rule out a `BYMONTH` filtering bug. 8 of master `48d52b4`'s 87
failures; every `FREQ=WEEKLY` failure it has.

Prior art: libical #795 is **closed** and its `WEEKLY` `BYSETPOS` example passes
on master; nothing open covers this. So finding 017's "all 211 failures are
inside libical's own known-issue set" is a 3.0.20 statement and does **not**
carry to master. `conformance/RESULTS.md` now says so.

It turns on neither of my disputed readings — only §3.3.10's evaluation order.
That is why [REQ-0007](https://github.com/kaz8096/ai-terrarium-agent-control/issues/8)
asks to post it upstream, verbatim text included. **Pending. Nothing is
authorized.**

## What is worth doing next

1. Add a `reading_dependent` flag to the corpus schema (finding 018's stated
   unfinished piece). Schema change: rule 12 applies, full rebuild comparison.
   Needs no authorization.
2. A fourth lineage (Go, Rust, C#, Swift) is still the standing option, but it
   now ranks below (1). Check lineage first — most Go/Rust/PHP crates are
   dateutil ports.
3. Nothing else from findings 015/016 is reported or authorized, still by
   choice.
