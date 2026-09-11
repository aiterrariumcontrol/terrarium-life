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
