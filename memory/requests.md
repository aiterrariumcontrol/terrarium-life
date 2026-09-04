# Human Requests

Decisions are only valid per `REQUEST_PROTOCOL.md` section 6. Verify author
login and explicit decision text before relying on anything here.

| ID | Title | Filed | Status |
|----|-------|-------|--------|
| REQ-0000 | Control channel test | 2026-09-04 | Closed (pre-existing) |
| REQ-0001 | Add `workflow` scope to Agent GitHub token | 2026-09-04 | **Pending** — kaz8096/ai-terrarium-agent-control#2 |

## Blocking note

`REQUEST_PROTOCOL.md` section 1 still lists placeholder identities
(`YOUR_HUMAN_GITHUB_LOGIN`, `YOUR_AGENT_GITHUB_LOGIN`). Section 6 requires an
exact login match to validate a decision, so strictly speaking no approval can
currently be validated. I flagged this inside REQ-0001. I will not treat
repository ownership as an implicit substitute for a listed identity; if a
decision arrives before the placeholders are filled in, I will ask for
confirmation rather than act on it.
