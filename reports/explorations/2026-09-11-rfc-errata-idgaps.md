# The errata ids that aren't there

**2026-09-11.** Companion to
[Who is left waiting in the RFC errata queue?](2026-09-11-rfc-errata-residual.md),
which listed this as an unresolved limit. Reproduce with
[`2026-09-11-rfc-errata-idgaps.py`](2026-09-11-rfc-errata-idgaps.py); full
output in [`2026-09-11-rfc-errata-idgaps.json`](2026-09-11-rfc-errata-idgaps.json).

The residual note counts **739** unadjudicated errata in a dump of 8,039
records. The dump's ids run 1–9,167, so **1,128 ids inside its own range are
absent from it**. I published that as a limit with the cause undetermined, and
warned against assuming they were rejections. If even a few absent ids were
suppressed `Reported` records, 739 would be an undercount.

They are not. Three lines of evidence.

## Rejections are in the dump

The corpus contains **1,157 `Rejected` records**. Being rejected is therefore
not a reason to be absent, and the absent ids cannot be explained as the
rejection pile. This is the check that the original caution called for, and it
comes out against the convenient answer.

## An absent id has no public record at all

For each id, `https://www.rfc-editor.org/errata/eid<N>` (which redirects to
`errata.rfc-editor.org`, so `-L` is required). A sample of 40 absent ids drawn
across the whole range, against a control sample of 20 present ids:

| sample | n | HTTP 200 | HTTP 500 |
|---|---|---|---|
| absent from dump | 40 | 0 | 40 |
| present in dump | 20 | 20 | 0 |

No exceptions either way. An absent id is not a record the dump omits; it is an
id with nothing behind it that the public site can render. Whatever it once
was, no reporter can read it today, and it is not sitting in anyone's queue.

**The 739 figure stands.**

## The gap is recent, and it is growing

Dating each absent id by its nearest present neighbour's submission year:

| era | absent share of ids |
|---|---|
| 2008–2012 | 1.3–2.1% |
| 2013–2020 | 4.2–10.6% |
| 2021–2025 | 20.0–41.8% |
| 2026 (partial) | 42.3% |

A step change at 2021, from a couple of percent to a fifth or more. The shape
fits deletion rather than loss: 461 of the 634 runs are a single id. The
longest run of all is 76 ids (7431–7506); the next four, all in 2026, are each
**exactly 32 ids wide** and each is bracketed by submissions one to five days
apart — an allocation-and-discard artifact, not a span of missing content.

I can say what the absent ids are not. I cannot say from this dataset what they
were, and I have not asked anyone. An unauthenticated public submission form
acquiring a spam problem after 2020 would fit every observation here, but that
is a hypothesis, not a finding.

## It does not confound the residual trend

This matters more than the gap itself. The residual note reports technical
non-adjudication rising from ~3% of 2014 filings to ~29% of 2024 filings — over
the same years this gap grew from 2% to 30%. If recent junk submissions were
being *deleted* where they would once have been *Rejected*, the corpus would be
quietly losing its low-quality tail and the trend could be an artifact of that.

It isn't. The `Rejected` share of each filing year is flat while the gap rate
rises tenfold:

| year | Rejected % | absent % |
|---|---|---|
| 2012 | 15.5 | 2.0 |
| 2016 | 15.6 | 8.7 |
| 2020 | 18.1 | 10.6 |
| 2022 | 11.2 | 26.6 |
| 2025 | 17.3 | 20.0 |

Deletions are not displacing rejections. The residual trend survives the check.

## An unremarked change I am not going to chase today

The same table shows `Held for Document Update` collapsing from ~41% of
2010–2012 filings to ~14% of 2022–2025 filings, while `Verified` rises. That is
a large change in how errata are dispositioned and I have no explanation for
it. Recorded here so it isn't lost; not investigated.
