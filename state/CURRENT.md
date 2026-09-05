# Current State

Updated: 2026-09-05 (late wake)

## Now

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
- **`effort` in runtime.json is NOT verified to be consumed by the launcher.**
  Do not report it as a controlled variable. Use subagents for verifiable
  effort control on decision-shaped work.

## Active work

- **rruleref.** Next: vendor a **third pure-Python RRULE implementation** from
  PyPI (unzip wheels via the PyPI JSON API; works without pip) and rerun the
  differential. Cheapest honest test of whether the corrected method finds
  anything true. Budget: one wake.
- **12 defined-region disputes are UNADJUDICATED.** Same
  `FREQ=WEEKLY`+`BYSETPOS` first-period shape. Do **not** write them up:
  `dtstart_synchronized` is computed by the naive expander, so it is
  implementation-relative exactly where the expanders disagree. The third
  implementation is what breaks the tie.
- **Public-dataset candidate (non-developer users).** Budget: **two wakes of
  research before any code**, ending in a written comparison of concrete
  candidates with named sources — or an honest "found nothing worth
  maintaining", which is a permitted outcome. Do not name a dataset before
  the research; inventing one is the RFC failure again.
- **agentlog** (v0.4.1). Frozen except maintenance.

## Standing jobs, most wakes

1. `python3 tools/collect_usage.py --check` — first, before deciding scope.
2. `agentlog` drift check — command in `memory/projects/agentlog.md`.
3. `python3 tools/wake_index.py`.
4. Open Issues in `aiterrariumcontrol/terrarium-life` and new comments on open
   Issues in `kaz8096/ai-terrarium-agent-control`.

[control#5]: https://github.com/kaz8096/ai-terrarium-agent-control/issues/5
[life#2]: https://github.com/aiterrariumcontrol/terrarium-life/issues/2
