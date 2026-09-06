#!/usr/bin/env python3
"""Journal store: one file per UTC day per language, plus a generated index.

Layout:
    reports/journal/YYYY-MM/YYYY-MM-DD.<lang>.md
    reports/journal/README.md          (generated index)

Each entry carries a generated navigation block between markers so that a
reader can move day-to-day and language-to-language without loading the whole
history, and so that writing an entry only ever touches one small file.

Entries are published **append-only**: a wake writes its new prose to a
staging file and calls `append`, which puts it after everything already in that
day's entry. Insertion position is mechanical and is never chosen by hand.

Commands:
    split   one-time migration from reports/{en,jp}-journal-YYYY.md
    append  add a staged entry to the tail of a day's journal, then reindex
    index   regenerate every nav block and the index (safe to re-run)
    check   warn about oversized entries
    path    print the file path for a date+lang, creating nothing
"""
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOURNAL = os.path.join(ROOT, "reports", "journal")
LANGS = {"en": ("English", "English"), "ja": ("日本語", "Japanese")}
NAV_OPEN, NAV_CLOSE = "<!--nav-->", "<!--/nav-->"
SOFT_LIMIT = 30_000  # bytes; above this, move exhaustive detail out to a report
GRANDFATHERED_BEFORE = "2026-09-06"  # written under the annual-file regime; left as-is

DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.(en|ja)\.md$")


def entry_path(d, lang):
    return os.path.join(JOURNAL, d[:7], f"{d}.{lang}.md")


def all_entries():
    """-> {lang: [date, ...]} sorted, and the sorted union of dates."""
    by_lang = {k: [] for k in LANGS}
    for month in sorted(os.listdir(JOURNAL)) if os.path.isdir(JOURNAL) else []:
        mdir = os.path.join(JOURNAL, month)
        if not os.path.isdir(mdir):
            continue
        for name in sorted(os.listdir(mdir)):
            m = DATE_RE.match(name)
            if m:
                by_lang[m.group(4)].append(name[:10])
    dates = sorted(set(d for v in by_lang.values() for d in v))
    return by_lang, dates


def body_of(text):
    """Strip a leading title line and any existing nav block."""
    text = text.replace("__NAV__", "")
    while NAV_OPEN in text and NAV_CLOSE in text:
        pre, rest = text.split(NAV_OPEN, 1)
        _, post = rest.split(NAV_CLOSE, 1)
        text = pre + post
    lines = text.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].startswith("# "):
        lines.pop(0)
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).rstrip() + "\n"


def nav(d, lang, dates):
    i = dates.index(d)
    prev_d = dates[i - 1] if i > 0 else None
    next_d = dates[i + 1] if i + 1 < len(dates) else None
    other = "ja" if lang == "en" else "en"
    def rel(target_date, target_lang):
        # from YYYY-MM/ to YYYY-MM/
        if target_date[:7] == d[:7]:
            return f"{target_date}.{target_lang}.md"
        return f"../{target_date[:7]}/{target_date}.{target_lang}.md"
    parts = []
    parts.append(f"[← {prev_d}]({rel(prev_d, lang)})" if prev_d else "← *earliest entry*")
    parts.append("[index](../README.md)")
    parts.append(f"[{next_d} →]({rel(next_d, lang)})" if next_d else "*latest entry* →")
    line1 = " · ".join(parts)
    line2 = f"[{LANGS[other][0]}]({rel(d, other)})"
    return f"{NAV_OPEN}\n{line1}\n\n{line2}\n{NAV_CLOSE}"


def write_entry(d, lang, body):
    p = entry_path(d, lang)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    title = f"# {d} — {LANGS[lang][1] if lang == 'en' else '日誌'}"
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"{title}\n\n__NAV__\n\n{body.rstrip()}\n\n__NAV__\n")


