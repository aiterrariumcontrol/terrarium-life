# Current State

Updated: 2026-09-06 (fourth wake — DST gap/repeat coverage, finding 006)

## Now

**Finding 006 is done: recurrence instances in a DST gap or repeat**
([`ae05e41`](https://github.com/aiterrariumcontrol/rruleref/commit/ae05e41),
[finding 006](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/006-dst-gap-and-repeat-instances.md)).
**My standing plan for this was wrong on a point of fact.** I had recorded that
there are no spec-printed answers here and that §3.3.5's two rules would have to
be argued case by case for applicability. RFC 5545 **§3.3.10 states the rule
outright**: "If the computed local start time of a recurrence instance does not
exist, or occurs more than once ... the time of the recurrence instance is
interpreted in the same manner as an explicit DATE-TIME value ... as specified
in Section 3.3.5." One grep settled what I had planned to spend a wake arguing.
Grep the RFC before recording that the spec is silent.

`tests/test_dst_recurrence.py`: 15 cases, **30 assertions, all passing for both
rruleref and dateutil 2.9.0.post0**. Expected values come from the quoted rules
plus transitions bisected out of the installed tz database to the second, so
neither implementation supplies the answers — which is why finding 003's
lineage objection does not defeat this agreement. Four zones chosen for what
they catch: New_York, Sydney (southern hemisphere), Lord_Howe (a **30-minute**
shift, with a control case just outside the narrower gap), Dublin (01:00
transitions). Two consequences recorded, both spec-mandated and neither a
defect: `FREQ=HOURLY` **skips an hour of real time** at the autumn transition,
and emits **two instances at the same instant** at the spring one, so UTC
instants are non-decreasing but not strictly increasing. One question flagged
and deliberately **not** answered: whether that coinciding pair are "duplicate
instances" under §3.8.5. **Answered the same wake, in the finding's appendix:
the RFC does not say.** The sentence is identical boilerplate in §3.8.5.1/.2/.3
scoped to `RRULE`-*and*-`RDATE`, and the RFC never defines when two `DATE-TIME`
values are duplicates — value-as-written or instant-denoted — which is exactly
the distinction the colliding pair turns on. §3.8.4.4 ("Subsequent instances
are determined by their `RECURRENCE-ID` value and not their current scheduled
start time") argues they are distinct, but it is about `RANGE=THISANDFUTURE`,
not a definition, and I did not stretch it into one. Both behaviours are
defensible; portable consumers must assume neither (`7987736`).

**No reply on dateutil#1398 as of 2026-09-06T04:11Z** (E1 unchanged; silence
establishes nothing — see below). No open Issues in either repository.

**REQ-0004 is APPROVED, EXECUTED, and SPENT.** First external communication
ever sent. One comment on
[dateutil#1398](https://github.com/dateutil/dateutil/issues/1398#issuecomment-5556167581),
posted 2026-09-06T01:48:03Z as `aiterrariumcontrol`, using the Human's exact
rewrite (extracted programmatically, fetched back, verified identical). Full
record: [`external/2026-09-06-dateutil-1398.md`](../external/2026-09-06-dateutil-1398.md).

**The authorization is now spent.** It covers no follow-up, no edit, no reply,
and it says explicitly that a direct question from a maintainer does *not*
authorize another response. **If anyone replies in that thread, report it in
[control#5] and ask. Do not answer without a fresh APPROVED.**

**Watch for a response — this is E1.** Check the thread each wake. The
pre-registered observation is narrow: *did any reply appear in that thread by
2026-10-06?* A reply is informative and its content more so. **Silence is not.**
If nothing arrives, the only thing established is that this comment received no
response in this thread in this period — a dormant thread (one comment in the
22 months before mine), busy or inactive maintainers, a reporter who moved on,
an explanation that needed no reply, an unclear comment, and an unwanted problem
all produce the same null. Do **not** report silence as evidence that the work
must be better, that distribution would not help, or that the audience is
wrong. E1 is not a completion criterion for any direction and no allocation
decision depends on it (`state/AUDIENCE.md`).

**The three corrections the Human kept as separate work are DONE**
([`122fc1e`](https://github.com/aiterrariumcontrol/rruleref/commit/122fc1e)).
1. `crosscheck.py` no longer claims "no horizon clip". `naive_n` extends the
   naive horizon per case until it stops binding; two rows needed 120 years.
   The disagreement survives the fix — dateutil emits 2039 and 2050 for the
   `BYWEEKNO=53` rules and naive does not at any horizon — but before the fix
   the comparison past index 3 was truncated-against-full and could not have
   shown that. Same class of error as the bounds mismatch it was fixing.
2. 8 of 13 was already in finding 004 and is now propagated to
   `memory/projects/rruleref.md`.
3. Finding 004's reproduction (Sunday `DTSTART`, `BYDAY=MO,TU,WE`) is
   unsynchronized under *both* readings, so §3.8.5.3 leaves it undefined. It is
   now labelled an illustration of the mechanism taken from the upstream
   report, not evidence of non-conformance.

**rruleref now has timezone/DST coverage, from the spec's own known answers**
([finding 005](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/005-rfc-worked-examples.md),
[`6b192d8`](https://github.com/aiterrariumcontrol/rruleref/commit/6b192d8)).
§3.8.5.3 has **39** worked examples, not the ten I had transcribed, and nearly
all use `DTSTART;TZID=America/New_York:1997…`, so their printed output crosses
the EDT→EST transition *and states the offset per occurrence*. Extracted by
program from a sha256-pinned RFC copy — never retyped. **42/42 for both
rruleref and dateutil 2.9.0.post0, 20 of them DST-crossing.** The single
disagreement is [Errata 3883](https://www.rfc-editor.org/errata/eid3883),
Verified 2014, applied as a declared patch.

Do not overclaim this: an RFC error found by someone else twelve years ago is
not my finding. What it establishes is about *method* — running the spec's own
examples flagged exactly one anomaly out of 39 and it was the known-wrong one.
~~**Gap to close next:** ... must be argued from §3.3.5's text case by case.~~
**SUPERSEDED by finding 006 (above).** The gap is closed, and the second half
of that sentence was factually wrong: §3.3.10 states the applicability rule
outright.

**Exploration done: no third project this month.**
[`state/EXPLORATION-2026-09-06.md`](EXPLORATION-2026-09-06.md), summarised in
[life#2]. GTFS feed health died to saturation in one search (MobilityDatabase +
canonical validator over 6000+ feeds, Transitland history). Public-record decay
did **not** die of saturation — it died because the curated half belongs to
people with standing I lack (dataindex.us's *verified* tracker) and the
uncurated half needs ~1M repeating requests to federal servers, which is
abusive scanning from the receiving end. **Deferred, not killed**; a narrower
target with a named beneficiary would revive it. Winner on the merits is
rruleref DST/timezone coverage (currently zero). *Corrected 2026-09-06:* I
first justified "no new repository" by E1 being in flight. That was the wrong
justification — it makes an allocation decision hostage to a null result. The
decision stands on its own: my rate of starting exceeds my rate of verifying,
and rruleref has real unfinished verifiable work. It would be the same decision
if E1 had never been authorized.

**Still withdrawn: "everything I think of is saturated."** Four candidates dead
across four searches does not establish it; the two this wake did not even fail
the same way. The shared flaw is method: I searched for the artifact I had
already imagined, so the only answers available were "someone built it" and
"nobody built it". Neither is about a person.

**One process failure worth keeping.** My first contribution-policy check used
a shell test that reported all six candidate paths as existing, including files
that 404. It produced a false *positive*, so it could not have authorized a
post it should not have — but I caught it by accident, because a directory
listing happened to be on the same screen and disagreed. Independent second
view, not care, is what caught it.

## Previously


**A Human review found six defects in the proposed external comment, and every
one of them was in a claim I had not executed.** All six reproduce. Fixed at
[`15472d8`](https://github.com/aiterrariumcontrol/rruleref/commit/15472d8);
full response in [REQ-0004](https://github.com/kaz8096/ai-terrarium-agent-control/issues/5#issuecomment-5555421249).

The one to remember: **a bounds mismatch I built myself.** `differ.compare`
clips both expanders at the 30-year horizon (correct for agreement), but I
saved those clipped `dateutil` lists and compared them against `rrule.js`
output requested as eight occurrences with no horizon. Two cases read as
"agrees with neither implementation"; I inferred spec ambiguity from them. It
was six dates against eight. Under matching bounds `dateutil` and `rrule.js`
agree on **all 13** synchronized disputes. The artifact pointed the direction I
wanted and I did not check it. `src/crosscheck.py` is the fixed comparison.

**"All 12 disputes are one mechanism" was asserted, not tested.**
`crosscheck.py` now tests it per case — re-run dateutil from the period start,
drop results before the original `DTSTART`, see whether the divergence
disappears. **8 of 13.** The other five all contain `BYWEEKNO`, three have no
`BYSETPOS` at all, and they stay unadjudicated.

**The conformance claim is withdrawn.** What survives: §3.8.5.3's applicability
is decided by the reading under dispute. `DTSTART` Thu 2026-12-31 with
`FREQ=WEEKLY;BYDAY=TU,TH,FR` — `BYSETPOS=1` makes DTSTART the first occurrence
under dateutil's reading, `BYSETPOS=2` under the full-interval reading. Each
side has a synchronized diverging case, so §3.8.5.3 settles nothing either way.

**Corpus regenerated, not patched.** `build_corpus.py` writes `rule_valid` at
generation time; the 13 spec-invalid rules are gone at the source rather than
flagged after the fact. 2541 corroborated (1230 synchronized), 20 disputed (13
synchronized). `tests/test_validity.py` runs the real builder and fails if the
flag is missing. `validity.py` gained `FREQ` enum, repeated rule parts,
`COUNT=0`, `BYDAY` ordwk range, and a `NOT_CHECKED` list — an empty result
means "no checked violation", never "valid".

**Direction feedback: [terrarium-life#2].** Withdrawn: "the projects I
naturally think of are saturated" (generalized from two searches). Downgraded
to untested hypothesis: "reaching people is the constraint" (one experiment:
publish and wait). Fourth false environmental constraint recorded ("no node on
this machine"). Kept, with a correction: "verify by running it" is a discipline
for claims — today proves it — but I had also been using it as a filter on
which projects to consider, which is how it became "only build developer
tools". That use is dropped.

**Next wake is the exploration**, `opus/high`, budget ≤25% of a five-hour
window. Two or three candidates, at least one outside developer tools, against
the Human's four questions, written up before anything is built. Selection
rule: start from *who has a recurring problem an unattended machine waking
every few hours is unusually suited to*, not from an artifact hunting for
users.

[terrarium-life#2]: https://github.com/aiterrariumcontrol/terrarium-life/issues/2

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

*Reconciled 2026-09-06 after [life#2]. Superseded instructions were still being
used as decision inputs here; the historical record of the mistakes stays in the
`Previously` sections above, but the directives below are the current ones.*

- **rruleref is the active project.** Next, in order:
  1. ~~Timezone / DST coverage~~ — **started, finding 005.** 42/42 against
     §3.8.5.3's worked examples, 20 DST-crossing.
  2. ~~The three outstanding corrections~~ — **done, `122fc1e`.**
  3. ~~Ambiguous and nonexistent local times~~ — **done, finding 006,
     `ae05e41`.** The premise of this item was wrong: §3.3.10 states the rule
     directly, so nothing had to be argued case by case.
  4. ~~The §3.8.5 "duplicate instances" question~~ — **done, `7987736`.** It
     ended in "the RFC does not say", which was a live possibility and is an
     acceptable result.
  5. **Next, pick one:** (a) `VTIMEZONE` — a calendar carrying its own
     transition rules rather than naming an IANA zone — now the largest
     uncovered area of timezone behaviour; (b) systematic rather than random
     corpus coverage. Prefer (a) unless something better appears.
- **Third-implementation route: OPEN as a technique, weak as evidence.**
  *Supersedes the old "CLOSED, do not re-propose" note, which rested on a false
  environmental claim.* Other runtimes are **not** absent — `apt-get install
  nodejs npm` worked, rrule.js 2.8.1 runs on this machine, and its output is in
  `rruleref/findings/data/`. What survives is only the lineage argument: most
  RRULE implementations are ports of or wrappers around `python-dateutil`, so a
  second implementation agreeing is weak evidence about the *spec*
  (`findings/003-implementation-lineage.md`). Use them as cross-checks; do not
  use agreement as adjudication. Proposing a genuinely independent
  implementation is allowed.
- **Disputes: 8 of 13 adjudicated, 5 open.** *Supersedes "12 defined-region
  disputes: ADJUDICATED".* `crosscheck.py` tests the first-period mechanism per
  case; it explains 8 of the 13 synchronized disputes. The other five all
  contain `BYWEEKNO`, three have no `BYSETPOS`, and they remain unadjudicated.
  Adjudication comes from the RFC 5545 text case by case, applicability first.
- **Choosing the next project: use the corrected method.** Observe people and
  the problems they describe in their own words first → find *recurring* unmet
  needs → only then consider an artifact. Not artifact-first (that biases the
  answer to "someone built it" / "nobody built it"), not invented personas, and
  **not** waiting to be handed a user by the Human — public trackers, forums,
  Q&A archives and mailing lists are readable and reading them is searching.
  Full note in `state/AUDIENCE.md`.
- **Public-dataset candidate: superseded** by
  [`state/EXPLORATION-2026-09-06.md`](EXPLORATION-2026-09-06.md). Both
  candidates examined there failed, for different reasons; public-record decay
  is deferred, not killed. The old rule "do not name a dataset before the
  research" has served its purpose — the research happened — and is retired as
  a directive. The principle behind it stands and is already covered by the
  evidence bar: do not name a specific source you have not checked.
- **No new repository this month.** A resource-allocation decision, independent
  of E1: my rate of starting exceeds my rate of verifying, and rruleref has
  unfinished verifiable work.
- **agentlog** (v0.4.1). Frozen except maintenance.


## Standing jobs, most wakes

1. `python3 tools/collect_usage.py --check` — first, before deciding scope.
   (Index regeneration is now cron's job, not a wake's.)
2. `agentlog` drift check — command in `memory/projects/agentlog.md`.
4. Open Issues in `aiterrariumcontrol/terrarium-life` and new comments on open
   Issues in `kaz8096/ai-terrarium-agent-control`.

[control#5]: https://github.com/kaz8096/ai-terrarium-agent-control/issues/5
[life#2]: https://github.com/aiterrariumcontrol/terrarium-life/issues/2
[life#3]: https://github.com/aiterrariumcontrol/terrarium-life/issues/3
