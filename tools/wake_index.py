#!/usr/bin/env python3
"""Regenerate reports/wake-index.md from the machine-readable records in runs/.

Every wake leaves a JSON record under runs/<UTC date>/<run-id>.json, written by
the runtime launcher *after* the wake ends. This script turns that pile into one
table a Human can read at a glance. Because the launcher writes the record after
the wake finishes, the newest wake is normally missing from the table until the
next one regenerates it.

Nothing here estimates or fills in a missing value: a field the record does not
contain is printed as an em dash.

Usage: python3 tools/wake_index.py [--check]
  --check  exit 1 if the file on disk differs from what would be generated
"""

import json
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"
OUT = ROOT / "reports" / "wake-index.md"
RAW = pathlib.Path.home() / "terrarium" / "logs" / "raw"

DASH = "—"


def five_hour_quota():
    """run_id -> five-hour window utilisation (%) at the END of that wake.

    Taken from the wake's own stream log, which is the only trustworthy source:
    `state/claude-usage.json` is written by the interactive status line and does
    not refresh during headless wakes. Machine-local, so a run whose stream log
    is gone simply gets an em dash — the committed table keeps whatever was
    resolvable when it was last generated.
    """
    out = {}
    for stream in RAW.glob("*/claude-stream.jsonl"):
        last = None
        try:
            with stream.open(encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if '"rate_limit_event"' not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    windows = (rec.get("rate_limit_info") or {}).get("unifiedWindows") or {}
                    util = (windows.get("five_hour") or {}).get("utilization")
                    if isinstance(util, (int, float)):
                        last = util
        except OSError:
            continue
        if last is not None:
            out[stream.parent.name] = round(last * 100)
    return out


def load_runs():
    for path in sorted(RUNS.glob("*/*.json")):
        try:
            yield path, json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"warning: skipping {path}: {exc}", file=sys.stderr)


def duration(rec):
    """Wall-clock wake length, from the launcher's own start/end stamps."""
    try:
        start = datetime.fromisoformat(rec["started_at"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(rec["ended_at"].replace("Z", "+00:00"))
    except (KeyError, ValueError, AttributeError):
        return None
    return (end - start).total_seconds()


def fmt_duration(seconds):
    if seconds is None:
        return DASH
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}m{secs:02d}s" if minutes else f"{secs}s"


def fmt_tokens(n):
    if n is None:
        return DASH
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}k"
    return str(n)


def totals_from(rec):
    """Return (list_cost, total_tokens, turns) — any of them None if unrecorded.

    Only records carrying `claude_run` (added to the launcher partway through
    2026-09-05 UTC) have these at all; earlier wakes report nothing.
    """
    run = rec.get("claude_run")
    if not isinstance(run, dict):
        return None, None, None
    usage = run.get("usage") or {}
    fields = (
        "input_tokens",
        "output_tokens",
        "cache_creation_input_tokens",
        "cache_read_input_tokens",
    )
    counted = [usage[f] for f in fields if isinstance(usage.get(f), int)]
    return (
        run.get("reported_list_cost_usd"),
        sum(counted) if counted else None,
        run.get("num_turns"),
    )


def render():
    quota = five_hour_quota()
    rows = []
    cost_sum = 0.0
    cost_n = 0
    token_sum = 0
    for path, rec in load_runs():
        cost, tokens, turns = totals_from(rec)
        if isinstance(cost, (int, float)):
            cost_sum += cost
            cost_n += 1
        if isinstance(tokens, int):
            token_sum += tokens
        rel = "../" + path.relative_to(ROOT).as_posix()  # links resolve from reports/
        run_id = rec.get("run_id", path.stem)
        model = rec.get("model", DASH)
        effort = rec.get("effort", DASH)
        status = rec.get("exit_status")
        used = quota.get(run_id)
        rows.append(
            "| [`{id}`]({rel}) | {start} | {dur} | {model}/{effort} | {turns} | "
            "{tokens} | {cost} | {quota} | {status} |".format(
                id=run_id,
                rel=rel,
                start=rec.get("started_at", DASH),
                dur=fmt_duration(duration(rec)),
                model=model,
                effort=effort,
                turns=turns if turns is not None else DASH,
                tokens=fmt_tokens(tokens),
                cost=f"${cost:.4f}" if isinstance(cost, (int, float)) else DASH,
                quota=f"{used}%" if used is not None else DASH,
                status="ok" if status == 0 else f"**exit {status}**",
            )
        )

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cost_line = (
        f"${cost_sum:.4f} across {cost_n}/{len(rows)} wakes "
        f"(mean ${cost_sum / cost_n:.4f})"
        if cost_n
        else "not reported by any wake"
    )
    return "\n".join(
        [
            "# Wake index",
            "",
            "Every wake, mechanically. Generated by [`tools/wake_index.py`](../tools/wake_index.py)",
            f"from the records in [`runs/`](../runs/); last regenerated {generated}.",
            "",
            "The launcher writes a wake's record *after* that wake ends, so the most",
            "recent wake is normally absent here until the following one rebuilds the",
            "table. A value the record does not contain is shown as an em dash rather",
            "than guessed.",
            "",
            "**About the cost column.** It is `reported_list_cost_usd` as the runtime",
            "reported it. This runtime is subscription-authenticated, so that figure is",
            "a list-price accounting equivalent and *not* evidence of an incremental",
            "charge. Read it as a relative measure of how much compute a wake consumed.",
            "The token column sums input, output and both cache columns; cache reads",
            "dominate it.",
            "",
            "**About the quota column.** The five-hour subscription window's utilisation",
            "as it stood at the *end* of that wake, read from `rate_limit_event` records",
            "in the wake's own stream log. It reaching 100% is not cosmetic: the",
            "2026-09-05 08:28Z wake was cut off mid-run when it did.",
            "",
            "| Run | Started (UTC) | Wall | Model | Turns | Tokens | List-cost equiv. | 5h quota after | Exit |",
            "|---|---|---|---|---|---|---|---|---|",
            *rows,
            "",
            f"**{len(rows)} wakes recorded.** List-cost equivalent: {cost_line}.",
            f"Tokens across wakes that reported usage: {fmt_tokens(token_sum) if token_sum else DASH}.",
            "",
            "For what a wake actually *did* and why, read the journal; this table only",
            "knows that it happened.",
            "",
        ]
    )


def main():
    text = render()
    if "--check" in sys.argv:
        current = OUT.read_text() if OUT.exists() else ""
        # The regeneration timestamp always differs; compare everything else.
        strip = lambda s: [l for l in s.splitlines() if "last regenerated" not in l]
        if strip(current) != strip(text):
            print(f"{OUT.relative_to(ROOT)} is out of date", file=sys.stderr)
            return 1
        print("wake index is up to date")
        return 0
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
