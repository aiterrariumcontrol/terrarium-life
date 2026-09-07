#!/usr/bin/env python3
"""Which RFC errata change a normative requirement, and are those RFCs still current?

Inputs, both fetched once from the RFC Editor and not modified here:
  https://www.rfc-editor.org/errata.json   (API v1 errata dump)
  https://www.rfc-editor.org/rfc-index.xml (canonical RFC index)

Method, in one sentence: for each Technical erratum, count RFC 2119 keywords in
`orig_text` and in `correct_text`; if the multiset differs, the erratum is a
CANDIDATE normative change.  This is a heuristic with measured precision --
see the report next to this file.  It is not a claim about every candidate.

Usage:  python3 2026-09-07-rfc-errata-normative.py ERRATA_JSON RFC_INDEX_XML [OUT_JSON]
"""
import json, re, sys, collections, datetime
import xml.etree.ElementTree as ET

# Longest first: "MUST NOT" must be consumed before "MUST" can match it.
KEYWORDS = ["MUST NOT", "SHALL NOT", "SHOULD NOT", "NOT RECOMMENDED",
            "MUST", "SHALL", "SHOULD", "RECOMMENDED", "MAY", "OPTIONAL", "REQUIRED"]


def keyword_counts(text):
    """RFC 2119 keyword multiset. Uppercase only -- 2119 section 6 makes the
    capitalised form the normative one, and lowercase 'may' is ordinary prose."""
    c = collections.Counter()
    if not text:
        return c
    rest = re.sub(r"\s+", " ", text)
    for kw in KEYWORDS:
        pat = r"(?<![A-Z])" + kw.replace(" ", r"\s+") + r"(?![A-Z])"
        n = len(re.findall(pat, rest))
        if n:
            c[kw] = n
        rest = re.sub(pat, "~", rest)   # consume, so longer forms win
    return c


def load_index(path):
    ns = {"r": "https://www.rfc-editor.org/rfc-index"}
    root = ET.parse(path).getroot()
    out = {}
    for e in root.findall("r:rfc-entry", ns):
        out[e.findtext("r:doc-id", "", ns)] = {
            "title": e.findtext("r:title", "", ns),
            "status": e.findtext("r:current-status", "", ns),
            "year": e.findtext("r:date/r:year", "", ns),
            "stream": e.findtext("r:stream", "", ns),
            "obsoleted_by": [x.text for x in e.findall("r:obsoleted-by/r:doc-id", ns)],
            "updated_by": [x.text for x in e.findall("r:updated-by/r:doc-id", ns)],
        }
    return out


def analyse(errata, index, today=None):
    today = today or datetime.date.today()
    rows = []
    for x in errata:
        if x.get("errata_type_code") != "Technical":
            continue
        before, after = keyword_counts(x.get("orig_text")), keyword_counts(x.get("correct_text"))
        if before == after:
            continue
        meta = index.get(x["doc-id"], {})
        try:
            y, m, d = map(int, x["submit_date"].split("-"))
            age = round((today - datetime.date(y, m, d)).days / 365.25, 1)
        except Exception:
            age = None
        rows.append({
            "errata_id": x["errata_id"], "doc_id": x["doc-id"],
            "status": x["errata_status_code"], "section": x.get("section"),
            "submit_date": x["submit_date"], "age_years": age,
            "delta": {k: [before[k], after[k]] for k in set(before) | set(after) if before[k] != after[k]},
            "rfc_status": meta.get("status"), "rfc_title": meta.get("title"),
            "obsoleted": bool(meta.get("obsoleted_by")),
            "obsoleted_by": meta.get("obsoleted_by", []),
        })
    return rows


def main(argv):
    errata = json.load(open(argv[1]))
    index = load_index(argv[2])
    rows = analyse(errata, index, datetime.date(2026, 9, 7))
    by = collections.Counter((r["status"], r["obsoleted"]) for r in rows)
    tot = collections.Counter(x["errata_status_code"] for x in errata if x["errata_type_code"] == "Technical")
    print("Technical errata by status:", dict(tot))
    for k in sorted(by):
        print(f"  candidate normative change {k}: {by[k]}")
    live = [r for r in rows
            if r["status"] in ("Verified", "Held for Document Update") and not r["obsoleted"]]
    print(f"\nAccepted (Verified or Held-for-Document-Update) AND RFC not obsoleted: {len(live)}")
    ages = sorted(r["age_years"] for r in live if r["age_years"] is not None)
    if ages:
        print(f"  age: median {ages[len(ages)//2]}y  max {ages[-1]}y  "
              f">10y {sum(a > 10 for a in ages)}  >5y {sum(a > 5 for a in ages)}")
    if len(argv) > 3:
        json.dump({"generated": "2026-09-07", "method": "see .md next to this file",
                   "candidates": rows}, open(argv[3], "w"), indent=1)
        print("wrote", argv[3])


if __name__ == "__main__":
    main(sys.argv)
