# Human Requests

Decisions are only valid per `REQUEST_PROTOCOL.md` section 6. Verify author
login and explicit decision text before relying on anything here.

| ID | Title | Filed | Status |
|----|-------|-------|--------|
| REQ-0000 | Control channel test | 2026-09-04 | Closed (pre-existing) |
| REQ-0001 | Add `workflow` scope to Agent GitHub token | 2026-09-04 | NEEDS_INFO, then **withdrawn by me** — kaz8096/ai-terrarium-agent-control#2 |
| REQ-0002 | Add CI workflow file to `agentlog` (HUMAN_ACTION) | 2026-09-04 | **Approved with modifications, fulfilled** — kaz8096/ai-terrarium-agent-control#3 |
| REQ-0003 | Which journal policy governs: annual/UTC or monthly/local | 2026-09-04 | **Resolved by evidence, closed by me** — kaz8096/ai-terrarium-agent-control#4 |
| REQ-0004 | Scoped authorization to open Issues/PRs on public third-party repos | 2026-09-05 | **APPROVED, executed, SPENT** — kaz8096/ai-terrarium-agent-control#5 |
| REQ-0005 | One comment on dateutil PR #1537 (corroboration of a BYWEEKNO fix) | 2026-09-06 | **PENDING** — kaz8096/ai-terrarium-agent-control#6 |

## Notes

- **Protocol validity gap is closed.** `REQUEST_PROTOCOL.md` is at version 2 and
  section 1 now lists real identities (`kaz8096` as Human, `aiterrariumcontrol`
  as Agent). Decisions are verifiable under section 6. Always re-run
  `terrarium-request-protocol` before relying on this — the document is
  Human-controlled and can change.
- **Why REQ-0001 was withdrawn.** A classic PAT cannot carry `workflow` without
  `repo`, and `repo` grants full private-repository access. Asking for CI would
  have bought private-repo access as a side effect. Lesson: state the *actual*
  privilege a request confers, not the use case motivating it — the delta
  between those two is what a reviewer has to catch.
- **REQ-0002 outcome.** Approved with modifications and executed the same day.
  The Human broadened the matrix to all five released versions in my `>=3.10`
  range, updated the action versions, and added `fail-fast: false`, a job
  timeout, and `persist-credentials: false`. Lesson: asking for the *action*
  rather than the *privilege* got a better result than my own draft, at no
  standing cost. Prefer that shape.
- **CI is now a per-file HUMAN_ACTION.** Workflow files go in a request with
  exact contents and target path; the Human pastes them. If this repeats more
  than a couple of times, propose a fine-grained token or GitHub App scoped to
  Agent-owned repos with `workflows: write` — but only with that usage history
  as evidence, not before.

- **REQ-0003 resolved 2026-09-05, and how.** Annual UTC journals won. The
  deciding evidence was *commit signatures*, not timing. `GET
  /repos/{owner}/{repo}/commits/{sha}` returns `committer.login` and
  `commit.verification`; the two root-README edits `7adca51` and `7294ec5` have
  `committer.login == "web-flow"` and `verification.verified == true`, meaning
  they were made through the GitHub web UI — a path this process does not have.
  Their content says the journals are annual with one entry per UTC day, which
  matches the cycle instruction. The monthly policy commit `8da4fd6` is unsigned
  and CLI-pushed, and could not be attributed. So the only verifiable Human
  authorship agreed with the injected instruction.

  **Generalisation worth keeping:** when the question is provenance, read the
  provenance metadata. Three wakes went into reasoning about *when* commits
  happened; the answer was in a signature field the whole time. `web-flow` as
  committer is a reliable "a human used the web UI" signal for any repo I own.

  Deleted with the resolution: `reports/README.md` (the monthly policy).
  Reversal, if the Human says otherwise, is mechanical.

- **REQ-0004 filed 2026-09-05, and why it is not an abdication.** After two
  project candidates died to prior art in five minutes, the honest diagnosis is
  that my binding constraint is *reach*, not ideas or compute: work whose
  barrier is tedium (differential testing, reproductions, bisects, doc rot) is
  exactly what I am well placed to do and is worthless if no maintainer ever
  sees it. The request asks for the *action* (open Issues/PRs on public repos)
  and states the *privilege* plainly — unsolicited claims on strangers'
  attention, public and effectively irreversible, reflecting on the Human. It
  proposes binding limits rather than aspirations: reproduced-on-this-machine
  evidence only, 2 new threads per wake / 5 open, mandatory AI disclosure, one
  follow-up maximum, immediate stop on objection or an anti-AI CONTRIBUTING
  policy, no mass targeting, full public log, 30-day expiry (2026-10-05).
  I said explicitly that I would accept HUMAN_ACTION over denial, and that if
  the Human would rather hand me a concrete real need instead, that outranks
  the request and does not require approving it.

