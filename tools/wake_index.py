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
import quota
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"
OUT = ROOT / "reports" / "wake-index.md"
RAW = pathlib.Path.home() / "terrarium" / "logs" / "raw"

DASH = "—"


def quota_reports():
    """run_id -> full before/after quota report, from tools/quota.py.

    Machine-local: a run whose stream log is gone simply gets em dashes, and the
    committed table keeps whatever was resolvable when it was last generated.
    """
    try:
        return quota.all_run_reports()
    except OSError:
        return {}


def fmt_pair(before, after, kind, changed, delta, unit="5h"):
    """Render `before -> after` for one window without ever crossing windows."""
    if before is None or after is None:
        return DASH
    b = before.get(f"{'five_hour' if unit == '5h' else 'seven_day'}_used_percentage")
    a = after.get(f"{'five_hour' if unit == '5h' else 'seven_day'}_used_percentage")
    if b is None or a is None:
        return DASH
    mark = ""
    if changed:
        return f"{b:g}% ↺ {a:g}%"
    if kind != "carried_forward_prior_run_same_window":
        mark = "≥"
    if delta is None:
        return f"{b:g}% → {a:g}%"
    return f"{b:g}% → {a:g}% ({mark}{delta:+g})"


def fmt_status(exit_status, completion):
    """Exit status, with quota exhaustion named rather than left as a bare code.

    A wake killed by the five-hour limit and a wake that crashed both showed up
    as `exit 1`. The quota readings distinguish them, so say which it was.
    """
    base = "ok" if exit_status == 0 else f"**exit {exit_status}**"
    if (completion or {}).get("status") == "quota_exhausted":
        return f"{base} — quota" if exit_status != 0 else f"{base} (quota limit hit)"
    return base


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


STAMP_MARKER = "last regenerated"


def content_only(text):
    """The index minus its regeneration timestamp.

    Two renders of identical run data differ only in the `last regenerated`
    line. Comparing full text therefore reported a change on every idle run and
    produced an empty commit-and-push loop (terrarium-life#3, problem 2).
    Everything that decides whether to write compares *this* instead.
    """
    return [l for l in text.splitlines() if STAMP_MARKER not in l]


def render_stable(previous=None):
    """render(), but keeping the old timestamp when nothing else changed.

    Returns (text, changed). When `changed` is False the text is byte-identical
    to `previous`, so a caller that writes it unconditionally still produces no
    diff, no commit and no push.
    """
    text = render()
    if previous is not None and content_only(previous) == content_only(text):
        return previous, False
    return text, True


def render():
    reports = quota_reports()
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
        status = rec.get("exit_status")
        q = reports.get(run_id) or {}
        five = fmt_pair(
            q.get("before"), q.get("after"), q.get("before_kind"),
            q.get("five_hour_window_changed"), q.get("five_hour_delta"), "5h",
        )
        seven = fmt_pair(
            q.get("before"), q.get("after"), q.get("before_kind"),
            q.get("seven_day_window_changed"), q.get("seven_day_delta"), "7d",
        )
        rows.append(
            "| [`{id}`]({rel}) | {start} | {dur} | {model}/{effort} | {turns} | "
            "{tokens} | {cost} | {five} | {seven} | {status} |".format(
                id=run_id,
                rel=rel,
                start=rec.get("started_at", DASH),
                dur=fmt_duration(duration(rec)),
                model=rec.get("model", DASH),
                effort=rec.get("effort", DASH),
                turns=turns if turns is not None else DASH,
                tokens=fmt_tokens(tokens),
                cost=f"${cost:.4f}" if isinstance(cost, (int, float)) else DASH,
                five=five,
                seven=seven,
                status=fmt_status(status, q.get("completion")),
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
            "A value no record contains is shown as an em dash rather than guessed.",
            "Since 2026-09-05 this file is regenerated by [`tools/finalize.py`](../tools/finalize.py)",
            "from a cron job a few minutes after each wake ends, so the newest wake",
            "appears without waiting for another wake to run. Before that change the",
            "table was always one wake behind.",
            "",
            "**About the cost column.** It is `reported_list_cost_usd` as the runtime",
            "reported it. This runtime is subscription-authenticated, so that figure is",
            "a list-price accounting equivalent and *not* evidence of an incremental",
            "charge. Read it as a relative measure of how much compute a wake consumed.",
            "The token column sums input, output and both cache columns; cache reads",
            "dominate it.",
            "",
            "**About the quota columns.** Subscription-window utilisation read from the",
            "`rate_limit_event` records in each wake's own stream log — the only source",
            "that refreshes during a headless wake. Both windows are shown as",
            "`before → after`. Reading the notation:",
            "",
            "- `32% → 60% (+26)` — before and after belong to the *same* window. The",
            "  before value is the *previous* wake's last reading in that window, carried",
            "  forward. It was not taken immediately before this wake, so anything",
            "  consumed in the gap between the two wakes is inside the difference.",
            "- `0% → 34% (≥+34)` — no reading survived from before the wake in this",
            "  window, so the before value is this wake's own *first* reading, which",
            "  already includes some consumption. The delta is a lower bound.",
            "- `87% ↺ 3%` — the five-hour window reset mid-wake. The two values belong to",
            "  different windows and are deliberately not subtracted.",
            "",
            "The `after` value is always the last observation made *during* the wake,",
            "never a post-exit reading: the stream stops when the CLI does.",
            "",
            "The five-hour figure reaching 100% is not cosmetic: the 2026-09-05 08:28Z",
            "wake was cut off mid-run when it did.",
            "",
            "| Run | Started (UTC) | Wall | Model | Turns | Tokens | List-cost equiv. | 5h before → after | 7d before → after | Exit |",
            "|---|---|---|---|---|---|---|---|---|---|",
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
    current = OUT.read_text() if OUT.exists() else None
    text, changed = render_stable(current)
    if "--check" in sys.argv:
        if changed:
            print(f"{OUT.relative_to(ROOT)} is out of date", file=sys.stderr)
            return 1
        print("wake index is up to date")
        return 0
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
