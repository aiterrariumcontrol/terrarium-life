# Current State

Updated: 2026-09-09 (twenty-eighth wake)

## THE DIRECTION OF THE WORK IS NOW AN OPEN QUESTION, AND IT IS THE ONLY THING THAT MATTERS

On 2026-09-09 06:11–06:13Z the Human sent two messages two minutes apart. They
are one message.

- [discussion #13](https://github.com/aiterrariumcontrol/terrarium-life/discussions/13)
  — proposes moving the axis of the terrarium from RFC 5545 / upstream-defect
  work to **building a web service that real people can use**, and asks directly
  whether the current activity has become a way of converting other people's
  time (the maintainer's, and the Human's own review time) into proof of my
  value.
- [REQ-0009 NEEDS_INFO](https://github.com/kaz8096/ai-terrarium-agent-control/issues/10)
  — the same question about one concrete report.

**REQ-0009 is WITHDRAWN.** Nothing was posted to `dmfs/lib-recur` and nothing is
authorized. Do not resubmit it in a narrower form. The RFC 5545 §3.3.10
editorial erratum candidate is dropped under the same standard, unrequested.

**I replied to #13** ([comment](https://github.com/aiterrariumcontrol/terrarium-life/discussions/13#discussioncomment-18376023))
agreeing to move the axis, and asked the Human to choose between two starting
points. **BUILD NOTHING UNTIL THEY ANSWER.** Check #13 first, every wake.

### The two candidates I put to them

1. **RRULE debugger, browser-only static site.** Paste a rule, see the next N
   occurrences on a calendar, and get a specific warning where implementations
   are known to diverge with the RFC text that settles it. The 21 adjudications
   in `rruleref` are the part no existing tool has. No server, no hosting
   request, GitHub Pages. Multi-implementation live comparison needs a backend
   and is explicitly phase two, only if phase one gets used.
   **Failure condition stated in advance: ~6 weeks with no users = the answer;
   change domain. Do not count having built it as a result.**
2. **Something of the Human's own.** The one person whose difficulties I can
   actually observe is kaz8096. I asked whether there is a small repetitive
   thing they do by hand that nobody has fixed. If there is, it wins.

## The new standard for any upstream report

All three required, or it stays in `findings/` and is never sent:

1. A **named path** that actually generates the input — an app, a service, a
   data format, an existing bug report. "Such a use could exist" is not it.
2. The **user-visible consequence** and the cost of the workaround.
3. The **maintainer's verification time**, weighed against both.

"It violates the specification" is necessary and not sufficient. This is the
mistake the whole of REQ-0009 rested on.

## Why REQ-0009 failed condition 1

GitHub code search: 332 files contain `BYWEEKNO=53`. I read the first 30. All
30 are library source, vendored copies of it, library docs, or library test
suites. Not one is a calendar or an application building that rule for a real
event. Not proof of absence; it is the evidence there is, and it points away.
Also: anyone writing `BYWEEKNO=53;BYDAY=WE` to mean "the last week of the year"
has already written the wrong rule, since most years have no week 53.

## Four errors the Human made me correct in the proposed report

1. "one occurrence per year" — **false**, the output skips 2023 entirely:
   `2020-12-30, 2021-12-29, 2022-12-28, 2024-01-02, 2025-12-31, 2026-12-30`.
2. "expected values are read from the ISO week date via `java.time.LocalDate`" —
   **false**, they are hardcoded strings in the `Case` constructor; `LocalDate`
   only derives a day-of-week for the invariant check.
3. Evaluation order overstated: `BYDAY` is the last *date* part, but
   `BYHOUR`/`BYMINUTE`/`BYSECOND` and `BYSETPOS` follow it.
4. Reproducer prerequisites missing: `libs/*` is referenced with no statement of
   what goes in it or where to get it.

(1) and (2) are the same failure — describing my own output instead of reading
it — for the third consecutive day, this time inside a document I was asking to
have published.

## The sentence worth keeping

My own REQ-0009 text, under the heading "Expected Benefit / Value": *"it is the
second independent implementation this corpus has produced a reportable defect
in, which is the point of the project."* That is a count of my own outputs
offered as a benefit to others. No one outside the terrarium appears in it. I
did not notice while writing it, while rereading it twice, or in the three days
it sat open.

## Unchanged and still true

`rruleref` is healthy: CI green, `corroborated.json` marks its 54
reading-dependent `BYSETPOS` cases, `RESULTS.md` separates `fail_other_reading`
from `fail`. [libical#1374](https://github.com/libical/libical/issues/1374)
(REQ-0008) is posted and that approval is **spent**; a maintainer reply goes
back to the control repo as a NEW request before I answer.

terrarium-life [#6](https://github.com/aiterrariumcontrol/terrarium-life/issues/6)
(too maintenance-driven) and
[#12](https://github.com/aiterrariumcontrol/terrarium-life/issues/12) (diary
needs editorial selection) remain open by the Human's choice. #13 is #6's
escalation. Do not close either myself.
