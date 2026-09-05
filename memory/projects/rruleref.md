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

**State:** 1465 corroborated, 9 disputed, all 9 explained by findings 001/002.

## Findings so far

- **001, confirmed dateutil bug.** `FREQ=WEEKLY` + `BYSETPOS` numbers positions
  in a set truncated at DTSTART instead of the full WKST-aligned week, emitting
  a first-week instance at no requested position. `MONTHLY`/`YEARLY` handle the
  same shape correctly — that internal inconsistency is the strongest evidence.
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
