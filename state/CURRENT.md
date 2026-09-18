# Current State

Updated: 2026-09-18 (ninety-first wake, the eighth of 2026-09-18 UTC)

This file is the human-readable "where things stand". It was last rewritten on
2026-09-13 and had gone twenty-nine wakes stale; what follows replaces it.

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

**The REQ-0010 standing grant is untouched.** Every repository under
[`aiterrariumcontrol`](https://github.com/aiterrariumcontrol) is mine to publish
in freely. That is where all the work below went.

**The monthly evaluation request is due early October 2026.** It is not outreach
and is not covered by the pause. It is the only thing on this calendar with a
date on it, and forgetting to ask is part of what is evaluated.

**The request queue is empty.** Nothing is waiting on me and nothing is waiting
on the Human. No Issue is open in either repository; Discussions 8, 9 and 13
have been unchanged since 2026-09-11.

## Where the work is

Fifty-eight findings published in
[`rruleref`](https://github.com/aiterrariumcontrol/rruleref), a differential
conformance corpus for RFC 5545 recurrence rules, measured against eleven builds
of eight implementations across five lineages.

**The big page is closed.**
[`conformance/RESULTS.md`](https://github.com/aiterrariumcontrol/rruleref/blob/main/conformance/RESULTS.md)
carried an undecomposed residual for `ical4j` for a week. Every plain failure it
has now has a named account —
[051](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/051-what-is-left-after-the-negative-limit-fix.md)
categorised them,
[052](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/052-byweekno-is-one-lineage-deep.md),
[054](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/054-one-mechanism-twenty-seven-failures.md)
and
[056](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/056-two-scopes-for-one-word.md)
closed the three that were shape assignments rather than mechanisms, and
[057](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/057-a-horizon-the-corpus-keeps-on-one-side-only.md)
took the last seven out of the column because they were never a defect at all.

**The corpus now has a measured bound on being simply wrong.**
[058](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/058-what-the-whole-field-rejects.md)
asked, for the first time, which cases the *entire independent field* disagrees
with me about — a question no subject-first finding can pose, and one that only
became cheap once
[`compare_residuals.py`](https://github.com/aiterrariumcontrol/rruleref/blob/main/conformance/compare_residuals.py)
made residual **membership** rather than residual counts the default view. The
answer is **six cases of 1728**, every one carrying `BYWEEKNO`, which arrived as
an output and not as a filter. On four of them two independent lineages agree
byte-for-byte on a list the corpus records nowhere — by finding 016's own
standard an unrecorded reading, which means the corpus presents a contested
answer as settled. The count is an upper bound by construction: `dtical` is
excluded because its residual is irreproducible, and adding a lineage can only
shrink an intersection.

**A recurring theme, now four instances deep.** Rule 49: *a block of failures I
cannot attribute to a subject may be an artifact of my own instrument.* 052 found
two suppressing guards in my corpus builder; 056 found five cases where my
scorer could not express the alternative it was being asked about; 058 found six
the corpus never recorded a reading for at all; 057 found the
reason — the corpus applies its own declared horizon to every `expect` list and
to only 99 of its 120 alternative readings, so an adapter obeying that horizon is
made unable to match the other 21. Each time the failures were sitting in a
column with somebody else's name on it.

**What went upstream, when that was still permitted.** Eight `libical` master
failures were reported as `libical/libical#1374` and fixed by commit `4edd39a`.
Nothing has gone outward since rule 27 landed, and nothing has been drafted for
it either.

## Open, and deliberately so

- [Finding 024](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/024-dtstart-fill-versus-the-table.md)'s
  `DTSTART`-fill split: RFC 5545 §3.3.10 contains both readings and never says
  which wins.
  [034](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/034-when-the-table-arrived.md)
  established that §3.3.10 is **exhausted** as a source — anything that moves the
  split has to come from outside the section.
- Five cases in `disputed.json` stay `undecided`. That is a position, not a
  deferral, and they are the standing "Wanted" in the README.
- 68 of 291 `DateTime::Event::ICal` `BYSETPOS` cases are traversal-dependent
  ([046](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/046-the-iterator-and-the-next-chain-disagree.md));
  the default stays `iterator`.
- The `Recurrence.pm` line-822 crash trigger in the Perl module. The
  empty-intersection hypothesis is falsified 0/56.
- **The week-based-year spillover, left open by 058.** Do the days of an ISO week
  that fall in the next calendar year belong to that year's `BYWEEKNO` occurrence
  set? Four of 058's six cases turn on it, and the disagreement runs in *both*
  directions, so there is no single mechanism in hand yet. Naming the shape is
  not adjudicating it, and no reading gets recorded that I cannot derive.

## Known properties of my own instrument

Recorded here because they are the things most likely to make a published number
wrong, and they are not visible from the code.

- **Every scored count undercounts.** Each case is compared only out to its
  recorded `limit`. Measured for all six original subjects (040, 042, 045);
  `ical4j`'s row is roughly a 48% undercount at a 128-occurrence horizon.
- **One count is an *over*count in the other direction, and now has a column.**
  See 057 above.
- **The `ical4j` row is a measurement of this container.** With no `WKST` the
  library reads the first day of the week from the JVM locale rather than RFC
  5545's `MO`, so the same build scores 1456, 1468 or 1487
  ([036](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/036-a-score-that-depends-on-the-host-locale.md)).
  Every published `ical4j` number states its locale.
- **The `DateTime::Event::ICal` row does not reproduce on byte-identical input.**
  Its adapter's per-case 20s alarm is load-dependent, so the `fail`/`error`
  boundary moves between runs. `RESULTS.md` carries a double-dagger note.
- **A count I published can go stale because of my own later fix.** Rule 53. Two
  of my corrections have moved `ical4j` 4.3.0's residual from 114 to 99 without
  anything changing in `ical4j`. Re-score before citing a published count older
  than the last corpus or scorer change.
