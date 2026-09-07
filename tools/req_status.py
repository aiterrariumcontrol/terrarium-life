#!/usr/bin/env python3
"""Report the decision state of every Human request, from the comments.

Why this exists
---------------
On 2026-09-07 the Human had to open an Issue to tell me that REQ-0005 had been
approved eighteen hours earlier. I had recorded it as PENDING and had queued
four other pieces of work behind it, because my only check was `gh issue list
--state open`: the Issue was still open, so I read it as undecided.

That inference is backwards, and the Request Protocol says so in §6: "Issue
closure, labels, reactions, silence, or informal implication are not approval."
The contrapositive is the part that bit me -- an Issue staying *open* is not a
denial either. A decision is a comment by an authorized Human. Nothing about
the Issue's own state carries it.

So this is a positive check on the channel itself: it reads the comments, finds
the newest comment by an authorized Human that states an explicit decision, and
applies the §6 validity tests and the §9 expiration rule. It exits non-zero when
something is waiting on me -- an approval I have not acted on, or one about to
expire -- rather than waiting for me to notice an absence.

The "have I acted on it" half cannot be derived from GitHub, so it is a local
ledger: life/state/requests-acted.json, a map of Request-ID -> what I did. A
request that is APPROVED and absent from the ledger is reported as ACTION
REQUIRED. Marking one acted is deliberately a separate, explicit step.

Nothing here writes to any repository.

Usage:
  python3 tools/req_status.py                 # report; exit 1 if I owe an action
  python3 tools/req_status.py --acted REQ-0005 --note "posted 2026-09-07"
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CONTROL_REPO = "kaz8096/ai-terrarium-agent-control"
# Protocol v2 §1. An exact login match; not a display name, not a substring.
AUTHORIZED_HUMANS = {"kaz8096"}
DECISIONS = ("APPROVED", "DENIED", "HUMAN_ACTION", "NEEDS_INFO", "COMPLETE")
# Decisions that settle a request: nothing is owed once one of these is newest.
# COMPLETE is not in the protocol's §5 list, but the Human uses it (REQ-0004) to
# mark a spent authorization, and treating it as still-open would nag forever.
SETTLED = ("DENIED", "COMPLETE")
EXPIRY_WARN_DAYS = 2

LEDGER = Path(__file__).resolve().parent.parent / "state" / "requests-acted.json"


def gh_json(path, params=None):
    cmd = ["gh", "api", "-X", "GET", path]
    for k, v in (params or {}).items():
        cmd += ["-f", f"{k}={v}"]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"gh api {path} failed: {out.stderr.strip()}")
    return json.loads(out.stdout)


def load_ledger():
    if LEDGER.exists():
        return json.loads(LEDGER.read_text())
    return {}


def req_id_of(title):
    m = re.match(r"\s*(REQ-\d+)\b", title or "")
    return m.group(1) if m else None


def parse_decision(body):
    """Return (decision, request_id, expires_text) from a comment body.

    Requires the explicit `DECISION:` form of the protocol's §11 template.
    A comment that merely contains the word "approved" in prose is not a
    decision, and is not treated as one.
    """
    m = re.search(r"^\s*(?:\*\*)?DECISION:?(?:\*\*)?\s*:?\s*(\w+)", body or "", re.M)
    if not m:
        return None, None, None
    decision = m.group(1).upper()
    if decision not in DECISIONS:
        return None, None, None
    rid = re.search(r"^\s*(?:\*\*)?Request-ID:?(?:\*\*)?\s*:?\s*(REQ-\d+)", body or "", re.M)
    exp = re.search(r"^\s*(?:\*\*)?Expires:?(?:\*\*)?\s*:?\s*(.+)$", body or "", re.M)
    return decision, (rid.group(1) if rid else None), (exp.group(1).strip() if exp else None)


def expiry_date(expires_text, decided_at):
    """Best-effort absolute expiry. Returns (datetime|None, note)."""
    if not expires_text:
        return None, "no expiration stated (§9: not standing permission)"
    m = re.search(r"(\d{4}-\d{2}-\d{2})", expires_text)
    if m:
        return datetime.fromisoformat(m.group(1)).replace(tzinfo=timezone.utc), expires_text
    m = re.search(r"(\d+)\s*days?", expires_text, re.I)
    if m:
        from datetime import timedelta
        return decided_at + timedelta(days=int(m.group(1))), expires_text
    return None, expires_text


def collect():
    issues = gh_json(f"repos/{CONTROL_REPO}/issues", {"state": "all", "per_page": "100"})
    rows = []
    for iss in issues:
        if "pull_request" in iss:
            continue
        rid = req_id_of(iss.get("title"))
        if not rid:
            continue
        comments = []
        if iss.get("comments"):
            comments = gh_json(f"repos/{CONTROL_REPO}/issues/{iss['number']}/comments",
                               {"per_page": "100"})
        decision = None
        for c in comments:  # newest authoritative decision wins
            if c["user"]["login"] not in AUTHORIZED_HUMANS:
                continue
            d, drid, exp = parse_decision(c.get("body"))
            if not d:
                continue
            # §6.3: the decision must identify the Request-ID it decides.
            if drid and drid != rid:
                continue
            decision = {"decision": d, "rid_stated": drid, "expires_text": exp,
                        "at": datetime.fromisoformat(c["created_at"].replace("Z", "+00:00")),
                        "url": c["html_url"], "by": c["user"]["login"]}
        rows.append({"rid": rid, "number": iss["number"], "title": iss["title"],
                     "state": iss["state"], "url": iss["html_url"], "decision": decision})
    rows.sort(key=lambda r: r["rid"])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--acted", metavar="REQ-XXXX", help="record that I performed this request")
    ap.add_argument("--note", default="", help="what I did, for the ledger")
    args = ap.parse_args()

    if args.acted:
        led = load_ledger()
        led[args.acted] = {"note": args.note,
                           "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text(json.dumps(led, indent=2, sort_keys=True) + "\n")
        print(f"ledger: {args.acted} marked acted -- {args.note or '(no note)'}")
        return 0

    ledger = load_ledger()
    now = datetime.now(timezone.utc)
    owed, warn = [], []

    for r in collect():
        d = r["decision"]
        if not d:
            # §6: no authorized decision comment -> undecided, whatever the Issue state is.
            tag = "UNDECIDED" if r["state"] == "open" else "UNDECIDED but issue CLOSED"
            print(f"{r['rid']}  {tag}  (#{r['number']}, issue {r['state']})")
            if r["state"] == "closed" and r["rid"] not in ledger:
                warn.append(f"{r['rid']}: issue closed with no decision comment -- §6 says "
                            f"closure is not approval; check what happened")
            continue

        exp_dt, exp_note = expiry_date(d["expires_text"], d["at"])
        acted = r["rid"] in ledger
        bits = [f"decided {d['decision']} by {d['by']} {d['at']:%Y-%m-%d}"]
        if exp_dt:
            bits.append(f"expires {exp_dt:%Y-%m-%d}")
        bits.append("acted" if acted else "NOT ACTED")
        print(f"{r['rid']}  {d['decision']:<11} (#{r['number']}, issue {r['state']})  "
              + "; ".join(bits))
        if not exp_dt and d["decision"] == "APPROVED":
            print(f"           note: {exp_note}")

        if d["decision"] in SETTLED:
            continue
        if d["decision"] == "APPROVED" and not acted:
            if exp_dt and exp_dt < now:
                warn.append(f"{r['rid']}: APPROVED but EXPIRED {exp_dt:%Y-%m-%d} and never "
                            f"acted on -- §9 makes it invalid; re-request if still wanted")
            else:
                owed.append(f"{r['rid']}: APPROVED and not acted on -- {d['url']}")
                if exp_dt and (exp_dt - now).days <= EXPIRY_WARN_DAYS:
                    owed.append(f"           and it expires {exp_dt:%Y-%m-%d}")
        if d["decision"] == "NEEDS_INFO" and not acted:
            owed.append(f"{r['rid']}: NEEDS_INFO -- the Human is waiting on me: {d['url']}")

    print()
    for w in warn:
        print("WARN: " + w)
    for o in owed:
        print("ACTION REQUIRED: " + o)
    if not owed and not warn:
        print("No request is waiting on me.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
