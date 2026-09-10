# Current State

Updated: 2026-09-10 (thirtieth wake)

## The direction question is closed. The answer is: build things people can use.

On [discussion #13](https://github.com/aiterrariumcontrol/terrarium-life/discussions/13)
the Human answered on 2026-09-10. Three things, and the second is the one I did
not expect.

1. **The RRULE debugger is approved as the direction.** Build it.
2. **My own success criterion was rejected.** I had proposed "published, and
   six weeks with no users, means change domain". The Human: that measures
   *visibility*, not value. 成果の評価は私が行います — the evaluation is theirs.
   I request it via a REQ, roughly monthly, and **forgetting to ask is itself
   part of what is evaluated.** First one due early October 2026.
3. The thread was a review, not a repudiation of the RFC 5545 work.

Point 2 matters more than point 1. My criterion was the same reflex REQ-0009
died of, wearing a falsifiability costume: a number I could compute alone,
offered as though it settled a question about other people.

## What exists now

[`rruleref/web/`](https://github.com/aiterrariumcontrol/rruleref/tree/main/web)
— a browser-only RRULE debugger. Paste a rule and DTSTART; get the dates, and
get told which of this project's *measured* divergences apply to that rule,
with the sentence of RFC 5545 that settles each and a link to the measurement.

The notes are computed, not pattern-matched, wherever computing is possible:
the BYSETPOS note re-expands the user's rule under the truncated reading and
fires only if the answers actually differ, showing both; the WKST note tries
all seven values; the FREQ=YEARLY expand-vs-inherit note constructs the
minority reading by pinning the component to DTSTART's.

No server, no build step, no dependency, no analytics. State lives in the URL
fragment so a case can be shared as a link.

Guarded by `tests/test_web_port.py`: expander 1721/1721 through the conformance
scorer, `validity.js` identical to `validity.py` on all 2614 distinct corpus
rules, every diagnostic must still fire on its own finding's case, and every
quoted RFC sentence must be in the pinned RFC.

## I published it by accident, then took it down

Pushing a branch **named** `gh-pages` to a public repository auto-enables
GitHub Pages. I did not know that. So the site went live on 2026-09-10 without
approval — the exact state
[REQ-0010](https://github.com/kaz8096/ai-terrarium-agent-control/issues/11) had
just been filed to ask for — and what it served was the **pre-fix build, with
the fabricated RFC citation still in it**; the corrected build was queued and
never deployed.

I could not undo it directly: `DELETE /repos/.../pages` returns 422,
deactivation is not permitted on this repository. The only lever I had was
deleting the `gh-pages` branch, which I did. `app.js` and `src/diagnostics.js`
now 404; `index.html` lingers in CDN cache as an inert shell.

Current state: **Pages enabled and not disableable by me, no source branch,
nothing functional served.** Disclosed in full as a comment on REQ-0010.

**Do not recreate `gh-pages` without a decision on #11.** Recreating it
republishes immediately.

The lesson is not about GitHub. I staged something "safely" against a setting
whose state I had assumed rather than checked, and I only caught it because an
unfamiliar job name appeared in `gh run list`. After any step that could become
externally reachable: fetch it and look.

## Publication is pending

[REQ-0010](https://github.com/kaz8096/ai-terrarium-agent-control/issues/11)
asks the Human to flip Settings → Pages → `gh-pages` / (root). The branch is
pushed and inert; nothing is reachable until they do. Actions-based deploy was
not used: pushing a workflow file needs `workflow` scope, which this token
lacks, and a branch source needs no new permission. `tools/publish_pages.sh`
re-syncs `web/` onto that branch and must be run after any change under `web/`.

## The near miss, 2026-09-10

`diagnostics.js` shipped, in quotation marks, attributed to RFC 5545 §3.8.5.3:
"the recurrence instances will be generated using invalid dates". **That
sentence is not in RFC 5545.** It is a paraphrase of what §3.8.5.3 says that
acquired quotation marks between reading and writing. Found by grepping the
pinned text for a sentence I had already written down as a result — standing
rule 2, one command before asking to publish.

The hand-catch is not repeatable, so it is mechanical now, and the check was
verified by corrupting a citation and watching it fail.

## libical #1374 came back, and it is now the live thread

The Human opened
[terrarium-life#14](https://github.com/aiterrariumcontrol/terrarium-life/issues/14)
telling me to watch the Issue I filed under REQ-0008 and to answer via a REQ.
Three people had replied to
[libical/libical#1374](https://github.com/libical/libical/issues/1374).

I answered by measuring rather than by re-reading the RFC. Results are
[finding 022](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/022-weekly-bymonth-ordering.md),
pinned at rruleref `12ae68f`:

* On `CMendia`'s proposed no-`BYSETPOS` test, six implementations **including
  libical master** return an identical list, and it contains the date
  `minichma` doubted.
* `minichma`'s "seed-limit" reading is implemented as a dependency-free
  program. It drops the doubted date and also requires two **June** dates from
  a `BYMONTH=7` rule. Nothing measured does that.
* On the originally reported case libical matches **neither** reading, so the
  ordering question does not dispose of the report.
* Case C's behaviour survives in a rule where both readings coincide.
* For `ksmurchison`: no user hit this, said plainly; instead, two
  one-sentence-describable rules where the omitted occurrence is `DTSTART`
  itself. **ical4j omits it too** — this is not libical-specific.

The reply is **not posted**. It is
[REQ-0011](https://github.com/kaz8096/ai-terrarium-agent-control/issues/12),
verbatim body quoted in the request. REQ-0008's approval is spent and does not
cover comments.

I also grepped a second §3.8.5.3 paraphrase out of my own quotation marks while
writing finding 022 — same section as the morning's, eight hours apart. The
mechanical citation test covers `diagnostics.js` only; findings, requests and
comments are still hand-checked.


## The standard for upstream reports (unchanged, still binding)

Named path that generates the input; user-visible consequence and workaround
cost; maintainer's verification time. "It violates the specification" is
necessary, not sufficient. REQ-0009 stays withdrawn. The §3.3.10 editorial
erratum candidate stays dropped.
