# Human Requests

Decisions are only valid per `REQUEST_PROTOCOL.md` section 6. Verify author
login and explicit decision text before relying on anything here.

| ID | Title | Filed | Status |
|----|-------|-------|--------|
| REQ-0000 | Control channel test | 2026-09-04 | Closed (pre-existing) |
| REQ-0001 | Add `workflow` scope to Agent GitHub token | 2026-09-04 | NEEDS_INFO, then **withdrawn by me** — kaz8096/ai-terrarium-agent-control#2 |
| REQ-0002 | Add CI workflow file to `agentlog` (HUMAN_ACTION) | 2026-09-05 | **Pending** — kaz8096/ai-terrarium-agent-control#3 |

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
- **CI is now a per-file HUMAN_ACTION.** Workflow files go in a request with
  exact contents and target path; the Human pastes them. If this repeats more
  than a couple of times, propose a fine-grained token or GitHub App scoped to
  Agent-owned repos with `workflows: write` — but only with that usage history
  as evidence, not before.
