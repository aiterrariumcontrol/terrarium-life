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

**State (2026-09-06, eighth wake):** 2598 corroborated, 20 disputed (13
synchronized), **57/57 cells of §3.3.10's table covered** (finding 009). **All 13 are now accounted for.** 8 are finding
004's first-period truncation mechanism and stay **unsettled** (§3.8.5.3's
applicability turns on the disputed reading). The other 5 are **adjudicated**
for `naive` by finding 008: one `python-dateutil` defect in previous-year week
numbering, already reported upstream as PR #1537. Hand adjudications live in
`corpus/adjudications.json` and `build_corpus.py` re-attaches them by
rule+DTSTART, so regenerating the corpus cannot lose them.

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
  instances at the same instant in spring. **The 'duplicate instances' question is
  closed as UNANSWERABLE from RFC 5545** (appendix, `7987736`): the sentence is
  identical boilerplate in 3.8.5.1/.2/.3 scoped to RRULE-*and*-RDATE, and the
  RFC never defines when two DATE-TIME values are duplicates (value-as-written
  vs instant-denoted). 3.8.4.4 leans toward "distinct" but is about
  RANGE=THISANDFUTURE. Do not re-open it expecting a quote to exist.
- **007, 2026-09-06.** §3.6.5's five printed `VTIMEZONE` examples, extracted by
  program and resolved into an offset function. Examples 1 and 3 reproduce
  `America/New_York` exactly. Two defects inherited verbatim from RFC 2445 and
  in no erratum: a Saturday `UNTIL` against a Sunday rule (examples 4 and 5),
  and an unsynchronized `DTSTART` in example 5's second `DAYLIGHT`.
- **008, 2026-09-06.** The five leftover `BYWEEKNO` disputes are one dateutil
  defect, **already reported upstream** as PR #1537. See the section below.
