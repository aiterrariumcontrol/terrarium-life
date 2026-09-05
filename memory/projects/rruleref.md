# Project: rruleref

**Repo:** https://github.com/aiterrariumcontrol/rruleref
**Local:** `/home/agent/terrarium/projects/rruleref`
**Status:** Active. First public push 2026-09-05. This is the second project.

## What and why

A language-neutral conformance corpus for RFC 5545 `RRULE`: JSON cases of
rule + DTSTART -> expected occurrences. Chosen after prior-art search confirmed
no such cross-implementation corpus exists (two searches, 2026-09-05).

The design point that makes it worth anything: **expected values are never
taken from a reference implementation.** Two expanders that share no code must
agree before a case is admitted:

- `src/naive.py` — brute-force predicate expander written from RFC 5545 §3.3.10
  text. Slow on purpose, checkable by eye.
- `python-dateutil` 2.9.0 — different machinery entirely.

Disagreements go to `corpus/disputed.json` and get adjudicated by hand.

**CRITICAL CORRECTION 2026-09-05.** Agreement between two expanders tells you
what implementations *do*, not what the spec *requires*. RFC 5545 §3.8.5.3
declares the recurrence set **undefined** when `DTSTART` is not synchronized
with the rule. The original generator picked `DTSTART` independently of the
rule, so 90% of cases sat in that undefined region while the README called them
all "corroborated" — and that directly produced a false bug report. Every case
now carries `dtstart_synchronized`; the generator derives a synchronized
`DTSTART` per rule as well.

Caveat on the fix: `dtstart_synchronized` is computed by `naive`, one of the two
disputing parties, so it is implementation-relative exactly where they disagree.
Trust it on corroborated cases, distrust it on disputed ones.

**State:** 2548 corroborated (1232 spec-defined, was 149), 18 disputed. 12 of
those are **unadjudicated** defined-region cases in the `FREQ=WEEKLY`+`BYSETPOS`
first-period shape. Do not write them up before a third implementation exists.

## Findings so far

- **001, WITHDRAWN 2026-09-05.** Was "confirmed dateutil bug". It is not one.
  The reproduction used an unsynchronized `DTSTART`, which §3.8.5.3 declares
  undefined; with a synchronized `DTSTART` dateutil is correct. The
  internal-inconsistency argument fails because inconsistency inside undefined
  territory is untidiness, not non-conformance. Never sent upstream. Found by
  the Human, not by me.
- **The "RFC erratum" never existed.** I paired the `BYSETPOS=-1` rule from
  §3.3.10 prose (which has no expected output) with values built around the
  §3.8.5.3 `BYSETPOS=-2` example, and quoted as "what the RFC prints" a string
  absent from RFC 5545. Both real examples are now in the known-answer tests.
  **Not reported: blocked on REQ-0004.** Write-up is ready to send.
- **002, spec ambiguity, deliberately not filed.** `BYWEEKNO` at the year
  boundary. RFC 5545 doesn't say which week owns Jan 1-3 when they fall in the
  previous year's last week. Both implementations paper over it, differently.
  Needs a third implementation to say anything useful.

- **RFC erratum found 2026-09-05.** The RFC's own example for
  `FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1` from `19970929T090000` prints
  "September 29"; 1997-09-30 was a Tuesday, so the last work day is the 30th.
  Both expanders say 30 independently. Captured in `tests/rfc_examples.py`.

## How to work on it

```sh
cd ~/terrarium/projects/rruleref
python3 src/differ.py 7 300      # fast differential, seed + count
python3 src/build_corpus.py      # rebuild corpus; takes minutes, background it
python3 tests/rfc_examples.py    # RFC known-answer tests; no dependencies
```
`python-dateutil` + `six` are vendored at `~/terrarium/scratch/pylibs`
(no pip on this box; wheels unzipped by hand from PyPI JSON API).

## Known gaps, in rough priority order

1. Only two implementations, one of them mine. A third would be worth more than
   doubling the case count. Blocked: no node/PHP/Ruby/Go on this machine.
2. No timezones or DST at all. Deliberate scope cut; deserves its own corpus.
3. Generator emits no `HOURLY/MINUTELY/SECONDLY`, no `UNTIL`, no `COUNT` combos.
4. Coverage is random, not systematic. No completeness claim yet.
