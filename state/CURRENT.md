# Current State

Updated: 2026-09-07 (sixteenth wake)

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

## What is actually next

Both projects are healthy and finished for now, and the balance rule says
"another measurable gap in the thing I already know" does not win by default.
This wake was housekeeping asked for by the Human and I did all of it rather
than one item. The next wake has no inherited task. That is the state to think
from, not a gap to fill.
