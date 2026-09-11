# The errata status that stopped being used

*2026-09-11. Data: `https://www.rfc-editor.org/errata.json` (8,039 records, local
copy taken 2026-09-11). Reproduce with `2026-09-11-rfc-errata-hfdu.py`; all
figures below come from the JSON beside it.*

While checking something else I noticed that *Held for Document Update* had
fallen from about 41% of 2010–2012 errata filings to about 14% of recent ones,
and recorded it as unexplained. This note explains it. The short version: a
dated IESG statement changed both who dispositions editorial errata and what
they are told to choose, and the data shows the effect landing exactly when the
statement says it should.

## The decline is entirely editorial

Splitting adjudicated errata (excluding still-pending `Reported`) by type puts
the whole effect on one side:

| filed | Editorial, HFDU | Technical, HFDU |
|---|---|---|
| ≤2009 | 51.1% (n=1089) | 25.6% (n=1056) |
| 2010–2012 | 51.3% (n=696) | 28.8% (n=553) |
| 2013–2015 | 38.3% (n=473) | 17.0% (n=505) |
| 2016–2018 | 44.3% (n=377) | 27.2% (n=438) |
| 2019–2021 | 33.5% (n=412) | 33.3% (n=486) |
| 2022–2026 | **10.6%** (n=530) | 23.8% (n=684) |

Technical errata wander between 17% and 33% with no trend. Editorial errata sit
near 50% for a decade and then collapse. Where they went is Verified: the
editorial Verified share rises from 40.5% (≤2009) to 80.6% (2022–2026).

Two confounds die here. It is not the growing pool of unadjudicated errata
inflating denominators — these rates already exclude `Reported`. And it is not
the changing technical/editorial mix — the mix does shift (editorial falls from
50.8% to 34.3% of filings), but the effect is *within* type, and recent
editorial errata are now held *less* often than technical ones, reversing the
historical order.

## It is not maturation either

The remaining worry is that HFDU is simply decided slowly, so recent
would-be-HFDU errata are still sitting in `Reported`. That confound can be
bounded without any timing assumption: ask what the rate would be if **every**
still-pending editorial erratum of a year eventually became HFDU.

| filed | editorial total | still `Reported` | HFDU now | ceiling if all pending → HFDU |
|---|---|---|---|---|
| 2018 | 154 | 11 | 42.2% | 49.4% |
| 2020 | 154 | 9 | 34.4% | 40.3% |
| 2021 | 159 | 13 | 22.6% | 30.8% |
| 2022 | 162 | 8 | 6.2% | **11.1%** |
| 2024 | 119 | 6 | 11.8% | **16.8%** |
| 2026 | 92 | 7 | 5.4% | **13.0%** |

Every recent ceiling is below every earlier observed value. Maturation cannot
produce this gap.

I had intended to check disposition lag directly and could not: `update_date` is
not a disposition date. 5,157 of 8,039 records — 64% of the corpus — carry the
single timestamp 2019-09-10, a bulk re-touch. Any lag computed from that field
is meaningless, and I discarded the check rather than report it.

## What changed: who decides, and what they are told to choose

Editorial errata that were Verified or held, by the year they were filed, split
by whether the recorded verifier is RPC staff (including the generic "RFC
Editor" identity) or an Area Director:

| filed | n | dispositioned by RPC | HFDU rate, RPC | HFDU rate, AD | HFDU overall |
|---|---|---|---|---|---|
| 2018 | 130 | 7.7% | 0.0% | 54.2% | 50.0% |
| 2019 | 108 | 9.3% | 0.0% | 50.5% | 45.4% |
| 2020 | 114 | 6.1% | 0.0% | 49.5% | 46.5% |
| **2021** | 134 | **21.6%** | 13.8% | 30.5% | 26.9% |
| **2022** | 142 | **70.4%** | 2.0% | 19.5% | 7.0% |
| 2023 | 88 | 58.0% | 7.8% | 43.2% | 22.7% |
| 2024 | 98 | 69.4% | 8.8% | 26.7% | 14.3% |
| 2025 | 73 | 69.9% | 9.8% | 9.1% | 9.6% |
| 2026 | 82 | 70.7% | 3.4% | 12.5% | 6.1% |

Two things move at once in 2021. Editorial errata stop going to Area Directors
and start going to the RPC, and the RPC almost never holds — its HFDU rate runs
0–14% throughout, against roughly 50% for ADs before 2021. The ADs' own rate
also falls, from ~50% to 26.5% across the whole 2021–2026 era.

Decomposing the fall in the overall editorial HFDU rate from 47.8% (2016–2020,
n=563) to 14.9% (2021–2026, n=617), a drop of 32.9 points:

- new routing mix with the old per-handler rates gives 23.0% — routing alone
  accounts for **24.7 points, 75% of the drop**;
- old routing mix with the new per-handler rates gives 25.1% — the per-handler
  rate change alone accounts for **22.7 points, 69%**.

These do not sum to 100% and should not: both changed together, and the
decomposition is not additive. The honest reading is that routing is the larger
single factor and neither alone explains it.

## The document

Both arms correspond to clauses in one text: the IESG statement [*IESG
Processing of RFC Errata for the IETF
Stream*](https://www.ietf.org/about/groups/iesg/statements/processing-errata-ietf-stream/),
published **2021-05-07**.

On routing:

> When an editorial erratum is reported, the RFC Editor will do an initial
> review and handle errata that are clearly editorial in nature. If the erratum
> cannot be handled by the RFC Editor, the AD will be asked to review.

And on what the reviewer should pick:

> Grammar corrections and typographical errors should be classified as Verified.
>
> Changes that are stylistic issues or simply make things read better should be
> classified as Hold for Document Update.

The first clause predicts the routing shift; the second predicts the drop in the
ADs' own hold rate, since it tells any reviewer to Verify the typos that
previously might have been held. The statement is dated May 2021 and the RPC
share jumps that same year, from 6.1% in 2020 to 21.6% in 2021 to 70.4% in 2022.

## Limits

- **I did not establish what the pre-2021 guidance said.** The datatracker
  history and versions pages for this statement both returned 404 to me. So I
  can say the 2021 statement contains clauses that predict the observed shift
  and that the shift begins in 2021; I cannot show from a source that these
  clauses were *new* in that revision. The timing fit is tight, but it is a fit,
  not a demonstrated cause.
- The RPC/AD split uses the `verifier_name` string, with a fixed list of RPC
  staff names plus the generic "RFC Editor" identity. A staff member not on that
  list is counted as AD/other, which would understate the routing shift.
- `verifier_name` records who is credited, not necessarily who reviewed; the
  statement itself notes ADs may delegate.
- 2023 is a visible exception — the AD hold rate returns to 43.2% for one year.
  I have no explanation for it.

## Why this matters beyond the curiosity

The [residual note](2026-09-11-rfc-errata-residual.md) treats an erratum's
status as a property of the erratum. For editorial errata it is substantially a
property of **when it was filed**, because that determines who dispositioned it
under which rule. Comparing editorial hold rates across the 2021 boundary — or
reading a fall in HFDU as a change in the quality of submissions — measures the
IESG statement rather than the errata.
