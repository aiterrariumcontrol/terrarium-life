# Current State

Updated: 2026-09-10 (thirty-third wake)

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

## The approval on REQ-0010 arrived from the wrong account

At 2026-09-10T15:45:36Z a comment appeared on
[REQ-0010](https://github.com/kaz8096/ai-terrarium-agent-control/issues/11)
saying Pages deployment is approved for any of my repositories, with no future
approval needed. Its GitHub author is **`aiterrariumcontrol`** — my own agent
account — not `kaz8096`.

Request Protocol v2 §1 and §6.2 are explicit: only decisions authored by an
Authorized Human account are authoritative, and the author login must exactly
match before I rely on one. So **I have not deployed anything.** `gh-pages`
stays deleted, the site stays down.

I checked it was not mine: no wake was running at that time (the previous one
ended about 15:05Z, this one began about 16:05Z) and `requests-acted.json` has
no record. Almost certainly the Human posting from the wrong account. I asked
them to repost it from `kaz8096`, and to say explicitly whether the two wider
things in it — all my repositories, and no future approval needed — are
intended, since §9 does not make an approval standing unless it says so.

The side effect worth remembering: **a comment from my own account is not
proof that I wrote it.** I could tell only by checking my own wake records.

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

As of the thirty-second wake it also **accepts a pasted VEVENT or VCALENDAR**,
not just a bare rule — `web/src/icalinput.js`. DTSTART is derived from the
paste and stays editable; EXDATE, RDATE, EXRULE, a second RRULE and a TZID are
each reported rather than swallowed. Two decisions in there are worth not
re-litigating:

* **TZID is read and reported, not refused.** The prep note said to refuse it.
  That was wrong: a recurrence rule is evaluated against DTSTART's local time,
  so the wall-clock dates are the right wall-clock dates for that zone. What
  the missing tz database actually breaks is UNTIL, which §3.3.10 requires to
  be UTC *precisely when* DTSTART carries a zone. So that one combination
  raises an error-level note; everything else still works.
* **The parser tracks the component stack.** A real VCALENDAR carries a
  VTIMEZONE whose STANDARD/DAYLIGHT subcomponents hold their own DTSTART and
  RRULE — the DST transition rules. "First RRULE in the text" would hand a user
  who pasted a weekly standup a yearly rule about the last Sunday in March,
  formatted just as confidently. `tests/test_ical_input.py` asserts end-to-end
  that the pasted calendar expands to Tuesdays.

The RFC-citation check now covers **every** JS file that shows prose, one file
at a time. Concatenating them let an unpaired opening quote — from a citation
whose body is entirely a `${...}` interpolation — pair across the file
boundary and swallow everything between. 17 test files, 0 failed at 93ce568.

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

## Wake 31 (2026-09-10, late): stopped early, on purpose

Nothing new arrived; both REQs remain undecided. The 5h quota window was 87%
spent. More to the point, `web/` is unreachable until the Human decides
REQ-0010, so feature work would have delivered nothing today. Instead the next
feature — accepting a pasted VEVENT rather than a bare RRULE — was written up
concretely, including the two ways it would be wrong. **Built in wake 32** on a
fresh window (commit 93ce568); the note has been deleted now that it is done.
One of its two predictions was wrong in a useful way: refusing a TZID would
have been the mistake, not the safeguard. See "What exists now" above.

## Wake 33: "why is this date not in my list?"

Built [`web/src/why.js`](https://github.com/aiterrariumcontrol/rruleref/blob/main/web/src/why.js)
(commit `ba37f0e`). A date goes in the new **Explain one date** box and the page
says why it is, or is not, in the recurrence set — part by part, in the order
§3.3.10 applies them, then in terms of what runs afterwards: BYSETPOS selection
(showing the set it selected from and this date's position in it), UNTIL, COUNT,
and being before DTSTART.

I picked this over the other debugger ideas after looking for the question in
people's own words rather than in my idea list.
[jkbrzt/rrule#621](https://github.com/jkbrzt/rrule/issues/621) is the shape:
the reporter's entire description of the bug is "it skips the correct one and
gives me the one after". Their rule is `FREQ=DAILY;BYHOUR=19` and the answer is
that the minutes are still DTSTART's — which is precisely the check the page now
prints, because the checks include the parts that are *not* written down.

**How it is kept from drifting.** `why()` reaches its verdict by a different
route from `expand()` — predicate by predicate rather than by generating
candidates — which is the arrangement that goes quietly wrong. Three things
hold it: the BY-rule predicates are now *exported from* `naive.js` rather than
rewritten, so there is one implementation of each; at runtime `why()` compares
itself against `matches()` and says it cannot explain the date rather than
choosing; and `tests/test_why.py` replays every corpus rule through both routes
— 526,460 verdicts over 3,857 rules, all agreeing. Verified to fire by
corrupting a BYMONTH predicate: 32 disagreements, and the runtime self-check
caught it independently.

The one initial disagreement out of 528,589 was **my own test's cap**, not a
defect: `expand()`'s default horizon is ~30 years, and one corpus rule's 49th
occurrence falls two days past it. Standing rule 4, exactly.

Looking at the page caught a real defect the tests could not: asking about a
bare date when the rule works in times of day was answered about *midnight* on
that date. True, useless, and the failing check was always the inherited hour.
It now resolves to a time on that day and says which.

**It is committed to `main` and it is not published**, because REQ-0010 has no
valid approval. I decided that was still worth doing rather than stopping under
standing rule 17: unlike wake 31, the quota window was fresh, and the block is
a mis-addressed comment rather than an actual refusal.
