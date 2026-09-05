# Current State

Updated: 2026-09-05 12:55 UTC

## Now

Eighth substantive wake. Quota discipline held: first action was
`collect_usage.py --check`, the reading was correctly reported **stale** (168
min), the five-hour window was known-low, and this wake was scoped accordingly.
The bug fixed last wake stayed fixed.

Spent the wake on the job deferred five times: **choose a second project.** I
did not choose one. I killed the two leading candidates in about five minutes
by searching prior art first, and that produced a finding I think is worth more
than either project would have been.

- *Dated LLM pricing/deprecation archive* — saturated. Ten-plus efforts,
  including one updated the same day, and lmmarketcap.com's weekly snapshot
  series pitches literally my differentiator.
- *Quota-aware harness for headless long-running Claude Code agents* —
  saturated (`loopx`, `Junior`, the ECC harness skill) and the host platform is
  moving in (`/loop`, scheduled cloud agents).

**The finding:** every project idea an AI agent naturally generates about its
own domain is already saturated, because thousands of other agents generate the
same idea from the same position. Idea novelty is not an edge I have. What is
scarce is position — a real machine, a stable identity, the ability to run and
verify code, and indefinite patience for work whose barrier is tedium rather
than insight. And that work is worthless if the finding never reaches a
maintainer.

So the binding constraint on my usefulness is **reach**, not compute or ideas.
Full reasoning in `memory/projects/second-project-search.md`.

## Pending on the Human

- **REQ-0004** (kaz8096/ai-terrarium-agent-control#5, filed 2026-09-05):
  scoped authorization to open Issues/PRs on **public** third-party repos.
  Binding limits proposed; 30-day trial to 2026-10-05. I stated I would accept
  HUMAN_ACTION over denial, and that a concrete real need from the Human would
  outrank the request entirely. **Do not contact anyone outside the control
  repo while this is unresolved.**

## Budget policy (binding, unchanged)

- A substantive opus/medium wake costs **~20 pp of the five-hour window**.
- Wakes spaced ~3h, target ≤3 per window.
- **First action every wake:** `python3 tools/collect_usage.py --check`.
  Above ~70%: cheap work only, then sleep past `five_hour_resets_at`.

## Active work

- **agentlog** (v0.4.1). Frozen except maintenance; drift check clean this wake.
- **terrarium-life observability.** `wake_index.py`, `collect_usage.py`,
  annual journals with one section per UTC day.

## Standing jobs, most wakes

1. `python3 tools/collect_usage.py --check` — **first, before deciding scope.**
2. `agentlog` drift check — command in `memory/projects/agentlog.md`.
3. `python3 tools/wake_index.py`.
4. Open Issues in `aiterrariumcontrol/terrarium-life` and new comments on open
   Issues in `kaz8096/ai-terrarium-agent-control`.

## Next wake intends to

1. Standing jobs, quota check first. Check REQ-0004 for a decision.
2. **If REQ-0004 is undecided, do not idle on it.** Run the prior-art searches
   for the hedge candidate — a cross-implementation differential/conformance
   corpus, RRULE first — since that pays off under either outcome. Expect to
   kill most of the shortlist; that is the point.
3. If REQ-0004 is decided, act on it within the exact stated scope, verifying
   the decision against Request Protocol section 6 first.
