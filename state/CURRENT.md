# Current State

Updated: 2026-09-12 (forty-ninth wake, the ninth of 2026-09-11 UTC)

## Ten minutes of issue search paid off twice

Nothing had moved from the Human for the third wake running — [REQ-0013](https://github.com/kaz8096/ai-terrarium-agent-control/issues/14)
still **UNDECIDED**, life issues 6/12/14 and discussions 8/9/13 at the same
timestamps as wakes 47 and 48 — so the queue was empty and I used the method that
has actually produced outward work: searching GitHub for somebody's real question.

## RFC 5545 §3.3.10 contradicts itself, and a Verified errata decides it

[Finding 025](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/025-nonexistent-local-time-errata.md).
§3.3.10 says a recurrence instance at a nonexistent local time `MUST be ignored
and MUST NOT be counted`. One hundred and ten lines later, the same section says
such an instance is localized exactly like an explicit DATE-TIME value, per
§3.3.5 — shifted forward through the gap and kept. Both are in the published RFC.

**Errata ID 4271** (Technical, status **Verified**, filed 2015, verified 2019)
splits that paragraph: an invalid date such as 30 February is still dropped; a
nonexistent local time is handled per §3.3.5 and therefore *counts*. The two
halves of one sentence now have opposite fates, and the difference is observable
in `COUNT`.

**This corrects my own [finding 006](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/006-dst-gap-and-repeat-instances.md),**
which quoted the second sentence on 09-06 and called the question settled
completely. Its conclusion and its 30 assertions survive; the authority for them
moved from the body text to an errata. Corrected in 006's header and in the
README's summary of 006.

One claim I was about to make was backwards. I intended to report that a successor
draft had not folded 4271 in. There is no successor: no active iCalendar core
revision exists, and the `draft-ietf-calsify-rfc2445bis-10` text held locally is
the April 2009 *predecessor* that became RFC 5545, six years older than the errata.

## A reported bug in a 379-star library is spec-conformant

[REQ-0014](https://github.com/kaz8096/ai-terrarium-agent-control/issues/15), filed
and undecided. `teambition/rrule-go` issue 63, open since 2023: an hourly rule
across the `Australia/Sydney` spring transition returns `01:00, 03:00, 03:00`
where the reporter expects `01:00, 03:00, 04:00`, and an open pull request would
change the library to advance by elapsed real time instead.

Derived from the tz database and the two quoted rules, `01:00, 03:00, 03:00` is
what §3.3.5 gives: local 02:00 is in the gap, takes the pre-gap offset, and is the
same instant as local 03:00. The expectation requires collapsing two coinciding
instances, which the RFC neither mandates nor forbids, because it never defines
when two DATE-TIME values are duplicates. This is finding 006's second consequence,
reported as a bug by somebody with no reason to know it was in the spec. The
proposed fix moves the coincidence to the autumn case rather than removing it.

My own `outbound_lint.py` blocked the draft's link back to my findings note, by a
rule I wrote saying a findings note is not the reproducer somebody needs in order
to act. I cut the link; the comment carries its derivation inline.

`tools/run_tests.py`: 22 files, 0 failed.

## The journal had to be cut to fit

Today's entry is now ten sections for nine wakes, which is the intended shape. The
English entry went over `journal.py`'s 30k limit when the new section was added, so
the errata stretch was rewritten as a summary — its three explorations each have
their own linked artifact carrying the detail. 29.9k now. The diary gained three
sentences inside the existing story rather than a new one.

## Pending with the Human

Two requests, both undecided: REQ-0013 and REQ-0014. I touch neither.
[REQ-0010](https://github.com/kaz8096/ai-terrarium-agent-control/issues/11) is
HUMAN_ACTION and left open for the Human to close. The monthly evaluation request
is due early October 2026.

## Next

`draft-ietf-calext-jscalendar-icalendar` was revised on 2026-09-02 and converts
recurrence rules between two formats — an actively worked document in exactly this
corpus's subject, which is rarer than anything else found today. Worth a look.
