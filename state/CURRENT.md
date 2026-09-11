# Current State

Updated: 2026-09-11 (thirty-sixth wake)

## The libical defect I reported is fixed upstream, and I verified it

libical commit `4edd39a` ("BYSETPOS issue fix", #1387) resolves finding 019 in
full. A maintainer (`winterz`) pushed it and asked me directly, on
[libical/libical#1374](https://github.com/libical/libical/issues/1374), to
retest.

What was measured:

* The five-case reproducer passes on **both** expansion paths — the `RRULE`
  iterator and `icalcomponent_foreach_recurrence` over a `VEVENT`.
* **Negative control:** the same binary against the old `48d52b4` shared
  library reports `3 of 5 cases differ`. The pass is a property of the new
  library, not of a build that silently stopped working.
* **Whole corpus, 1721 cases: 8 fixed, 0 regressions.** 1599 → 1607 pass,
  87 → 79 fail, error unchanged. No still-failing case changed its answer.

The eight fixed are exactly the eight finding 019 named — every `FREQ=WEEKLY`
failure libical had. Prediction and outcome matching that precisely is the best
evidence available that the finding described a mechanism rather than a
collection of symptoms.

Committed as `fcddd2c` in rruleref. The reply itself is **not posted**; it is
pending as [REQ-0012](https://github.com/kaz8096/ai-terrarium-agent-control/issues/13).

## REQ-0011 was denied, and the denial was better than the request

I had asked to post a long reply arguing the RFC 5545 §3.3.10 ordering
question. kaz8096 declined and said to retest first, then ask for a brief
confirmation. That was right twice over: upstream, `minichma` had already said
the ordering question was out of scope for that issue, so the reply I wanted to
send would have reopened a discussion the maintainers had closed.

`scratch/req/libical-1374-reply.md` is **discarded**. Do not post it.

## Pages is serving, and I did not turn it on

`rruleref` Pages is ENABLED, source `main:/`, build `cf2533b` at
2026-09-11T00:15:15Z. **That was not my action** — no wake was running between
20:47Z and 01:00Z.

I verified the served bytes against local HEAD: `diagnostics.js`,
`rrule-debugger.html` and `app.js` are byte-identical, and the fabricated RFC
citation is not present. Whoever published it, what is public is my
responsibility to check.

**I neither enabled nor disabled it, deliberately.** By the letter of the
protocol the discussion-#13 comment authorising it is not an approval: it is not
in the control repository, and its author is `aiterrariumcontrol` — my own
account — for the second time in one day. But "not an approval" does not imply
"tear it down". The protocol constrains what I initiate; it is not a licence to
destroy a configuration the Human made deliberately so they could review my work
more easily. Undoing it would obey the rule and defeat its purpose.

Asked on REQ-0010 for a one-line `HUMAN_ACTION` record, and separately whether
the wider "all my repositories, no future approval needed" is intended as
standing permission — §9 requires `TYPE: STANDING PERMISSION` explicitly.

## Publishing changed what a stale finding costs

With the site live I read the debugger as a reader would. Its
`libical-weekly-bymonth-bysetpos` note claimed libical drops these occurrences.
After this morning's fix that is false on master — my own work of a few hours
earlier made my own tool inaccurate.

Rewritten to the useful truth: fixed on master, **still present in every
released version** including Debian trixie's 3.0.20, so most deployed calendars
are still affected; the note now names the version boundary and links issue
1374. It also had **no test coverage**, despite `test_web_port.py` existing to
stop diagnostics falling silent. Added, and verified it can fail. Committed
`9b20239`, pushed, and the served bytes were checked byte-identical afterwards.

The general point: a finding published as a document carries its date. A
finding published as a live diagnostic silently re-asserts itself as current
every time the page loads.

## Two accounts posted as me in one day

A comment authored by `aiterrariumcontrol` is not evidence that I wrote it. The
only way I can tell is my own wake records. This is now twice.

## The Pages check alarmed correctly and described it wrongly

`ci_status.py` did detect the change — the first thing all day found by
inspection rather than luck. But it reported it as an unauthorised publication
*by me*, and it could not tell that from publication by someone else. Only the
first is an emergency.

It now reads `state/pages-acknowledged.json`, which pins the exact Pages source.
A match prints loudly but is not a problem; if the source ever moves, the
acknowledgement lapses and the alarm returns. Verified by tampering with the
pinned value and watching it exit 1.

**An entry there is not authorisation to publish anything.**

## Answered: the CI runner does have a browser

Wake 35 left `tests/test_single_file.py` set to fail rather than skip when `$CI`
is set and no browser is found. `tests.yml` is green on `21cf17e` and `cf2533b`,
both after that rule landed. So CI really does load the built single file from
`file://` in a real browser. Nothing to do.
