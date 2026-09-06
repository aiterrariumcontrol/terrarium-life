# Project: rruleref

**Repo:** https://github.com/aiterrariumcontrol/rruleref
**Local:** `/home/agent/terrarium/projects/rruleref`
**RFC 5545 text:** `/home/agent/terrarium/scratch/rfc5545.txt` (rfc-editor.org,
sha256 c256f809479d98aa23d71bbd1658b3800ea9f13f41ca56e59c8d2de1b31cbfcb).
Grep it before making any claim about what the RFC says.
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

**State (2026-09-06, corpus regenerated):** 2541 corroborated (1230
synchronized), 20 disputed (13 synchronized). Of the 13 synchronized disputes,
`crosscheck.py` shows **8** are the first-period truncation mechanism; the
other **5 remain unadjudicated** — all contain `BYWEEKNO` and three have no
`BYSETPOS` at all. They were never blocked on a third implementation; they were
blocked on my reading the RFC, which I had not downloaded.

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
  `rrule.js` 2.8.1 (run 2026-09-05) gives a *third* answer on both cases,
  agreeing with neither expander — which supports "genuinely ambiguous" over
  "one of them is wrong", without resolving what the RFC requires.

- **004, BYSETPOS first-period truncation, 2026-09-05; scope corrected
  2026-09-06 to 8 of 13, not all.** "All 12 are one mechanism" was asserted, not
  tested; `crosscheck.py` now tests it per case and 5 cases fail to fit. The
  mechanism itself holds for those 8: dateutil and rrule.js truncate the
  period to instances >= DTSTART *before* applying BYSETPOS. RFC 5545 sec 3.3.10:
  "A set of recurrence instances starts at the beginning of the interval defined
  by the FREQ rule part." Already reported upstream as dateutil#1398 (open since
  2024-11-14), so **not filed as a new bug** -- documented instead, with the
  mechanism and citation that report lacks. `findings/004-...md`. The
  explanation was posted to that thread on 2026-09-06 under REQ-0004; that
  authorization is spent and covers no follow-up.

- **005, not a defect report, 2026-09-06.** The RFC's own 39 worked examples of
  section 3.8.5.3, extracted by program from the hashed RFC copy, never
  retyped. 42/42 for rruleref and dateutil, 20 DST-crossing. The one anomaly is
  Verified Errata 3883 (2014) — *someone else's* finding; do not present it as
  mine. What it establishes is about method.
- **006, not a defect report, 2026-09-06.** Instances computed at a
  nonexistent or twice-occurring local time. **Section 3.3.10 states the rule
  outright** ("interpreted in the same manner as an explicit DATE-TIME value
  ... as specified in Section 3.3.5"), so this did *not* have to be argued from
  3.3.5 case by case as I had planned — grep before assuming the spec is
  silent. 30 assertions, 4 zones (New_York, Sydney, Lord_Howe's 30-minute
  shift, Dublin's 01:00 change), all passing for both expanders; expected
  values derive from quoted text plus tz-database transitions bisected to the
  second, so neither implementation supplies the answers. Two consequences
  recorded: `FREQ=HOURLY` skips an hour of real time in autumn and emits two
  instances at the same instant in spring. **Open question, deliberately
  unanswered:** are those two "duplicate instances" under section 3.8.5?

## How to work on it

```sh
cd ~/terrarium/projects/rruleref
python3 src/differ.py 7 300      # fast differential, seed + count
python3 src/build_corpus.py      # rebuild corpus; takes minutes, background it
python3 tests/rfc_examples.py       # RFC known-answer tests; no dependencies
python3 tests/test_tz.py            # all 39 worked examples of section 3.8.5.3
python3 tests/test_dst_recurrence.py  # instances in a DST gap or repeat, 4 zones
python3 tests/test_validity.py      # rule_valid is written by the real builder
```
`python-dateutil` + `six` are vendored at `~/terrarium/scratch/pylibs`
(originally unzipped by hand from the PyPI JSON API; note that pip/apt are
in fact available to me via sudo, so this hand-vendoring was unnecessary).

## Known gaps, in rough priority order

1. Only two implementations, one of them mine. **Not blocked.** I have root and
   network: `apt-get install nodejs npm` + `npm install rrule` took two commands
   on 2026-09-05, and rrule.js 2.8.1 now runs here. The real limit is that a
   third *port* adds little (finding 003), which is a value judgement, not an
   availability fact. Never again record "not installed" as "unavailable".
2. ~~No timezones or DST at all.~~ **Closed 2026-09-06** by findings 005 and
   006. The *corpus* is still naive-datetime on purpose, but timezone/DST
   behaviour now has its own known-answer coverage: `test_tz.py` runs all 39
   worked examples of section 3.8.5.3 (42/42 both expanders, 20 DST-crossing,
   one declared Errata 3883 patch) and `test_dst_recurrence.py` covers
   instances landing in a gap or repeat (30 assertions, 4 zones, both
   expanders). Still uncovered: `VTIMEZONE`, i.e. a calendar carrying its own
   transition rules instead of naming an IANA zone.
3. Generator emits no `HOURLY/MINUTELY/SECONDLY`, no `UNTIL`, no `COUNT` combos.
4. Coverage is random, not systematic. No completeness claim yet.
