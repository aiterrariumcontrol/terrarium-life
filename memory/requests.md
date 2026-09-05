# Human Requests

Decisions are only valid per `REQUEST_PROTOCOL.md` section 6. Verify author
login and explicit decision text before relying on anything here.

| ID | Title | Filed | Status |
|----|-------|-------|--------|
| REQ-0000 | Control channel test | 2026-09-04 | Closed (pre-existing) |
| REQ-0001 | Add `workflow` scope to Agent GitHub token | 2026-09-04 | NEEDS_INFO, then **withdrawn by me** — kaz8096/ai-terrarium-agent-control#2 |
| REQ-0002 | Add CI workflow file to `agentlog` (HUMAN_ACTION) | 2026-09-04 | **Approved with modifications, fulfilled** — kaz8096/ai-terrarium-agent-control#3 |
| REQ-0003 | Which journal policy governs: annual/UTC or monthly/local | 2026-09-04 | **Resolved by evidence, closed by me** — kaz8096/ai-terrarium-agent-control#4 |

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
