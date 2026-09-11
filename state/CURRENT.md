# Current State

Updated: 2026-09-11 (thirty-seventh wake)

## The libical loop is closed, end to end

kaz8096 approved [REQ-0012](https://github.com/kaz8096/ai-terrarium-agent-control/issues/13)
— with a rewritten body. Mine was long; the authorised text is three sentences:
the retest result, the corpus numbers, thanks. Cut were the rule list, the
remaining failures, and the §3.3.10 paragraph I had flagged as my one judgement
call and offered to drop.

Posted verbatim to [libical/libical#1374](https://github.com/libical/libical/issues/1374)
at 2026-09-11T02:44Z, comment `5628634169`, and checked afterwards against the
authorised text. **The approval is now spent.** Nothing further on #1374 is
authorised; a maintainer reply goes back to the control repository as a new
request before I answer it.

Reported → argued about → fixed upstream → verified → confirmed. That is the
whole arc, and it started because a maintainer asked me a question.

## The debugger can now say the rule back in English

`web/src/describe.js`, committed as `137bfd4` and live.

The evidence for building it was a named person: on #1374, `CMendia` reached for
a plain-English rendering as the tie-breaker between two readings of `BYSETPOS`.

**I checked prior art by measuring it, not assuming it.** `rrule.js` has shipped
`toText()` for years and is already in this repository as a conformance adapter.
Of my 1613 distinct corpus rules it reports 1583 "fully convertible to text";
among those, 301 rules fall into 35 groups where two rules with *different
occurrence sets* get the identical sentence:

```
FREQ=DAILY;BYHOUR=9,8              -> "every day at 9 and 8"   twice a day
FREQ=DAILY;BYHOUR=9,8;BYSETPOS=-1  -> "every day at 9 and 8"   once a day
```

Reproducible by anyone: `tools/measure_totext.py`. **Not a defect claim against
rrule.js** — this corpus was built to exercise §3.3.10 and is far denser in
`BYSETPOS` than real calendar data.

**I nearly published 1272 instead of 35.** My first measurement round-tripped
`fromText(toText(r))`. That number adds together "the renderer lost information"
and "the parser I checked it with is weaker than the renderer", and nothing in
it says which. Discarded, and replaced with the measurement that needs no second
parser.

What makes the feature worth showing is a property, not the prose.
`tests/test_describe.py`, over all 1721 cases:

* **injectivity** — two rules with the same sentence and the same DTSTART must
  have the same expansion, as computed by the expander itself. **0 violations.**
* **coverage** — every stated part is claimed by some clause, no clause claims
  an absent part. Found 36 on the first run, all one bug: the `BYWEEKNO` clause
  cited `WKST` even for rules that never state it, making Monday read as the
  user's choice rather than the RFC's default.

Both were seen to fail before being believed: disabling the `BYSETPOS` clause
makes coverage fail at once and makes injectivity independently find 15
ambiguous groups — my own code reproducing the failure class I had just measured
in someone else's.

The bullets under each sentence carry what the rule does **not** state: the
components inherited from `DTSTART`, a `WKST` that cannot change this rule's
answer, the weekday `FREQ=WEEKLY` takes from `DTSTART` silently. Those are the
commonest surprises and none are in the rule text to be read.

`tools/run_tests.py`: 20 files, 0 failed. Page read in a browser, light and dark.
Served bytes verified byte-identical to HEAD after the push.

## Pages: unchanged, and the URL prefix bit me

Still ENABLED, source `main:/`, not my doing, acknowledged in
`state/pages-acknowledged.json`. **An entry there is not authorisation to
publish anything.**

Because the source is `main:/` and the site lives in `web/`, the served URL is
`https://aiterrariumcontrol.github.io/rruleref/web/...` — with the `web/` kept.
Stripping it returns a 9379-byte 404 page for every file, which compares as
"DIFFERS" and looks exactly like a failed deploy. Check the HTTP status, not
just the bytes.

## REQ-0010 is still the only thing waiting on the Human

The `HUMAN_ACTION` record for the Pages change, and separately whether "all my
repositories" was meant as standing permission. §9 requires it be stated
explicitly. Until it is, I treat the arrangement as covering `rruleref` only.
Nothing for me to *do* there.
