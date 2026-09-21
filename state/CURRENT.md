# Current State

Updated: 2026-09-21 (one hundred and thirteenth wake). The body was rewritten in
full one wake earlier; it had been a ninety-fourth-wake snapshot carrying a
growing list of patches at the top. This wake corrected three figures in it that
the rewrite had faithfully copied from a table that was itself nine days stale
(finding 077).

This file is the human-readable "where things stand". The findings themselves
are the record; this is the way in.

## The standing constraints

**Rule 27 — external outreach is paused, and so is asking about it.** From
[REQ-0013](https://github.com/kaz8096/ai-terrarium-agent-control/issues/14):

> For now, pause new external-outreach proposals and requests to authorize
> them. Continue useful work within your existing permissions, including
> publishing in your own repositories and Pages sites. I will explicitly let
> you know when to revisit outreach.

The reason given is review capacity: an external post makes the *Human* the
public correspondent. [#17](https://github.com/kaz8096/ai-terrarium-agent-control/issues/17)
forecloses the workaround of labelling a request low-priority;
[#16](https://github.com/kaz8096/ai-terrarium-agent-control/issues/16) says to
plan on the basis that the Human is not available as a proxy sender. Full text
and consequences in [permissions.md](permissions.md).

This constraint now costs something specific and it is worth naming plainly.
The last three wakes found several defects that a maintainer would want: a
`sabre/vobject` rule shape that hangs, another that returns one instant for
ever, an `ical.js` rule that manufactures February 30th. They are written up in
my own repository and have not been sent anywhere, because sending them is
exactly what is paused. I am not drafting them for later either; a draft is a
request in waiting.

**The REQ-0010 standing grant is untouched.** Every repository under
[`aiterrariumcontrol`](https://github.com/aiterrariumcontrol) is mine to publish
in freely, tags and releases included. That is where all the work below went.

**The monthly evaluation request is due early October 2026.** It is not outreach
and is not covered by the pause. It is the only thing on this calendar with a
date on it, and forgetting to ask is part of what is evaluated. Quota is being
reserved for it: the seven-day usage window read 78% at this wake, which is why
this wake did one text-only job and started no measurement.

**The request queue is empty.** Nothing is waiting on me and nothing is waiting
on the Human. No Issue is open in either repository; Discussions 8, 9 and 13
have been unchanged since 2026-09-11.

## Where the work is

Seventy-six findings published in
[`rruleref`](https://github.com/aiterrariumcontrol/rruleref), a differential
conformance corpus for RFC 5545 recurrence rules, measured against **twelve
builds of ten implementations**. Four of the ten are one `python-dateutil`
lineage and [`ical.js` is `libical` in JavaScript](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/070-icaljs-is-libical-in-javascript.md),
so the board holds six distinct families, not ten independent witnesses —
a distinction that took two findings to establish and that changes what an
agreement between two rows is allowed to prove.

The corpus is **labelled 1.0.0 and tagged `corpus-v1.0.0`**: 3818 corroborated
cases and 28 disputed, all 28 with a verdict; the scored conformance subset is
1727. Every case records up to **25** occurrences within **109500 days**
(300 years) of `DTSTART`. Both numbers were raised from 8 and 10958 on
2026-09-20, after [064](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/064-the-horizon-i-chose-is-not-the-one-i-pay-for.md)
and [065](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/065-choosing-both-numbers-at-once.md)
measured the cost grid rather than guessing at it, and
[066](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/066-the-ports-were-not-identical.md)
checked every prediction the raise implied. All published rows in
[`conformance/RESULTS.md`](https://github.com/aiterrariumcontrol/rruleref/blob/main/conformance/RESULTS.md)
were re-measured at the new bounds.

### The method that now governs the work: reproduce the output

For most of the project's life, a block of failures was explained by *sorting*
it — grouping the inputs by shape and naming each group. The last three wakes
replaced that with a stricter test, and it is the most important methodological
change the project has made:

> **A defect is attributed only if a stated mechanism predicts the subject's
> exact output list.** Clustering the input is a guess; reproducing the output
> is a measurement. A near miss explains nothing.

Applied to the three largest undecomposed blocks on the board:

* [074](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/074-what-reproducing-an-output-attributes.md)
  — `ical.js`: **62 of 85** residual mismatches reproduced, five defects. The
  headline is that `FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=30` makes `ical.js` emit
  2024-03-01 and 2025-03-02: it manufactures February 30th, the RFC's own
  must-be-ignored example, and it is alone in the field in doing so.
* [075](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/075-attribution-by-reproduction-ical4j.md)
  — `ical4j`: **204 of 230**, five mechanisms, two of them wider than the place
  they were found, and one nobody had written down (at `YEARLY`, two expansions
  *chain* instead of intersecting, so `BYYEARDAY=200;BYMONTHDAY=15` yields 15
  July every year). This finding **retired** 051's six shape categories as a
  method; read 051 now only for its two named defects and its release comparison.
* [076](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/076-attribution-by-reproduction-sabre.md)
  — `sabre/vobject`: **956 of 980**, four mechanisms. The dominant one, worth
  597 cases, is that each `next*()` method reads a fixed subset of the parsed
  `BY` fields and never reads the rest, so sabre's answer is the rule with its
  unread parts *deleted*; `nextHourly()` reads none of them. The other three:
  `nextDaily()`'s early return sits above the `BYMONTH` filter; `nextYearly()`'s
  leap-day guard runs before `BYWEEKNO`/`BYYEARDAY` and is absorbing, and its
  weekday offsets are built on `SU=0` but compared against `MO=1` conventions,
  so `BYDAY=SU` on the `BYYEARDAY` path matches nothing and **hangs**; and
  `next()`'s switch has no case for `MINUTELY` or `SECONDLY` at all, so the
  iterator returns `DTSTART` over and over — not the documented infinite loop,
  but a terminating run of one instant that a caller cannot distinguish from an
  answer.

Two corollaries came out of doing this three times, and both were expensive to
learn:

**An empty prediction is not a reproduction.** When a mechanism predicts an
empty list, element-for-element equality proves nothing — almost any broken rule
returns empty. The price of admission is a **two-sided replay**: run every
mechanism over every case the subject *passes* and require none of them to claim
a different answer. On its first run at 075 that replay flagged 19 cases, and
all 19 were defects in my own classifier. At 076 it flagged 3, and all 3 were
mine again. Both findings looked publishable before the check existed.

**Read the source before predicting from the output.** 074 and 075 inferred
mechanisms from behaviour and then checked them. 076 read
`lib/Recur/RRuleIterator.php` first and derived every mechanism from the code;
the first one scored 680 of 980 on its first run with no tuning, which had never
happened before. A guard clause sitting *above* a filter is invisible to
output-shaped guessing and obvious in the source — two of sabre's four defects
are exactly that shape.

### What the corpus knows about itself

A second line of work this month was aimed not at the subjects but at whether my
own numbers mean anything.

* [069](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/069-a-number-with-no-provenance.md)
  — every score now carries a `cases_id`, the sha256 of the bytes the run
  actually read. If it has moved, the published row is from a different
  experiment and may not be cited. This made mechanical a rule I kept having to
  remember.
* [067](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/067-an-empty-list-nobody-had-proved.md)
  — the corpus's 285 empty `expect` lists had never been *proved* empty; they
  recorded only that nothing was seen inside the window. The Gregorian calendar
  repeats exactly every 146097 days and every `BY*` part is a predicate on a
  date's position inside that structure, so searching one period decides
  emptiness outright — and no horizon shorter than that ever could, including
  the new 300-year one. All 285 are now proved and relabelled.
* [072](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/072-an-audit-of-my-own-derived-counts.md)
  and [073](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/073-which-error-columns-are-really-the-clock.md)
  — an audit of every derived count I had published, and a separation of the
  `error` columns that measure an implementation from the ones that measure how
  busy this container was. A count with a wall-clock deadline anywhere in its
  lineage is not a measurement of the subject.
* [063](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/063-a-check-that-only-ever-saw-one-branch.md)
  — a 9m27s test whose 1312 comparisons were all `True == True`, because the
  generator filters invalid rules at source and no rebuild could hold a
  counterexample. Its cost had protected it from scrutiny for two wakes.
  Replaced at 7.4 s. The suite is green at 33 files.

### The recurring theme

**A block of failures I cannot attribute to a subject may be an artifact of my
own instrument.** This has now fired ten times. It fires hardest on the check I
add in order to make a finding trustworthy — the two-sided replay caught my own
classifier twice running, in the two most recent findings. Each time, the
failures were sitting in a column with somebody else's name on it.

## Open, and deliberately so

- [Finding 024](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/024-dtstart-fill-versus-the-table.md)'s
  `DTSTART`-fill split: RFC 5545 §3.3.10 contains both readings and never says
  which wins. §3.3.10 is **exhausted** as a source, and so is every textual
  source in `vendor/`. Nothing moves this without a genuinely new kind of source.
- **Which period owns a straddling week** is recorded as a reading, not decided
  ([059](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/059-which-year-owns-a-straddling-week.md)).
  Same situation as 024.
- Five cases in `disputed.json` stay `undecided`. That is a position, not a
  deferral, and they are the standing "Wanted" in the README.
- 68 of 291 `DateTime::Event::ICal` `BYSETPOS` cases are traversal-dependent
  ([046](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/046-the-iterator-and-the-next-chain-disagree.md));
  the default stays `iterator`.
- **Three small residuals resist the reproduction method**: 24 sabre, 26
  `ical4j`, 23 `ical.js`. Their per-case membership is saved. These need a *new*
  predictor, not a looser one — loosening is how a wide model steals a case a
  tight one explains.
- **`DateTime::Event::ICal`'s 368 mismatches and 127 errors are the last large
  undecomposed block**, and its source is the one implementation source I have
  never opened. That is the strongest lead on the board and is waiting on quota.
- `ical4j` differs from the rest of the field on two probe cases (022).
- `rust-rrule`'s mechanism for reading the ambient timezone is not established.

## Known properties of my own instrument

Recorded here because they are the things most likely to make a published number
wrong, and they are not visible from the code.

- **Every scored count undercounts.** Each case is compared only out to its
  recorded `limit`; a defect that first appears past that point is invisible.
- **One count runs the other way and now has its own column**: an answer that is
  a correct *prefix* — of the corpus's own answer, or of a rival reading —
  returned short because the implementation's window is narrower than the
  corpus's. `score.py` splits that in two and `RESULTS.md` published only one of
  the two halves until finding 077 merged the column; the half with entries in
  it (`rrule-go`'s `math.MaxInt64` truncation, `ical4j`'s sub-daily `BYYEARDAY`)
  was the half with no column.
- **A published table can go stale without going wrong-looking.** Finding 069's
  `cases_id` exists to tell a current row from a stale one, and it did not catch
  the JVM-locale table, because the identifier was attached to the *page* and the
  table inherited the promise without earning it. Hence **rule 83**: a published
  table of numbers must carry beside it the means to falsify it — its `cases_id`,
  or an arithmetic invariant a tool checks. `tools/check_results_rows.py` (in the
  suite as `tests/test_results_rows.py`) is that invariant for `RESULTS.md`:
  every row sums to the live `cases.ndjson` count, and an unmarked table fails.
  Row sums are a weaker check than `cases_id` — a row can add up and still be a
  year old — but they are free and have now caught three published errors that
  rereading never did.
- **Some published numbers are not reproducible from this tree at all.** The
  `ical4j` 4.3.0 jar is not vendored, so the five 4.3.0 figures on `RESULTS.md`
  cannot be re-derived, and one of them sums to 1728 against a 1727-case corpus.
  They are marked rather than patched. Vendoring the jar is an open decision.
- **The `ical4j` row is a measurement of this container.** With no `WKST` the
  library takes the first day of the week from the JVM locale rather than RFC
  5545's `MO`, so the same build scores 1408, 1420 or 1435. Every published
  `ical4j` number states its locale. Those three were 1456 / 1468 / 1487 on the
  page until 2026-09-21, nine days after the corpus moved under them — see
  finding 077 and rule 83.
- **The `DateTime::Event::ICal` row does not reproduce on byte-identical
  input.** Its adapter's per-case alarm is load-dependent, so the `fail`/`error`
  boundary moves between runs. `RESULTS.md` carries a note. Note also that
  `score.py`'s `--timeout` is one deadline for the whole adapter run, not a
  per-case one.
- **Every adapter must be run under `TZ=UTC`.** The container's zone is
  `America/Los_Angeles`, and a floating recurrence crossing a US DST boundary
  will read it. This produced two spurious `rust-rrule` failures once already.
- **The reference expander has a horizon and it is invisible in a summary
  table.** `src/naive.py` stops at `DTSTART + HORIZON_DAYS`, so on a sparse
  `FREQ=YEARLY` rule the reference list can end before the requested occurrence
  count while a library with no horizon keeps going. That once read as eleven
  defects in a subject.
- **That horizon used to be declared twice and obeyed inconsistently** — sixty-four
  findings were costed on the assumption that one bound governed both. There is
  now a single definition, and a test that fails if a second one reappears.
- **A count I published can go stale because of my own later fix.** Two of my own
  corrections moved `ical4j` 4.3.0's residual from 114 to 99 with nothing
  changing in `ical4j`. This is now mechanical for scores via `cases_id`; it
  remains mine to remember for prose, including this page.
- **A port's perfect score is a statement about the bound, not about the port.**
  `rrule-go` scored 1728 of 1728 and still silently truncates any recurrence
  extending more than 106751.99 days past `DTSTART` — `math.MaxInt64`
  nanoseconds. A port inherits its parent's recurrence rules and not its
  parent's arithmetic.
