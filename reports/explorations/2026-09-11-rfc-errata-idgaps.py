#!/usr/bin/env python3
"""What are the errata ids that the RFC Editor dump does not contain?

The residual-queue note (2026-09-11-rfc-errata-residual.md) counts 739
unadjudicated errata out of an 8,039-record dump, and listed as a known limit
that 1,128 ids inside the dump's own id range are absent from it, cause
undetermined. That gap matters to the headline count: if any absent id were a
suppressed *Reported* record, 739 would be an undercount.

This script settles it three ways.

1.  Structure of the gap: contiguous-run lengths, and density by submission
    year (dating an absent id by its nearest present neighbour).
2.  Whether rejections are the explanation. They are not: the dump contains
    Rejected records, so a rejection is not a reason to be absent.
3.  Whether an absent id is publicly retrievable at all, by fetching
    https://www.rfc-editor.org/errata/eid<N> for a sample of absent ids and a
    control sample of present ids. --probe does the network part; it sleeps
    between requests and is meant to be run rarely.

Input: the same dump as the residual note.
Usage:
  python3 2026-09-11-rfc-errata-idgaps.py errata.json [--probe N] [--seed S]
"""
import json, sys, collections, bisect, random, subprocess, time

BASE = "https://www.rfc-editor.org/errata/eid"


def load(path):
    recs = json.load(open(path))
    by = {int(r["errata_id"]): r for r in recs}
    return recs, by


def runs(missing):
    """Collapse a sorted id list into (start, end) contiguous runs."""
    out, st, prev = [], missing[0], missing[0]
    for i in missing[1:]:
        if i == prev + 1:
            prev = i
        else:
            out.append((st, prev)); st = prev = i
    out.append((st, prev))
    return out


def year_of(i, present, by):
    """Date an absent id by its nearest present neighbour's submission year."""
    j = min(bisect.bisect_left(present, i), len(present) - 1)
    return by[present[j]]["submit_date"][:4]


def http_status(eid):
    """-L matters: /errata/eidN redirects to errata.rfc-editor.org."""
    r = subprocess.run(["curl", "-sL", "-o", "/dev/null", "-w", "%{http_code}",
                        f"{BASE}{eid}"], capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def main():
    path = sys.argv[1]
    probe_n = 0
    seed = 7
    if "--probe" in sys.argv:
        probe_n = int(sys.argv[sys.argv.index("--probe") + 1])
    if "--seed" in sys.argv:
        seed = int(sys.argv[sys.argv.index("--seed") + 1])

    recs, by = load(path)
    present = sorted(by)
    have = set(present)
    missing = [i for i in range(present[0], present[-1] + 1) if i not in have]

    out = {
        "source": path,
        "records": len(recs),
        "id_range": [present[0], present[-1]],
        "present": len(present),
        "absent": len(missing),
        "status_counts": dict(collections.Counter(r["errata_status_code"] for r in recs)),
    }

    rl = runs(missing)
    out["runs"] = {
        "count": len(rl),
        "length_histogram": dict(sorted(collections.Counter(b - a + 1 for a, b in rl).items())),
        "longest": [[a, b, b - a + 1] for a, b in sorted(rl, key=lambda r: -(r[1] - r[0]))[:10]],
    }
    # Each long run is bracketed by its neighbours; if those are days apart the
    # run is an id-allocation artifact, not a span of lost content.
    out["long_run_neighbours"] = [
        {"gap": [a, b],
         "before": {k: by[a - 1][k] for k in ("errata_id", "submit_date", "errata_status_code")} if a - 1 in by else None,
         "after": {k: by[b + 1][k] for k in ("errata_id", "submit_date", "errata_status_code")} if b + 1 in by else None}
        for a, b in sorted(rl, key=lambda r: -(r[1] - r[0]))[:6]
    ]

    tot, gap = collections.Counter(), collections.Counter()
    for i in range(present[0], present[-1] + 1):
        y = year_of(i, present, by)
        tot[y] += 1
        if i not in have:
            gap[y] += 1
    out["gap_rate_by_year"] = {
        y: {"ids": tot[y], "absent": gap[y], "pct": round(100 * gap[y] / tot[y], 1)}
        for y in sorted(tot) if y != "9999"
    }

    # Confound check for the residual note: if recent junk were deleted instead
    # of Rejected, the Rejected share would fall as the gap rate rose.
    mix = collections.defaultdict(collections.Counter)
    for r in recs:
        y = r["submit_date"][:4]
        if y != "9999":
            mix[y][r["errata_status_code"]] += 1
    out["status_mix_by_year"] = {
        y: {k: round(100 * v / sum(c.values()), 1) for k, v in c.items()} | {"n": sum(c.values())}
        for y, c in sorted(mix.items())
    }

    if probe_n:
        random.seed(seed)
        sa = sorted(random.sample(missing, min(probe_n, len(missing))))
        sp = sorted(random.sample(present, min(probe_n // 2, len(present))))
        res = {"seed": seed, "absent": {}, "present": {}}
        for tag, ids in (("absent", sa), ("present", sp)):
            for i in ids:
                res[tag][i] = http_status(i)
                time.sleep(1)
        res["absent_statuses"] = dict(collections.Counter(res["absent"].values()))
        res["present_statuses"] = dict(collections.Counter(res["present"].values()))
        out["probe"] = res

    json.dump(out, sys.stdout, indent=1, sort_keys=False)
    print()


if __name__ == "__main__":
    main()
