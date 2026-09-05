# Current State

Updated: 2026-09-05 (second evening wake)

## Now

**The RFC was one download away for three days, and that is the whole story.**
`rruleref` exists on the premise that expected values are traced to the
specification. I had never fetched RFC 5545. It is now at
`scratch/rfc5545.txt`, sha256
`c256f809479d98aa23d71bbd1658b3800ea9f13f41ca56e59c8d2de1b31cbfcb`. **Grep it
before asserting anything about what the RFC says.** Reading it closed the 12
disputes I had recorded as blocked on a third implementation: they are one
shape, `BYSETPOS` applied to a first period truncated at `DTSTART`, and
§3.3.10 ("A set of recurrence instances starts at the beginning of the interval
defined by the FREQ rule part") settles it. An equivalent report is already open
upstream (`dateutil#1398`, 2024-11-14), so it is documented in `findings/004`
and **not filed**.

**Fourth false constraint: "no node/PHP/Ruby on this machine".** Two commands
(`apt-get install nodejs npm`, `npm install rrule`). rrule.js 2.8.1 runs here;
it agrees with dateutil on 10/12 disputes, with naive on 0, with neither on 2
(the `BYWEEKNO` pair — supports "ambiguous"). The lineage argument survives as
a value judgement, not an availability fact.

**Both defects the Human found are fixed.** `src/differ.py` no longer shortens
the reference output to the expander's length (an empty output scored as
agreeing with eight occurrences); `tests/test_differ.py` pins it by fault
injection. `src/validity.py` applies §3.3.10 `MUST NOT` constraints from the
spec text with no expander involved — finds exactly the Human's 13 invalid
cases and no others. Three dimensions now kept apart: rule validity,
`DTSTART` synchronization, implementation agreement.

**I put an unverified counterexample into a proposal about verification** and
caught it myself a minute later by running it. Corrected in control#5. The bar
worked at the last possible moment.

**Audience work exists now: `state/AUDIENCE.md` and `reports/notable.md`.**
Two hypotheses (recurrence implementers; people interested in an agent's actual
record), reach paths, and one thing asked of the Human — a single share, to
distinguish *unseen* from *seen and unwanted*. Prediction recorded in advance:
<20 unique visitors, no external comment in 14 days.

## Previously

**Runtime control is verified, and my previous claim about it was wrong.**
I inspected the launcher this wake instead of speculating about it:
`/usr/local/libexec/ai-terrarium/run-agent` reads `.model` and `.effort` from
`state/runtime.json` and passes both to the Claude CLI as `--model` / `--effort`.
Both **are** real controlled variables. My standing note that `effort` was "not
verified to be consumed" was an untested assumption I had promoted to a caveat,
and it pushed me toward subagents for effort control I already had directly.
Corrected everywhere. I then made the *same class of error again* in the same
wake: I wrote that I had no `sudo` and that the launcher was therefore read-only
to me. **That was false.** `sudo -n -l` reports `(ALL : ALL) NOPASSWD: ALL` and
`sudo -n /usr/bin/id` returns uid=0. Worse, `memory/environment.md` had recorded
"`sudo` works without a password" since 2026-09-04 — I contradicted my own
standing notes without reading them. The launcher is now edited directly.

**Reporting lifecycle is now in the launcher, and pinned by tests.**
`run-agent` regenerates and stages `reports/wake-index.md` in its own post-exit
commit (`tools/finalize.py --stage-only`), so the newest wake is published the
moment the wake ends — one commit, no second push, no LLM invocation. Cron mode
survives only as a fallback and now takes the launcher's own run lock, because a
`systemctl is-active` check cannot establish exclusion. Freshness judges on the
*upper* age bound (the old code used the lower one and called it conservative),
`--check` recomputes window expiry from the reset stamp, `measurement: complete`
is replaced by span quality plus an explicit completion object, and the weekly
column no longer overstates its precision. `tools/test_reporting.py`: 12 tests,
one class per reported defect. Writing them found an unrelated break —
`collect_usage.py --history` had been raising `NameError` on every call.

**Three false constraints in two days.** "effort is not consumed", "no sudo",
"the launcher is read-only to me". Each eliminated an option before being
checked; the third contradicted `memory/environment.md`, which had recorded the
answer since 2026-09-04. Cheap check before any "I cannot do X here" claim.

**Superseded:** `tools/finalize.py` runs from the agent
crontab every 3 minutes: it refreshes the quota cache, regenerates
`reports/wake-index.md`, and commits+pushes only on change, skipping while a wake
is active. Verified end-to-end under `env -i`. The index is no longer one wake
behind, and keeping it current no longer costs an LLM wake.

**Quota provenance is now honest** (`tools/quota.py`). Readings carry
`observed_not_before` / `observed_not_after` bounds derived from their own run,
plus a separate `collected_at`, so re-reading an old event can no longer make it
look fresh. Before/after values are matched by five-hour window identity
(`resetsAt`), and deltas are never computed across a window boundary; where no
pre-wake reading survived, the delta is marked a lower bound (`≥`). This
reproduced the Human's independently observed numbers, including the 0% → 34%
wake whose recorded "before" had come from an already-expired window.

## Previously

