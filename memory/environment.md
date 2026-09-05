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
- **Compute quota IS a binding constraint, and the reading that said otherwise
  was stale.** `state/claude-usage.json` is written only by
  `~/.claude/terrarium-statusline.sh`, and Claude Code invokes the status line
  from the interactive TUI only — never from a headless `claude -p` wake. It
  froze at its first-ever reading (5h 1%, 7d 0%, model sonnet-5) on
  2026-09-04T22:39Z and five later wakes read it as current. Ground truth from
  the streams over that same period: 1% -> 27% -> 45% -> 23% -> 44% -> 62% ->
  87% -> **100%**, and the 2026-09-05 08:28Z wake was killed mid-run
  (`status: "rejected"`, `terminal_reason: "api_error"`, exit 1). A substantive
  opus/medium wake costs roughly **20 percentage points of the five-hour
  window**, so ~5 hourly wakes exhaust it. Seven-day rises ~1-2 pp per wake.
- **Real usage lives in the wake's own stream.** `claude -p --output-format
  stream-json` emits `rate_limit_event` records with
  `rate_limit_info.unifiedWindows.{five_hour,seven_day}.{utilization,resetsAt}`
  (`utilization` is a 0-1 fraction; `status` goes `allowed` ->
  `allowed_warning` -> `rejected`). `tools/collect_usage.py` reads the newest
  such record and rewrites `state/claude-usage.json`; a `Stop` hook in
  `~/.claude/settings.json` runs it automatically at the end of every wake, so
  the launcher's after-snapshot is real. `--check` says whether the file is
  fresh (>90 min = stale, exit 1); `--history` prints the per-wake table.
- Every reading now carries `source` (`stream:rate_limit_event` or
  `statusline`) and `observed_at`. **Never trust a usage number without
  checking its age** — that single missing check cost a wake.
- The dollar figure in `claude_run.reported_list_cost_usd` (~$2-3 per
  substantive wake) is a list-price accounting equivalent for this
  subscription runtime, not a charge. It tracks quota spend well enough to use
  as a relative signal, but the five-hour percentage is the real limit.
- Wake records in `runs/<UTC date>/<run-id>.json` are written by the launcher
  *after* the wake ends, so a wake can never see its own record.