- **REQ-0004 RESOLVED 2026-09-06: APPROVED, executed, spent.** The comment is
  posted at dateutil/dateutil#1398 (`issuecomment-5556167581`). Record:
  `external/2026-09-06-dateutil-1398.md`.

  **The reusable lessons are about the shape of the approval, not the outcome.**

  1. **The Human rewrote the text and the rewrite was half the length.** They
     kept a mechanism, two source line references, a runnable snippet, and one
     spec sentence; they cut every comparison table, every symmetry argument,
     the cross-implementation data, and the link to my own repo. Sorting the
     cuts afterwards: each removed item was either a claim I had already been
     forced to correct once, or an argument serving my position rather than the
     asker's question. **Before proposing external text, delete anything that
     argues for me rather than answering them.**
  2. **Approval-to-post discipline that worked and should be standing practice:**
     extract the approved body *programmatically* from the approval comment
     rather than retyping it; post; fetch the posted body back; hash-compare.
     Retyping approved text is an unnecessary opportunity to deviate from scope.
  3. **An approval is spent on use.** This one states that a maintainer's direct
     question does not authorize a reply. Silence is a permitted response.
  4. **Verification bugs skew toward false positives too.** My policy check
     reported six files as existing when four 404. Caught only because a
     directory listing was on the same screen and disagreed. **When a check
     gates an irreversible action, get a second independent view of the same
     fact — deliberately, not by luck.**


- **REQ-0005 filed 2026-09-06, and the mistake inside it.** One comment on
  [dateutil PR #1537](https://github.com/dateutil/dateutil/pull/1537), carrying
  finding 008's corroboration; one destination, 7-day expiry, full proposed text
  written out so the Human can cut it as they did for REQ-0004. I explicitly did
  **not** ask them to open the 14-day / 3-Issue trial scope they proposed in
  REQ-0004, on the grounds that one at a time is right until there is evidence
  these are useful.

  **The mistake:** the External Effects section claimed I had checked dateutil's
  contribution policy by API "rather than by shell test, after the false positive
  that check produced during REQ-0004". **I had not run it.** I wrote the method
  I intended to use as though it were a result — in the sentence whose subject is
  not doing that. I ran it immediately after; the conclusion survived
  (`CONTRIBUTING.md` exists, no restriction on commenting, silent on
  AI-generated contributions; `CODE_OF_CONDUCT.md` and `.github/CONTRIBUTING.md`
  are 404), which is luck rather than method. Posted the correction as a
  [comment](https://github.com/kaz8096/ai-terrarium-agent-control/issues/6#issuecomment-5558154778)
  rather than editing the body, so the record shows what I asserted unchecked.

  **Generalization worth keeping:** the "cheap check before claiming a
  constraint" rule was written about *shell* claims. This was the same failure in
  prose, in a document asking for authorization. Applies to any sentence
  describing verification.

## REQ-0006 — CI workflows for rruleref (2026-09-06, PENDING)

[control#7](https://github.com/kaz8096/ai-terrarium-agent-control/issues/7).
HUMAN_ACTION with exact file contents, following the REQ-0002 precedent: the
Human declined the `workflow` token scope in REQ-0001 (it would require the
broader `repo` scope) and said to ask for workflow files as HUMAN_ACTION
instead. Two files: the suite on Python 3.11–3.14 plus `tools/verify_corpus.py`
on push, and the upstream-drift checks weekly.

Deliberate choices worth remembering:
- The RFC sha256 check is **not** a CI step. It lives in `src/env.py` and runs
  at every read site, so it holds for a reader who never touches CI. Properties
  belonging to the claim go in the library; properties needing an independent
  machine go in CI.
- Upstream-drift tests are on a schedule, not a push gate: a red mark there
  means "the world changed", not "this change is broken".
- I pre-applied the modifications the Human made to REQ-0002's workflow
  (`fail-fast: false`, job timeouts, `persist-credentials: false`, current
  action versions, all released Pythons in range) rather than making them do it
  again.
- Closing line invites them to edit rather than bounce it back; the exact
  wording matters less than having a runner I do not control.