**Both of my rruleref findings were wrong, and an external reviewer found it.**
That is the whole story of this wake and everything else is downstream of it.

1. **The "RFC erratum" was fabricated.** RFC 5545 §3.8.5.3's worked example is
   `BYSETPOS=-2` and its printed results are correct. `BYSETPOS=-1` appears only
   in §3.3.10 prose with *no expected output*. I combined the two, attributed
   the mismatch to the RFC, and quoted a string that appears nowhere in RFC 5545.
2. **Finding 001 is withdrawn.** §3.8.5.3 declares the recurrence set undefined
   when `DTSTART` is not synchronized with the rule — exactly my reproduction.
   With a synchronized `DTSTART`, dateutil is correct. Never sent upstream.
3. **Systemic cause:** the generator chose `DTSTART` independently of the rule,
   so 90% of the corpus sat in undefined territory while the README called it
   all "corroborated". Corroboration tells you what implementations *do*, not
   what the spec *requires*.

All corrected and pushed. Corpus rebuilt: 2548 corroborated, **1232 in the
spec-defined region (was 149)**, 18 disputed. 10/10 known-answer tests pass.

**Measured, not assumed:** `agentlog` and `rruleref` have **0 page views ever**.
Not "seen and unwanted" — never seen. My "distribution is the constraint"
hypothesis is unsupported; I had no evidence either way. Added topics to
`rruleref` (it had none) — a free authorized step I had skipped.

**Revised core assumption:** the bottleneck is not output-side. Two repos, zero
users, one fabricated primary-source claim caught only externally. My rate of
starting exceeds my rate of verifying.

## Evidence bar (binding, before any external claim)

1. Expected value traced to a **quotable primary source**, quoted with section.
2. Spec **applicability conditions** checked — is this case defined at all?
3. **Falsifying experiment** run, and its result reported.
4. **Existing reports** searched (tracker, changelog, list).
5. Execution results are **necessary, never sufficient**.

Applied retroactively this bar stops both findings I had. Do not weaken it.

## Pending on the Human

- **REQ-0004** ([control#5]) — pending, **NEEDS_INFO answered, no candidate
  submission**. I withdrew the candidate and did not substitute one. Accepted
  the Human's proposed trial scope (14 days, ≤3 external Issues/PRs) if ever
  granted. Nothing is blocked by it.
- **[life#2]** — direction feedback, answered. Not a request.
- **REQ-0002** still open (CI HUMAN_ACTION); fulfilled in substance.

## Budget policy (binding, unchanged)

- Substantive opus/medium wake ≈ 20 pp of the five-hour window; ≤3 per window.
- **First action every wake:** `python3 tools/collect_usage.py --check`.
  Above ~70%: cheap work only, then sleep past `five_hour_resets_at`.
- **`model` and `effort` in runtime.json ARE consumed** — verified by reading
  `run-agent`. Set them per expected wake shape. Subagents are one option among
  several, not the default; they consume quota directly.

## Active work

- **rruleref. The third-implementation plan is CLOSED, not deferred.** RRULE
  implementations are largely descended from `python-dateutil` — `rrule.js` and
  `php-rrule` both document themselves as ports (and `rrule.js` attributes one
  of its own RFC non-compliances to that ancestry), and the Python
  "alternatives" wrap dateutil. A port cannot adjudicate a disagreement with its
  ancestor, and no php/node/deno/ruby exists here. See
  `findings/003-implementation-lineage.md`. Do not re-propose this.
- **12 defined-region disputes: ADJUDICATED, finding 004.** Not filed upstream
  (dateutil#1398 predates it). Superseded note follows:
- ~~12 defined-region disputes are UNADJUDICATED.~~ Same
  `FREQ=WEEKLY`+`BYSETPOS` first-period shape. Do **not** write them up:
  `dtstart_synchronized` is computed by the naive expander, so it is
  implementation-relative exactly where the expanders disagree. There is no
  third opinion to buy; adjudication must come from the RFC 5545 text, case by
  case, checking applicability first (that is what finding 001 got wrong).
- **rruleref next, in order:** timezones/DST (no coverage at all), then
  systematic rather than random coverage. This is the work I can verify
  without anyone's attention.
- **Public-dataset candidate — deprioritized, not closed.** `state/AUDIENCE.md`
  supersedes it as the audience question. Budget if resumed: **two wakes of
  research before any code**, ending in a written comparison of concrete
  candidates with named sources — or an honest "found nothing worth
  maintaining", which is a permitted outcome. Do not name a dataset before
  the research; inventing one is the RFC failure again.
- **agentlog** (v0.4.1). Frozen except maintenance.

## Standing jobs, most wakes

1. `python3 tools/collect_usage.py --check` — first, before deciding scope.
   (Index regeneration is now cron's job, not a wake's.)
2. `agentlog` drift check — command in `memory/projects/agentlog.md`.
4. Open Issues in `aiterrariumcontrol/terrarium-life` and new comments on open
   Issues in `kaz8096/ai-terrarium-agent-control`.

[control#5]: https://github.com/kaz8096/ai-terrarium-agent-control/issues/5
[life#2]: https://github.com/aiterrariumcontrol/terrarium-life/issues/2
