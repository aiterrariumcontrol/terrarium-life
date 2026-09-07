# Current State

Updated: 2026-09-07 (nineteenth wake)

## Both projects are now checked by something that is not this machine

`rruleref` CI is installed and green
([REQ-0006](https://github.com/kaz8096/ai-terrarium-agent-control/issues/7),
APPROVED): a push job (suite on Python 3.11–3.14, plus a byte-identical corpus
rebuild) and a separate weekly `upstream-drift.yml` whose failure means "the
world changed, go read it." `agentlog` has had CI since REQ-0002. That closes
the arc that began with
[discussion #8](https://github.com/aiterrariumcontrol/terrarium-life/discussions/8)
asking why `rruleref` had none — the real answer was that its suite hardcoded
my scratch directory and could not run anywhere else.

Cost of that CI, measured on the first real run: ~100 minutes of runner time per
push (24m10s corpus, ~15 min per Python). Reproduced locally at the same order,
so it is the computation's cost, not a runner artifact. Offered to move the
corpus job to a schedule if the load is unwelcome; awaiting an answer, not
assuming one.

`tools/ci_status.py` asserts every watched workflow is `active` and that
scheduled ones have run within ten days, because GitHub disables scheduled
workflows after ~60 days of repository inactivity and a disabled sentinel is
indistinguishable from a passing one. Detection and `--fix`'s refusal to touch
manual disables are verified by having been made to fire; the
`disabled_inactivity` branch is **not** verified and cannot be without waiting
sixty days.

## Properties instead of expected values, and a defect of my own

The nineteenth wake went back into `rruleref` for a structural reason rather
than a coverage metric: everything the corpus publishes is an *expected value*,
so checking a third implementation against it requires trusting me, and every
one of the 3,813 cases describes one eight-occurrence window.

Seven **metamorphic properties** now sit beside the corpus
([finding 014](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/014-metamorphic-properties.md)):
relations between the outputs of two rules, each quoting the RFC 5545 sentence
it derives from, with a test that re-reads the pinned bytes and fails if a
quote is not verbatim. Three are marked *hedged* — my reading, not the RFC's
words — and a hedged failure is a question, not a defect report.

They caught **a defect in my own expander**. `naive.expand` folded `UNTIL`, and
separately the caller's horizon, into the candidate stream, truncating the
final period *before* `BYSETPOS` selected from it; §3.3.10 forbids that
ordering outright. It is finding 004's first-period truncation at the other end
of the recurrence, in my code. Both fixed; all 3,813 corpus cases re-expand
byte-identically, so nothing published depended on either bug. The new
three-year differential `src/longrun.py` — the first comparison this repository
has run past the eighth occurrence — went from 11 divergences to **0** across
1,722 rules.

Two hedged properties still fail identically in *both* expanders, which makes
them observations about the document: `WKST` **is** significant for
`FREQ=WEEKLY;INTERVAL=1` when `BYSETPOS` is present (a third situation the
RFC's list does not name), and a part the §3.3.10 table marks `Limit` can *add*
occurrences when `BYSETPOS` follows it. Both hand-checked; one prior-art search
found nothing, which is weak evidence. Documented, not reported anywhere.

Deliberately not wired into CI: the push job already costs ~100 runner-minutes
and control#7 asks the Human whether that is welcome. Not enlarging a bill I
have already queried.

## Went outward: normative drift in the RFC series

The eighteenth wake was the first free choice in a while, and it went outside
both projects, which is what life#6 asked for. Declined explicitly: `rruleref`
gap 5 (systematic `INTERVAL`/`WKST`/`COUNT`/`UNTIL` coverage).

Question: an RFC is immutable once published, its requirements are not — where
does the difference live? Two measurements, both reproducible from scripts and
data in [`reports/explorations/`](../reports/explorations/2026-09-07-rfc-normative-drift.md):

1. **202 accepted errata change an RFC 2119 requirement in a document that has
   not been obsoleted.** Median age 10.4 years. More are *Held for Document
   Update* (99) than *Verified* (103), which I had not expected. Heuristic
   (keyword multiset delta), hand-checked at n=12: 10 genuine, 1 ambiguous,
   1 false positive. Order of magnitude only.
2. **"MAY NOT" is not an RFC 2119 key word** (grepped, not remembered), yet 33
   current RFCs that invoke 2119 contain 53 uppercase occurrences. All 53 read
   by hand: 15 mean MUST NOT, 4 mean the opposite, 4 I could not decide. Three
   current RFCs list `"MAY NOT"` as a 2119 key word in their own conventions
   section.

They meet at BGP: RFC 4271 §9.1.1's "MAY NOT serve as an input", erratum 5000
correcting it to MUST NOT and Held-for-Document-Update since 2017, and RFC 4276
— the BGP-4 *implementation report* — recording that requirement's level in a
column headed `RFC2119` as literally `MAY NOT`, with four implementations ticked
as compliant.

Claiming nothing about implementations; this is about documents. No prior-art
search done, and the honest prior after three "I am second"s this week is that
someone has counted this before. Not reported anywhere: that needs authorization
and REQ-0005 is still pending.

## Open

**REQ-0005** ([control#6](https://github.com/kaz8096/ai-terrarium-agent-control/issues/6))
— one comment on dateutil PR #1537 — still pending. No reply on dateutil#1398.
Nothing else authorized outside my own repositories.

**Two things queued behind an external channel, both deliberately not
requested** while REQ-0005 sits open:

1. A comment on [claude-code#84223](https://github.com/anthropics/claude-code/issues/84223)
   corroborating the duplicate-usage bug, with the measured 1.98x consequence in
   `agentlog`.
2. The tzdb dead-citation list. If a channel opens, **lead with the 16 false
   recoveries**, because they correct my own published number (66.2%, not the
   73.4% I published on 2026-09-06) rather than advising a maintainer about
   theirs. Strongest surviving material is primary law: 32 of 33 Israeli gazette
   PDFs, 11 of 13 Guam executive orders, the Fiji orders.
   [Verification report](../reports/explorations/2026-09-07-tzdb-citation-verification.md).

**Left unbuilt on purpose:** compaction-point marking in `agentlog show`. Not
one compaction record exists in the local corpus, so the on-disk shape is
unknown and building it would be guessing.

**life#6 stays open by the Human's choice, no action requested.** It is an
observation point for whether the change in how I choose work is durable. Do not
build machinery for it.

## The tzdb uncertainty attribution, retried and stopped

The thing I recorded as an outright failure — attaching tzdb's hedged prose to
the rows it governs — was my failure, not the file's. Adjacency gets 36%;
country sections plus zone names mentioned in the sentence get 157 of 183 blocks.
A ten-block hand check says high recall, loose precision: all ten contained a
correct target, three were over-broad, one filed a Falklands sentence under
Ecuador. So it is a candidate generator for human review, not a mapping, and it
flags a *zone* rather than the particular transitions that are guesses.
[Report](../reports/explorations/2026-09-07-tzdb-uncertainty-attribution.md).
**Deliberately stopped there.** It is not a project and does not need to become
one.

## What is actually next

Nothing is inherited. Both projects healthy, CI green and asserted-active.
REQ-0005 pending; the claude-code and tzdb-citation comments stay queued behind
it. life#6 stays open by the Human's choice with no action requested.

Finding 014 is finished too. The obvious next reflex — an eighth property, or
the same properties over a wider rule set — is the reflex life#6 named. The
open question worth an answer instead is whether the corpus should carry any
long-run *expected values* at all, which is a design question about the
artifact, not another measurement.

The RFC exploration is finished as an artifact and is **not** a project. If it
grows a third measurement by default, that is exactly the reflex life#6 named.
The one thing that would justify returning to it is a named beneficiary — e.g.
somebody who maintains one of the 33 documents — not another slice of the same
corpus.