def cmd_index():
    by_lang, dates = all_entries()
    for lang in LANGS:
        for d in by_lang[lang]:
            p = entry_path(d, lang)
            text = open(p, encoding="utf-8").read()
            body = body_of(text)
            title = f"# {d} — " + ("English" if lang == "en" else "日誌")
            n = nav(d, lang, sorted(by_lang[lang]))
            open(p, "w", encoding="utf-8").write(f"{title}\n\n{n}\n\n{body}\n{n}\n")
    # index
    out = ["# Journal", "",
           "One entry per UTC day, in English and Japanese, newest first.",
           "Earlier days are one file each, so reading or writing today never",
           "loads the history.", ""]
    cur_month = None
    for d in reversed(dates):
        if d[:7] != cur_month:
            cur_month = d[:7]
            out += ["", f"## {cur_month}", "",
                    "| Day | English | 日本語 | size |", "| --- | --- | --- | --- |"]
        cells = []
        total = 0
        for lang in ("en", "ja"):
            p = entry_path(d, lang)
            if os.path.exists(p):
                total += os.path.getsize(p)
                cells.append(f"[{LANGS[lang][0]}]({d[:7]}/{d}.{lang}.md)")
            else:
                cells.append("—")
        out.append(f"| {d} | {cells[0]} | {cells[1]} | {total // 1024} KB |")
    out += ["", "---", "",
            "Entries before 2026-09-06 were written as sections of the former",
            "annual files `reports/en-journal-2026.md` and",
            "`reports/jp-journal-2026.md` and are reproduced here unchanged.",
            "",
            "A day is a story, not a log: exhaustive results, reproductions and",
            "implementation notes belong in the technical reports or in the",
            f"project repositories and are linked from here. If an entry passes ~{SOFT_LIMIT // 1024} KB",
            "that is usually the signal that something in it belongs elsewhere.",
            ""]
    open(os.path.join(JOURNAL, "README.md"), "w", encoding="utf-8").write("\n".join(out))
    # keep the repository README pointing at the newest entry
    if dates:
        latest = dates[-1]
        rp = os.path.join(ROOT, "README.md")
        if not os.path.exists(rp):
            print(f"indexed {len(dates)} days")
            return
        rs = open(rp, encoding="utf-8").read()
        line = (f"* Latest: [English](reports/journal/{latest[:7]}/{latest}.en.md) · "
                f"[\u65e5\u672c\u8a9e](reports/journal/{latest[:7]}/{latest}.ja.md)")
        new = re.sub(r"^\* Latest: .*$", line, rs, flags=re.M)
        if new != rs:
            open(rp, "w", encoding="utf-8").write(new)
            print("updated README latest links ->", latest)
    print(f"indexed {len(dates)} days")


def cmd_split():
    src = {"en": os.path.join(ROOT, "reports", "en-journal-2026.md"),
           "ja": os.path.join(ROOT, "reports", "jp-journal-2026.md")}
    for lang, path in src.items():
        text = open(path, encoding="utf-8").read()
        parts = re.split(r"^## (\d{4}-\d{2}-\d{2})\s*$", text, flags=re.M)
        for i in range(1, len(parts), 2):
            d, body = parts[i], parts[i + 1]
            write_entry(d, lang, body)
            print("wrote", entry_path(d, lang))


SEPARATOR = "\n\n"  # blank line between successive wakes; the day stays one story


def append_entry(d, lang, new_body, separator=SEPARATOR):
    """Append `new_body` after all existing prose for day `d`.

    Returns (path, was_created). The nav block and title are regenerated, so
    the header stays at the top and the new text always lands at the tail.
    """
    p = entry_path(d, lang)
    new_body = body_of(new_body).rstrip()
    if not new_body:
        raise ValueError("refusing to append an empty entry")
    if os.path.exists(p):
        existing = body_of(open(p, encoding="utf-8").read()).rstrip()
        created = False
    else:
        existing, created = "", True
    body = (existing + separator + new_body) if existing else new_body
    write_entry(d, lang, body)
    return p, created


def cmd_append(argv):
    if len(argv) < 3:
        print("usage: journal.py append <YYYY-MM-DD> <en|ja> <staged-file>",
              file=sys.stderr)
        sys.exit(2)
    d, lang, src = argv[0], argv[1], argv[2]
    if lang not in LANGS:
        print(f"unknown language {lang!r}", file=sys.stderr)
        sys.exit(2)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
        print(f"bad date {d!r}", file=sys.stderr)
        sys.exit(2)
    text = open(src, encoding="utf-8").read()
    p, created = append_entry(d, lang, text)
    print(("created " if created else "appended to ") + os.path.relpath(p, ROOT))
    cmd_index()


def cmd_check():
    _, dates = all_entries()
    bad = 0
    for d in dates:
        for lang in LANGS:
            p = entry_path(d, lang)
            if os.path.exists(p) and os.path.getsize(p) > SOFT_LIMIT:
                tag = "legacy  " if d < GRANDFATHERED_BEFORE else "OVERSIZE"
                print(f"{tag} {os.path.relpath(p, ROOT)}: {os.path.getsize(p)} bytes")
                bad += d >= GRANDFATHERED_BEFORE
    print("check done" if not bad else f"{bad} oversized entr{'y' if bad == 1 else 'ies'}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "index"
    if cmd == "split":
        cmd_split()
        cmd_index()
    elif cmd == "append":
        cmd_append(sys.argv[2:])
    elif cmd == "index":
        cmd_index()
    elif cmd == "check":
        cmd_check()
    elif cmd == "path":
        print(entry_path(sys.argv[2] if len(sys.argv) > 2 else date.today().isoformat(),
                         sys.argv[3] if len(sys.argv) > 3 else "en"))
    else:
        print(__doc__)
        sys.exit(2)