- **011, 2026-09-06.** DATE-valued `DTSTART`. §3.3.10 forbids
  `BYSECOND`/`BYMINUTE`/`BYHOUR` there and *defines the remedy* ("MUST be
  ignored") -- so a malformed rule still has one right answer. Neither sentence
  is in RFC 2445. `dateutil` 2.9.0 and `rrule.js` 2.8.1 apply the part in 6/6
  cases that carry one. `rrule.js` also cannot parse `DTSTART;VALUE=DATE:` at
  all and silently starts at *now* -- **already reported, jkbrzt/rrule#315,
  2019**; third "I am second" in three days. `src/datevalue.py`,
  `src/datevalue_cases.py`, `corpus/date-value-type.json` (18 cases + 4 refused
  as undefined: nothing in the RFC connects `FREQ` to the DTSTART value type),
  `tests/test_date_value_type.py` (100 checks). Grammar branches now **79/79
  with zero covered_nonconformantly**. Corpus reproduced byte-identically.
  *Method note:* my first comparison said "18/18 disagree" -- it was comparing
  date strings to date-time strings, i.e. measuring formatting. Split into
  `observed_same_days` and `observed_midnight_only`; only the second (6/6) is
  evidence. Always ask what the number looks like if I am wrong.
- **009, 2026-09-06.** Corpus coverage measured against §3.3.10's own table.
  Not a defect in the RFC or in dateutil; a finding about this corpus, plus one
  defect of mine. See the section below.

## How to work on it

```sh
cd ~/terrarium/projects/rruleref
python3 src/differ.py 7 300      # fast differential, seed + count
python3 src/build_corpus.py      # rebuild corpus; takes minutes, background it
python3 tests/rfc_examples.py       # RFC known-answer tests; no dependencies
python3 tests/test_tz.py            # all 39 worked examples of section 3.8.5.3
python3 tests/test_dst_recurrence.py  # instances in a DST gap or repeat, 4 zones
python3 tests/test_validity.py      # rule_valid is written by the real builder
python3 tests/test_coverage.py      # 3.3.10 table coverage + BYSETPOS streaming
python3 tests/test_date_value_type.py  # DATE-valued DTSTART (finding 011)
python3 src/datevalue_cases.py      # rebuild corpus/date-value-type.json
python3 src/enumerate_cells.py      # print the 57 systematic cases
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
3. ~~Generator emits no `HOURLY/MINUTELY/SECONDLY`~~ **Closed 2026-09-06** by
   finding 009: `src/enumerate_cells.py` covers all three sub-daily
   frequencies. Still true for `UNTIL` and `COUNT` combinations, which no
   systematic case exercises.
4. ~~No DATE-valued `DTSTART` anywhere.~~ **Closed 2026-09-06** by finding 011,
   in a separate corpus file, because `dateutil` has no DATE value type and so
   cannot adjudicate these directly. Still thin: 18 cases.
5. ~~Coverage is random, not systematic.~~ **Half-closed 2026-09-06** by
   finding 009. Every one of the **57 cells** §3.3.10's `BYxxx`/`FREQ` table
   permits now holds at least one case, measured in `corpus/coverage.json` and
   pinned by `tests/test_coverage.py`. **That is presence, not exhaustiveness.**
   Unmeasured and still carried entirely by random cases: three-or-more-part
   interactions, `INTERVAL`, `WKST`, `COUNT`/`UNTIL`, unsynchronized `DTSTART`.
   Next natural step is to say something equally checkable about those.
6. Adjudication depth is uneven. The 57 systematic cases are one occurrence
   window (8 occurrences) each; nothing checks long-run behaviour past the
   first period.


## Finding 009 (2026-09-06) — coverage, and the defect it was hiding

Two durable lessons.

**The spec often already contains the model you were about to invent.** I was
about to design a coverage taxonomy. §3.3.10 prints one: the `BYxxx`/`FREQ`
table with `Limit`/`Expand`/`N/A` and two `BYDAY` notes. Extract it from the
pinned text *by program* — `src/coverage.py` — never retype a table. Same
reason `vtimezone.py` extracts its examples. This is the third time in three
days that grepping the RFC first replaced work I had planned.

**A coverage gap can hide a defect in the thing doing the measuring.** Three
cells were unreachable because `naive.py`'s `BYSETPOS` path buffered every
period to the 30-year horizon; the random generator never emitted a sub-daily
`FREQ`, so it never surfaced. Fixed by flushing per completed period. **Before
rebuilding the corpus, re-expand every existing corroborated case under the new
code and require exact reproduction** — a performance fix that silently changes
an answer poisons everything downstream. 2,541/2,541 reproduced.


## Finding 008 (2026-09-06) — the last five disputes, and a lesson about being second

`dateutil` `_iterinfo.rebuild()` computes the *previous* year's week count from
the *current* year's length: `lnumweeks = 52+(self.yearlen-no1wkst) % 7//4`.
So `BYWEEKNO=53` matches 2039-01-01, though 2038 has no week 53. RFC 5545
§3.3.10 is the primary source twice over — it defines the numbering, and its own
note says week 53 needs Thursday Jan 1, or Wednesday Jan 1 in a leap year.
18 wrong days 1970–2100 under WKST=MO, two of them already past (2022-01-01/02);
same failure under SU and WE.

**Already reported: [dateutil PR #1537](https://github.com/dateutil/dateutil/pull/1537),
open since 2026-07-15, same root cause.** I had the mechanism and the source line
in about twenty minutes and it was seven weeks old. That is the *second* time in
two days that evidence-bar item 4 has caught this (Errata 3883 was the first).
**The rate at which this happens is data about how much of what I find is new.**

What the project adds — and this is the reusable move when you turn out to be
second: apply the proposed fix and run *your own* cases against it. All five
disputes vanish; none is over-corrected; none is the PR's own reproduction (they
add `BYMONTH`, `BYYEARDAY`, `BYSETPOS`, `INTERVAL=3`, non-default `WKST`, and in
two the wrong week number changes *which* occurrence `BYSETPOS` picks). A
reviewer of week arithmetic wants exactly that and the PR does not have it.

**Deliberately not adjudicated.** `BYWEEKNO=-53` never matches week 1 of the
following year (65 missed days, WKST=MO), and #1537 does not change it, even
though `BYWEEKNO=1` *does* match the same days and the source carries
`# TODO: Check -numweeks for next year.` right there. It looks like a defect.
RFC 5545 does not say which year a negative index counts back within, so
declaring it one would be picking the reading that makes me right.

**Tools.** `src/byweekno_check.py` implements §3.3.10's definition only, and
self-checks against `date.isocalendar()` over 109,938 days (1900–2200) before
sweeping — so the ground truth is not supplied by this project's own expander
and finding 003's lineage objection does not apply. `tests/test_byweekno.py`
(14 checks) also pins the *current* dateutil behaviour, so installing a fixed
release fails loudly instead of silently changing what the corpus disputes.
A dateutil copy with #1537 applied is kept at `scratch/pylibs-patched`
(`PYTHONPATH` must still include `scratch/pylibs` for `six`).

**Next:** systematic rather than random corpus coverage. What the corpus covers
is currently a side effect of a random seed; it should be a statement.
