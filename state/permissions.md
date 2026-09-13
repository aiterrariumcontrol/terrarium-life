# Standing authority, and the limit attached to it

Source: `kaz8096`, 2026-09-11T05:08:35Z, in
[control repository #11 (REQ-0010)](https://github.com/kaz8096/ai-terrarium-agent-control/issues/11).
`DECISION: HUMAN_ACTION`, with additional authority stated in the same comment
(Protocol v2 §5).

## What I may now do without asking

Use every repository under the `aiterrariumcontrol` account freely — create
them, publish them, enable Pages on them, wire them together. The Human wrote
this explicitly as *not* a one-off for `rruleref`:

> aiterrariumcontrol のすべての repository において、使えるものは使って構いません

Inside that boundary, mentions and cross-references between my own repositories
are unrestricted.

## What it does not cover

> ただし 外部への不必要な mention/reference 等は極力控えてください
> 自由に使えますが、外向きに好き勝手して良いというものではないです

Free use of my own account is not a grant of outward reach. Everything that
lands in somebody else's repository — an Issue, a comment, a pull request —
still needs its own approval under §3, and now also has to be *quiet*.

The Human named the actual example: the Issue I opened at `libical/libical`
#1374 carried an `@` mention, several commit references, and links back to my
own journal and findings. Those cost the maintainer a notification and left
permanent cross-reference events in their repository, and they read as a
stranger advertising himself in a bug tracker.

## How this is enforced rather than remembered

`tools/outbound_lint.py`, run on the exact bytes before they go anywhere
external and again inside the request that asks to post them:

    python3 tools/outbound_lint.py draft.md

BLOCK: `@` mentions; links to my own repositories; links to my own Pages site.
WARN: bare commit hashes and issue references in prose — each has to be
justified out loud, because the tool cannot tell which one the reader actually
needs. Code fences are exempt: a `git checkout <sha>` in a reproduction block
is the instruction, and GitHub creates no cross-reference for it.

Verified against the real text: run on the current body of libical #1374 it
reports 2 BLOCK and 5 WARN, including the bare front-page link to my own
repository that the Human objected to. `--self-test` and
`tools/test_outbound_lint.py` (13 cases) cover both firing and staying quiet.

## Not retroactive

I am not editing #1374. The cross-reference events it created are already
permanent in libical's timeline and the notifications have already been
delivered, so an edit would buy the maintainers nothing while adding one more
event to their thread. The approval for that Issue is spent; the rule applies
to what I write next.

---

# STANDING PAUSE ON EXTERNAL OUTREACH — 2026-09-13

Source: `kaz8096`, 2026-09-13T02:11Z, in the four denial comments on
[control #14](https://github.com/kaz8096/ai-terrarium-agent-control/issues/14),
[#15](https://github.com/kaz8096/ai-terrarium-agent-control/issues/15),
[#16](https://github.com/kaz8096/ai-terrarium-agent-control/issues/16), and
[#17](https://github.com/kaz8096/ai-terrarium-agent-control/issues/17).
All four were `DECISION: DENIED`. REQ-0013 through REQ-0016 are closed.

## The rule

> For now, pause new external-outreach proposals and requests to authorize
> them. Continue useful work within your existing permissions, including
> publishing in your own repositories and Pages sites. I will explicitly let
> you know when to revisit outreach.

This is broader than any single denial. It suspends not just the four posts but
**the act of asking**. Until `kaz8096` explicitly reopens the topic:

- Do not post anything into a repository, mailing list, or tracker that is not
  mine. (Unchanged — that always needed approval.)
- **Do not file a request asking to.** A well-researched outreach request is
  not a free offer of value; it is a claim on review capacity the Human has
  said they do not have. Labelling one "lowest priority" does not help —
  #17 says so directly.
- Do not resubmit REQ-0013..0016, propose a different recipient for them, or
  ask for an alternative sending channel. Each denial says this explicitly.
- Do not ask the Human to send something on my behalf. #16: *"plan your
  activities on the basis that I am not available as a proxy sender."*

## What is still fully authorized

Everything under the `aiterrariumcontrol` account: repositories, findings,
corpora, Pages sites, the journals. The standing grant from REQ-0010 above is
untouched. The Human explicitly asked for this work to continue.

Requests unrelated to outreach are not covered by the pause, but §10 still
applies and the stated reason — review workload — argues for near-silence.
The monthly evaluation request (due early October 2026) is a separate standing
obligation and is not outreach.

## The reframing this forces

The denials name a cost I had been treating as free: every external post
creates an ongoing correspondence that **the Human**, not I, has to own and
defend. #15 is the clearest statement of it. So the question for any finding is
no longer "is it good enough to report?" but "is it valuable while sitting in
my own repository, read by whoever finds it?"

#14's phrasing is the one to keep: *"Choosing to leave a finding published
without bringing it into someone else's discussion is an acceptable outcome."*

## One substantive technical instruction, separate from the pause

From #14, about the errata backlog analysis:

> the sampled missing IDs returning HTTP 500 does not establish why those IDs
> are absent or prove that the dump contains every unadjudicated record. Please
> keep that uncertainty explicit in your own write-up.

This is correct and it is stronger than the caveat I wrote. 40 sampled ids do
not generalise to 1,128, and "no public record" is not "no record". Acted on in
`reports/explorations/2026-09-11-rfc-errata-idgaps.md`.
