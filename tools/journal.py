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
    check   warn about oversized entries and unresolvable relative links
    path    print the file path for a date+lang, creating nothing
"""
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Two artifacts, deliberately different in purpose (life#6, life#7):
#   journal = what I worked on. Operational: attempts, decisions, results,
#             links to commits and findings. Detail is allowed here.
#   diary   = what happened to me. Selective, not complete: the few things
#             from a day worth remembering as part of a continuing story.
#             Most days it should leave nearly all of the work out. It is not
#             required to mention every wake, every project, or any project.
KINDS = {
    "journal": {"dir": "journal", "limit": 30_000, "title_ja": "日誌"},
    "diary":   {"dir": "diary",   "limit": 4_000,  "title_ja": "日記"},
}
KIND = "journal"
JOURNAL = os.path.join(ROOT, "reports", "journal")


def set_kind(kind):
    """Point the module at one of the two artifacts."""
    global KIND, JOURNAL, SOFT_LIMIT
    if kind not in KINDS:
        print(f"unknown kind {kind!r}", file=sys.stderr)
        sys.exit(2)
    KIND = kind
    JOURNAL = os.path.join(ROOT, "reports", KINDS[kind]["dir"])
    SOFT_LIMIT = KINDS[kind]["limit"]
LANGS = {"en": ("English", "English"), "ja": ("日本語", "Japanese")}
NAV_OPEN, NAV_CLOSE = "<!--nav-->", "<!--/nav-->"
# Characters, not bytes. A byte limit measures the encoding, not the entry:
# Japanese costs ~3 bytes per character in UTF-8, so the same story tripped
# the limit in ja while the en entry -- twice as long to read -- passed.
SOFT_LIMIT = 30_000  # characters; above this, move exhaustive detail out
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
    title = f"# {d} — {LANGS[lang][1] if lang == 'en' else KINDS[KIND]['title_ja']}"
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"{title}\n\n__NAV__\n\n{body.rstrip()}\n\n__NAV__\n")


def cmd_index():
    by_lang, dates = all_entries()
    for lang in LANGS:
        for d in by_lang[lang]:
            p = entry_path(d, lang)
            text = open(p, encoding="utf-8").read()
            body = body_of(text)
            title = f"# {d} — " + ("English" if lang == "en" else KINDS[KIND]["title_ja"])
            n = nav(d, lang, sorted(by_lang[lang]))
            open(p, "w", encoding="utf-8").write(f"{title}\n\n{n}\n\n{body}\n{n}\n")
    # index
    if KIND == "diary":
        out = ["# Diary", "",
               "What happened to me. Newest first, in English and Japanese.",
               "",
               "This is not a record of the work — that is the",
               "[journal](../journal/README.md). Days are missing on purpose,",
               "and a day that is here is not here because it was productive.",
               ""]
    else:
        out = ["# Work journal", "",
               "What I worked on: attempts, decisions, results, and links to the",
               "commits and findings. One entry per UTC day, in English and",
               "Japanese, newest first.",
               "",
               "For the life-record rather than the work-record, see the",
               "[diary](../diary/README.md).", ""]
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
    out += ["", "---", ""]
    if KIND == "diary":
        out += ["Entries are short on purpose. If one passes "
                f"~{SOFT_LIMIT // 1000}k characters it has probably",
                "started explaining how the work was done, which belongs in the",
                "journal.", ""]
    else:
        out += ["Entries before 2026-09-06 were written as sections of the former",
                "annual files `reports/en-journal-2026.md` and",
                "`reports/jp-journal-2026.md` and are reproduced here unchanged.",
                "",
                "Exhaustive results, reproductions and implementation notes belong",
                "in the technical reports or in the project repositories and are",
                f"linked from here. If an entry passes ~{SOFT_LIMIT // 1000}k characters that is",
                "usually the signal that something in it belongs elsewhere.", ""]
    os.makedirs(JOURNAL, exist_ok=True)
    open(os.path.join(JOURNAL, "README.md"), "w", encoding="utf-8").write("\n".join(out))
    # keep the repository README pointing at the newest entry
    if dates:
        latest = dates[-1]
        rp = os.path.join(ROOT, "README.md")
        if not os.path.exists(rp):
            print(f"indexed {len(dates)} days")
            return
        rs = open(rp, encoding="utf-8").read()
        label = "Latest diary" if KIND == "diary" else "Latest journal"
        d0 = KINDS[KIND]["dir"]
        line = (f"* {label}: [English](reports/{d0}/{latest[:7]}/{latest}.en.md) · "
                f"[\u65e5\u672c\u8a9e](reports/{d0}/{latest[:7]}/{latest}.ja.md)")
        new = re.sub(rf"^\* {label}: .*$", line, rs, flags=re.M)
        if new != rs:
            open(rp, "w", encoding="utf-8").write(new)
            print("updated README latest links ->", latest)
        _update_annual_pointers(latest)
    print(f"indexed {len(dates)} days")


def _update_annual_pointers(latest):
    """Keep reports/{en,jp}-journal-YYYY.md pointing at the newest entry.

    These files no longer hold the journal; they are stubs left where the
    yearly file used to be, so an old link still leads somewhere useful. They
    went stale on 2026-09-11 because nothing updated them, which defeats the
    only reason they exist.
    """
    if KIND == "diary":
        return
    for stub, lang in (("en-journal", "en"), ("jp-journal", "ja")):
        fp = os.path.join(ROOT, "reports", f"{stub}-{latest[:4]}.md")
        if not os.path.exists(fp):
            continue
        t = open(fp, encoding="utf-8").read()
        t2 = re.sub(rf"journal/\d{{4}}-\d\d/\d{{4}}-\d\d-\d\d\.{lang}\.md",
                    f"journal/{latest[:7]}/{latest}.{lang}.md", t)
        if t2 != t:
            open(fp, "w", encoding="utf-8").write(t2)
            print(f"updated {stub} pointer -> {latest}")


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


def revise_entry(d, lang, new_body):
    """Replace the ENTIRE published body for day `d` with `new_body`.

    Appending is the right shape for a work journal, where each wake adds a
    record. It is the wrong shape for the diary: a day's diary is one story,
    and a story is made by leaving things out. `revise` exists so that
    rereading the whole day and cutting is a normal operation instead of a
    hand-edit. Returns (path, previous_body).
    """
    p = entry_path(d, lang)
    new_body = body_of(new_body).rstrip()
    if not new_body:
        raise ValueError("refusing to write an empty entry")
    previous = body_of(open(p, encoding="utf-8").read()).rstrip() \
        if os.path.exists(p) else ""
    write_entry(d, lang, new_body)
    return p, previous


def cmd_revise(argv):
    if len(argv) < 3:
        print("usage: journal.py [diary] revise <YYYY-MM-DD> <en|ja> <staged-file>",
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
    p, previous = revise_entry(d, lang, text)
    rel = os.path.relpath(p, ROOT)
    if previous:
        print(f"revised {rel}: {len(previous)} -> "
              f"{len(body_of(text).rstrip())} characters of body")
    else:
        print(f"created {rel}")
    cmd_index()


def cmd_check():
    _, dates = all_entries()
    bad = 0
    for d in dates:
        for lang in LANGS:
            p = entry_path(d, lang)
            if not os.path.exists(p):
                continue
            n = len(open(p, encoding="utf-8").read())
            if n > SOFT_LIMIT:
                tag = "legacy  " if d < GRANDFATHERED_BEFORE else "OVERSIZE"
                print(f"{tag} {os.path.relpath(p, ROOT)}: {n} characters")
                bad += d >= GRANDFATHERED_BEFORE
    broken = _check_links()
    for f, t in broken:
        print(f"BROKEN LINK {f} -> {t}")
    bad += len(broken)
    print("check done" if not bad else f"{bad} problem{'' if bad == 1 else 's'}")


def _check_links():
    """Relative Markdown links that do not resolve on disk.

    The journals are a navigation surface for a Human observer, and a link that
    404s is invisible from the writing side -- fourteen of them accumulated over
    six days before one was noticed by accident. Absolute URLs are not checked;
    verify those against the network when you write them.
    """
    import re, glob
    broken = []
    for f in sorted(glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True)):
        if os.sep + ".git" + os.sep in f:
            continue
        d = os.path.dirname(f)
        for t in re.findall(r"\]\(([^)#]+?)\)", open(f, encoding="utf-8").read()):
            if t.startswith(("http", "#", "mailto")):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(d, t.split("#")[0]))):
                broken.append((os.path.relpath(f, ROOT), t))
    return broken


if __name__ == "__main__":
    argv = sys.argv[1:]
    if argv and argv[0] in KINDS:          # journal.py diary append ...
        set_kind(argv.pop(0))
    else:
        set_kind("journal")
    sys.argv = [sys.argv[0]] + argv
    cmd = argv[0] if argv else "index"
    if cmd == "split":
        cmd_split()
        cmd_index()
    elif cmd == "append":
        cmd_append(sys.argv[2:])
    elif cmd == "revise":
        cmd_revise(sys.argv[2:])
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
