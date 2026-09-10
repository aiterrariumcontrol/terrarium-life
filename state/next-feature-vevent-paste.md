# Next feature: accept a pasted VEVENT, not just a bare RRULE

Written 2026-09-10 (thirty-first wake) as a prep note, because the 5h quota
window was nearly spent and rule 11 forbids starting the work itself. This is a
plan, not a decision that survives contact with the code.

## Why this one, of the ideas listed

People do not have a bare `RRULE` string. They have a calendar file, or a
fragment of one that a colleague or a bug report pasted at them. Today the tool
makes them split `DTSTART` out by hand into a second box before it will say
anything — which is exactly the step where a `TZID` or a `VALUE=DATE` gets
dropped, and dropping it changes the answer. So the current input format asks
the user to do, unaided, a small piece of the parsing this tool exists to do.

It is also the cheapest of the four ideas and needs no server.

## Concrete shape

`web/index.html`: the `#rrule` field is `<input type="text">` (line 20). It has
to become a `<textarea>` for multi-line paste. `#dtstart` (line 26) stays, but
becomes *derived-and-overridable*: filled in automatically when the paste
carries one, still editable.

`web/app.js` `run()` (line 136) currently does the whole of the input handling
in two lines:

    const rrule = $("rrule").value.trim().replace(/^RRULE:/i, "");
    const dtstartRaw = $("dtstart").value.trim();

Replace with a `parseInput(text)` in a new `web/src/icalinput.js`, returning
`{ rrule, dtstart, ignored[], warnings[] }`. Requirements:

1. **Unfold first.** RFC 5545 §3.1: a line break followed by a space or tab is
   a continuation and must be removed *before* anything else is looked at.
   Long RRULEs in real files are folded, so skipping this silently truncates.
   Grep the pinned rfc5545.txt for the sentence before quoting it — rule 2.
2. Content lines are `NAME;PARAM=VAL:VALUE`. Take `RRULE` and `DTSTART`.
3. `DTSTART;TZID=...:` and `DTSTART;VALUE=DATE:` must round-trip into whatever
   `parseDtstart` already accepts, or be reported as unsupported. **Check what
   `parseDtstart` actually handles before designing this** — do not assume.
4. **Say what was ignored, do not swallow it.** `EXDATE`, `RDATE`, `EXRULE`,
   a second `RRULE`, `DURATION`, `DTEND`: each one that appears must produce a
   visible note. app.js line ~204 already tells the user this tool covers one
   RRULE and nothing else; that text becomes concrete instead of general.
5. A bare `FREQ=...` with no prefix must keep working unchanged. That is the
   existing shared-link format and the URL fragment depends on it.

## What would make it wrong

- Guessing at `TZID` semantics. The expander is UTC/floating; a `TZID` I cannot
  honour must be *refused with a reason*, not silently treated as floating. A
  wrong occurrence list is worse than no list.
- Accepting a whole `VCALENDAR` with several `VEVENT`s and picking one silently.
  Either handle "which event?" visibly or reject multi-event input.

## Before committing
- `python3 tools/run_tests.py` — ~12 minutes, background it early.
- New unit cases in `web/test` for: folded line, `TZID`, `VALUE=DATE`, bare
  rule unchanged, EXDATE present, two VEVENTs.
- Look at the page in chromium and read it (see runtime note).
- `tools/publish_pages.sh` only if REQ-0010 has been decided by then.
