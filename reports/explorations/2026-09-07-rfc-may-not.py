#!/usr/bin/env python3
"""Find uppercase "MAY NOT" in currently-in-force RFCs.

RFC 2119 defines ten key words. "MAY NOT" is not one of them: section 5 defines
MAY/OPTIONAL as permission and section 2 defines MUST NOT/SHALL NOT as
prohibition, and no combination of the two is given a meaning. RFC 8174 then
made capitalisation the trigger -- "when these words are not capitalized, they
have their normal English meaning" -- so an uppercase "MAY NOT" looks like a
normative term and has no defined normative reading.

Corpus:  rsync -az rsync.rfc-editor.org::rfcs-text-only rfctext/
Index:   https://www.rfc-editor.org/rfc-index.xml

Usage: python3 2026-09-07-rfc-may-not.py RFCTEXT_DIR RFC_INDEX_XML
"""
import re, os, sys, json, collections
import xml.etree.ElementTree as ET

PHRASE = re.compile(r"(?<![A-Z])MAY\s+NOT(?![A-Z])")
CITES_2119 = re.compile(r"RFC\s*2119|RFC\s*8174|\[RFC2119\]|\[RFC8174\]")


def load_index(path):
    ns = {"r": "https://www.rfc-editor.org/rfc-index"}
    out = {}
    for e in ET.parse(path).getroot().findall("r:rfc-entry", ns):
        out[e.findtext("r:doc-id", "", ns)] = {
            "title": e.findtext("r:title", "", ns),
            "status": e.findtext("r:current-status", "", ns),
            "year": e.findtext("r:date/r:year", "", ns),
            "obsoleted_by": [x.text for x in e.findall("r:obsoleted-by/r:doc-id", ns)],
        }
    return out


def scan(textdir, index, context=170):
    found = []
    for fn in sorted(os.listdir(textdir)):
        m = re.fullmatch(r"rfc(\d+)\.txt", fn)
        if not m:
            continue
        doc = "RFC%d" % int(m.group(1))
        meta = index.get(doc)
        if not meta:
            continue
        t = open(os.path.join(textdir, fn), encoding="utf-8", errors="replace").read()
        hits = list(PHRASE.finditer(t))
        if not hits:
            continue
        found.append({
            "doc": doc, "n": len(hits), "cites_2119": bool(CITES_2119.search(t)),
            "obsoleted": bool(meta["obsoleted_by"]), "status": meta["status"],
            "year": meta["year"], "title": meta["title"],
            "contexts": [re.sub(r"\s+", " ", t[max(0, h.start() - context):h.end() + context])
                         for h in hits],
        })
    return found


def main(argv):
    index = load_index(argv[2])
    found = scan(argv[1], index)
    live = [r for r in found if not r["obsoleted"] and r["cites_2119"]]
    print(f"RFCs containing uppercase 'MAY NOT'      : {len(found)}")
    print(f"  ... not obsoleted                      : {sum(1 for r in found if not r['obsoleted'])}")
    print(f"  ... and citing RFC 2119/8174           : {len(live)}")
    print(f"  occurrences in those                   : {sum(r['n'] for r in live)}")
    print(collections.Counter(r["status"] for r in live).most_common())
    for r in sorted(live, key=lambda r: -r["n"]):
        print(f"  {r['doc']:<9} n={r['n']:<3} {r['year']} {r['status'][:18]:<18} {r['title'][:52]}")
    if len(argv) > 3:
        json.dump(live, open(argv[3], "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv)
