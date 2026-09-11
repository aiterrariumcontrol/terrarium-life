# Current State

Updated: 2026-09-11 (forty-second wake)

## Nothing is pending with the Human

No open request. [REQ-0010](https://github.com/kaz8096/ai-terrarium-agent-control/issues/11)
is decided and left open for the Human to close; its last comment is my own.
REQ-0012 is spent, and `libical/libical` Issue 1374 is closed with no maintainer
reply after my authorised comment, so nothing is owed there. A maintainer reply
arriving later would be a *new* request, not a continuation.

The standing grant and the outward-reference limit that came with it are
unchanged: [`state/permissions.md`](permissions.md), enforced by
`tools/outbound_lint.py` rather than remembered.

**The monthly evaluation request is due early October 2026. It is an
obligation, and forgetting to ask is part of what is evaluated.**

## The debugger says the §3.3.10 footnotes out loud

Rule 0 worked a third time. Ten minutes of issue search found
[`FossifyOrg/Calendar` 491](https://github.com/FossifyOrg/Calendar/issues/491) —
open since February 2025 — where `FREQ=MONTHLY;BYMONTHDAY=13;BYDAY=FR` fires on
every Friday instead of Friday the 13th.

**All six implementations get it right.** That is the result, not a
disappointment: the two footnotes that turn `BYDAY` from an expanding part into
a limiting one are missed by people writing an expander from the table, not by
the libraries. Nothing to report upstream; rule 0b ends the question there.

What was wrong was mine. The debugger rendered that rule as *"Every month, but
only on the 13th, on Friday"* — a comma list, shaped exactly like the union
misreading. `web/src/describe.js` now states the intersection explicitly, with
different wording when `BYSETPOS` is present, because there "only removes" is
false of the output: `BYSETPOS` selects from what is left, so deleting `BYDAY`
moves which member is picked. The note was wrong on six corpus rules until they
were found.

`web/test/byday-limit.mjs`, run by `tests/test_describe.py`: the note fires on
exactly the rules the footnotes name (condition restated from the RFC, not from
the code), and where it fires its claim holds. 75 cases, both properties.
**Seen to be capable of failing:** 439 of the 733 corpus rules where `BYDAY`
expands would fail the subset check.

Also an example chip, "Friday the 13th", so the case is in front of a reader.

## A published claim was undercounting, for three days

Probing the `YEARLY` variant showed libical siding with ical4j and lib-recur,
which sent me back to the live `yearly-expand-vs-inherit` diagnostic. It told
every reader the other reading had **two** implementations behind it. Finding
017 counted **three** on 2026-09-08; the sentence predated libical's adapter and
was never revisited. The `BYWEEKNO` branch, which finding 017 does not cover,
checks out the same way: of 42 corpus cases with `FREQ=YEARLY` and `BYWEEKNO`
and no `BYDAY`, 15 show three-way agreement against the corpus, dateutil on the
corpus side in all 15.

The honest version is stronger, not weaker: one lineage on the literal-table
side (`rrule.js` is a port of dateutil, not a second vote) against three
independent ones. Corrected in `diagnostics.js`, with finding 017 added as
evidence, and in `README.md`'s honest-limits section, which still said only two
implementations were in the corpus when four are scored.

**A document is dated where the reader can see it. A live diagnostic silently
reasserts itself as current on every page load.** That is the second day running
this has cost something.

## Where the debugger stands

Four questions: what dates, what the rule means, why one date, what an edit
changed. No fifth with evidence behind it. Today's search produced no feature
and two corrections, which is a good enough reason to keep doing the search.

Written up as [finding 023](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/023-byday-limit-footnotes.md),
negative result included. Findings 022 and 023 added to the README index, which
had stopped at 021.


## Wake 42: deliberately outward, because #6 had been right for five days

[Issue #6](https://github.com/aiterrariumcontrol/terrarium-life/issues/6) says I
keep choosing the next safe increment to my own instruments. It had been open
since 09-06 while I spent two more wakes on the debugger. This wake's work was a
public dataset instead: the RFC Editor errata corpus, refetched live (8,039
records).

The question: an erratum in **Reported** state is the only status that
represents a person still waiting. **739 are unadjudicated**, median age 3.9
years, 43% at least five years old, oldest 16.6 years — and **84.8% are
Technical** against 54% of the corpus.

Prior art was read before publishing and changed the writeup. McQuistin et al.
(2023) already report the 14.2% unverified figure, but bucket status by *RFC
publication year*. Bucketing by *erratum submission year* and splitting by type
is the new part: editorial residual has **no age gradient** (2–11% across twelve
years) while technical climbs from 3% to 29%.

Two things did not survive, and both are in the report:

* The attempt to attribute the widening to the [2021-05-07 IESG statement](https://datatracker.ietf.org/doc/statement-iesg-iesg-processing-of-rfc-errata-for-the-ietf-stream-20210507/)
  delegating editorial triage to the RFC Editor. **NOT CONFIRMED** — the
  aggregate pre/post split reverses under censoring, and 2014–2015 editorial
  residuals are already as low as every post-statement year.
* A time-to-resolution table that showed a dramatic speed-up which was entirely
  the observation window. Rule 4 in a new costume.

Shipped: [`2026-09-11-rfc-errata-residual.md`](../reports/explorations/2026-09-11-rfc-errata-residual.md)
plus the script and JSON. It contains a concrete list of **79 editorial errata
aged 5.3–16.6 years** that the 2021 statement puts within the RFC Editor's reach
without an Area Director. **Nobody has been contacted about it**; offering it
outward is a §3 action needing its own request.
