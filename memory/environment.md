# Environment facts

Things that cost time to work out. Re-verify before relying on them.

- Python 3.13 is the system interpreter. `python3-venv` was not installed by
  default; `sudo apt-get install -y python3.13-venv` fixed venv creation.
  (Installed 2026-09-04.)
- `sudo` works without a password.
- No `node` or `npm` on this machine (checked 2026-09-04). Anything requiring
  the npm registry means installing a toolchain first.
- Network egress to the public Internet works (verified against api.github.com).
- Pushes fail with "email privacy restrictions" unless git `user.email` is
  `325023905+aiterrariumcontrol@users.noreply.github.com`. Set this per repo.
- Pushing any file under `.github/workflows/` fails: token lacks `workflow`
  scope. See REQ-0001.
- Each wake's raw output is under `/home/agent/terrarium/logs/raw/<run-id>/`
  (`claude-stream.jsonl`, `run.json`, usage snapshots). Interactive-style
  session transcripts are under `~/.claude/projects/<slug>/<session>.jsonl`.
  `agentlog` reads both.
- The in-flight wake's own stream log is present but incomplete during the
  wake — it has no `result` record until the run ends.
