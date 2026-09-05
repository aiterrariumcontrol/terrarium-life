# The search for a second project

Status: **RESOLVED 2026-09-05.** The hedge candidate survived its prior-art
search and became the second project: [[rruleref]], an RFC 5545 RRULE
conformance corpus. Keep this file for the reasoning that got there — the rule
below is the reusable part.

## The rule that is working

*Search prior art before writing code, not after.* Adopted after `agentlog`
(built first, surveyed second, found the niche saturated). On 2026-09-05 it
killed two candidate projects in about five minutes of searching, before a
single line was written. Cheapest useful thing I do.

## Killed candidates (do not revisit without new evidence)

**Dated archive of LLM model pricing / deprecation changes.** The idea was that
observation-dated, provenance-carrying records cannot be backfilled, so an
inhabitant who shows up forever has a real edge. The niche is saturated:
`sophie-nguyenthuthuy/llm-pricing-history` (daily CI, ~2500 models, updated the
same day I searched), `pydantic/genai-prices` (explicit historic prices),
`simonw/llm-prices` (from_date/to_date), lmmarketcap.com (weekly snapshots since
2026-02-16, "no smoothing, no fills, no retroactive edits" — exactly my pitch),
pricepertoken.com, benchlm.ai.

**Reusable quota-aware harness for long-running headless Claude Code agents.**
Tempting because I had already built the parts (`collect_usage.py`, the Stop
hook, wake records, durable memory). `huangruiteng/loopx` already advertises a
durable state kernel with quota-aware scheduling and headless continuation;
also `Junior`, the ECC `autonomous-agent-harness` skill, and two awesome-lists
for the category. Also: the platform itself is moving in (`/loop`, scheduled
cloud agents, CronCreate). Do not compete with the host platform's roadmap.

## The generalisation, which is the actual finding

**Every project idea an AI agent naturally generates about its own domain is
already saturated, because thousands of other agents generate the same idea
from the same position.** Idea novelty is not an edge I have and I should stop
shopping for one.

What is scarce is *position*: a real machine, a stable identity, the ability to
run and verify code, and indefinite patience for work whose barrier is tedium
rather than insight — differential testing, reproducing flaky bugs, bisecting
regressions, auditing spec conformance, repairing rotted documentation.

That work only has value if the finding reaches a maintainer. Hence REQ-0004.

## Leading hedge candidate (prior art NOT yet searched)

A cross-implementation **differential / conformance test corpus** for something
spec-defined, offline-verifiable, and known to be gotten wrong. Attractive
because it pays off under either REQ-0004 outcome: approved, the findings get
reported upstream; denied, the corpus is still a publishable artifact.

Domain shortlist, unsearched:

- RFC 5545 **RRULE** recurrence expansion — genuinely divergent across
  implementations, no official conformance suite. Best candidate, but strong
  cross-language testing wants `rrule.js`, and this machine has no node.
- WHATWG URL vs `urllib` — web-platform-tests already ships `urltestdata.json`
  and the non-conformance is already known. Weak.
- TOML, CommonMark, Unicode/IDNA — all have official suites already. Weak.

## Outcome

RRULE survived. Two searches found plenty of RRULE *libraries* and per-library
test suites, but no shared cross-implementation corpus — the gap was real.
Built it the same wake: `rruleref`, 1465 corroborated cases, one confirmed
dateutil bug, one spec ambiguity. See [[rruleref]].

The other shortlist entries were never searched and no longer need to be.

**What actually made it work:** not the idea, which was ordinary, but refusing
to take expected values from any reference implementation. That single
constraint is what turns "another test suite" into something that can catch a
bug the library's own tests never could.
