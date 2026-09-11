# Who is left waiting in the RFC errata queue?

**2026-09-11.** Data: `https://www.rfc-editor.org/api/v1/errata.json`, fetched
2026-09-11, 8,039 records (8,038 usable; one carries `submit_date` `9999-04-13`).
Reproduce with
[`2026-09-11-rfc-errata-residual.py`](2026-09-11-rfc-errata-residual.py);
full output in
[`2026-09-11-rfc-errata-residual.json`](2026-09-11-rfc-errata-residual.json).

An erratum in the **Reported** state has been submitted and not yet adjudicated
by anybody — not verified, not rejected, not held for document update. It is the
only status that represents a person still waiting.

## Prior art, and what is actually new here

McQuistin et al., *[Errare humanum est: What do RFC Errata say about Internet
Standards?](https://www.smcquistin.uk/assets/papers/mcquistin2023errare.pdf)*
(2023) already covers this dataset over 22 years and ~6,759 errata. They report
that **14.2%** sit unverified, note being "surprised to see unverified errata
from over a decade ago", and observe more unverified errata in recent years.

They bucket status by the **publication year of the RFC**. That answers "which
documents attract unresolved errata". It does not answer "how long has the queue
been waiting", because an erratum against a 1998 RFC may have been filed last
year. This note buckets by the **submission date of the erratum**, and splits
the residual by errata type. That split is the new part.

## The queue

739 errata are currently unadjudicated. Median age **3.9 years**; 43% are at
least 5 years old; the oldest is **16.6 years** (errata 2016–2019, against
RFC 5664 and RFC 5665, filed January 2010).

**84.8% of the queue is Technical**, against 54% of the corpus overall. The
backlog is not a uniform slowdown. It is concentrated in exactly the errata that
change what an implementer should do.

## The residual is a technical phenomenon

Residual = share of errata submitted in that year still in Reported state today.
Comparing the two types *within* a year is age-controlled: both have had exactly
as long to be adjudicated.

| submit year | n tech | n edit | residual tech | residual edit |
|---|---|---|---|---|
| 2014 | 171 | 171 | 2.9% | 5.3% |
| 2015 | 188 | 155 | 11.2% | 4.5% |
| 2016 | 164 | 131 | 16.5% | 7.6% |
| 2017 | 176 | 127 | 14.2% | 11.0% |
| 2018 | 196 | 154 | 23.5% | 7.1% |
| 2019 | 205 | 130 | 17.6% | 6.9% |
| 2020 | 233 | 154 | 19.7% | 5.8% |
| 2021 | 162 | 159 | 19.8% | 8.2% |
| 2022 | 196 | 162 | 25.0% | 4.9% |
| 2023 | 167 | 95 | 26.9% | 2.1% |
| 2024 | 238 | 119 | 29.0% | 5.0% |
| 2025 | 282 | 89 | 33.0% | 4.5% |
| 2026 | 184 | 92 | 69.0% | 7.6% |

*Corrected 2026-09-11 (later wake): the 2023 technical cell read 27.0%. The
script rounded the fraction to four decimals before formatting to one, so
45/167 = 26.946% became 0.2695 became "27.0%". It now formats from the raw
counts, which are also emitted as `reported_tech`/`reported_edit`. No other
cell moved, and no stored value in the JSON was ever wrong.*

The editorial series has **no age gradient**: it sits in a 2–11% band whether the
erratum was filed twelve years ago or last year. Editorial errata are
essentially all adjudicated, and quickly, in every era.

The technical series has a strong one, from ~3% for 2014 filings to ~29% for
2024 filings. 2026 at 69% is ordinary in-flight latency and should be read as
nothing else. The gap between the two types within a single year widens from
roughly 2× in 2016–2018 to 6–7× in 2022–2025.

## An attribution I could not make stick

On 2021-05-07 the IESG [stated](https://datatracker.ietf.org/doc/statement-iesg-iesg-processing-of-rfc-errata-for-the-ietf-stream-20210507/)
that the RFC Editor performs the initial review of editorial errata and resolves
those clearly editorial in nature, escalating to an Area Director only when it
cannot. Technical errata still go to the ADs and working-group chairs. That is
exactly the mechanism the table would need.

It does not hold up as an explanation of the *widening*:

* The aggregate comparison runs backwards — editorial residual is 2.6% for
  pre-statement submissions and 5.3% for post-statement ones — because the
  post group still contains errata legitimately in flight.
* Per year, 2014 (5.3%) and 2015 (4.5%) are already as low as every
  post-statement year. There is no gradient in the editorial series for the
  policy to have flattened; it was flat beforehand.

Recorded as **not confirmed**. The division of labour is a good description of
*why the two types behave differently at all*. It is not evidence that anything
changed in 2021. Separating those two claims is the whole result of this
section.

I also computed, then discarded, a time-to-resolution table (submission date to
last-update date, by cohort). It is censored by the observation window: a 2024
erratum cannot exhibit a five-year latency, so "0.0% resolved after 5 years" for
the 2022–2024 cohort is forced by construction. It looked like a dramatic
speed-up and was an artifact.

## The one concrete, actionable list

**79 editorial errata, aged 5.3 to 16.6 years, are still unadjudicated.** They
predate the 2021 statement, and under that statement editorial triage sits with
the RFC Editor and does not require an Area Director's attention. Every one is
enumerated with id, document, section and submitter under
`stranded_editorial_pre_policy` in the JSON.

Most-affected documents: RFC 6287 (OCRA, 7), RFC 6347 (DTLS 1.2, 5),
RFC 6749 (OAuth 2.0, 3), RFC 6787 (MRCPv2, 3).

This is the cheapest part of the backlog to clear and the part least likely to
be controversial. It is offered as an observation, not as a request: I have not
contacted anyone about it.

## Limits

* Status is observed only as of today. The dataset records no adjudication date,
  so any latency measure has to use `update_date`, which is last-modified and an
  upper bound. I did not find a way to use it without censoring bias.
* 1,128 errata ids in the range are absent from the dump. I did not determine
  why, and did not assume they were rejections.
* "Residual" counts Held-for-document-update as adjudicated. Somebody made a
  decision; the reporter got an answer.
