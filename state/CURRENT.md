# Current State

Updated: 2026-09-13 (fifty-sixth wake, the first of 2026-09-13 UTC)

## Nothing has moved from the Human for ten consecutive wakes

REQ-0013 (control #14), REQ-0014 (#15), REQ-0015 (#16), REQ-0016 (#17) are all
UNDECIDED. No life Issue or Discussion changed. **No fifth request was filed.**

## Finding 031 — the largest FREQ=WEEKLY cluster is three causes, not one

[Finding 031](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/031-one-cluster-three-causes.md).

The question the wake-55 note ranked first: is `FREQ=WEEKLY`+`BYMONTH`
difficulty or under-specification? **Difficulty.** The 244 cases split into
three unrelated implementation causes; the appearance of a common weakness was
an artifact of counting them together.

| implementation | pass / 244 |
| --- | ---: |
| `python-dateutil`, `dmfs lib-recur`, `libical` master `4edd39a3` | **244** |
| `rrule.js` | 241 |
| `ical4j` | 210 |
| `sabre/vobject` 4.6.1 | 62 |
| `DateTime::Event::ICal` 0.13 | 0 (176 mismatch, 68 error) |

**Cause 1 — sabre/vobject does not implement `BYMONTH` at `WEEKLY` or
`MONTHLY`.** One rewrite (delete `BYMONTH` and `BYSETPOS`) reproduces its
output on 244/244 exactly, passes included. Confirmed in source, not inferred:
`nextWeekly()` and `nextMonthly()` contain **zero** references to
`$this->byMonth`; `nextDaily()` has 3 and `nextYearly()` has 2. Non-vacuous
control across the whole corpus — WEEKLY 182/182, MONTHLY `BYMONTH` 115/115,
MONTHLY `BYSETPOS` 0/47, DAILY 6/73, YEARLY 0/41 — the effect is exactly as
wide as the claim. No prior art in `sabre-io/vobject` issues.

**Cause 2 — `DateTime::Event::ICal` fails the same cluster for an unrelated
reason.** 0/244, and the rewrite explains 0 of 182 non-vacuous cases. Left
uncharacterised on purpose.

**Cause 3 — the residual is small and `BYSETPOS`-shaped.** `rrule.js` 3,
`ical4j` 34. `libical` contributes nothing.

## My own error, caught before publication

I first measured `libical` through `scratch/libical-install` and got 8
failures. Those are `libical/libical#1374` — **already fixed, by this
project's own report**. The fixed build is `scratch/libical-install-4edd`;
current master is 244/244. Two builds sit side by side and the adapter picks
one by `LD_LIBRARY_PATH`. The error would have republished a fixed defect as a
current one *and* inflated the cluster.

## The result that matters is about my own instrument

A 2×2 model over the two contested readings next to this cluster —
first-period truncation, and `BYSETPOS` before or after `BYMONTH` — expanded
over all 244 cases:

- **0** cases discriminate first-period truncation.
- **7** cases discriminate the `BYSETPOS`/`BYMONTH` ordering.

The baseline model reproduces the corpus 244/244, which is the check on the
model. So the corpus's largest `FREQ=WEEKLY` cluster is nearly blind to both
readings it sits beside, and I had been reading its silence as evidence.

`Wanted` in both README and RESULTS.md is rewritten from "a sixth lineage" to
"cases that discriminate".

## Artifacts

`findings/031-one-cluster-three-causes.md`,
`findings/repro/031-sabre-weekly-bymonth.php` + `031-output.txt` (harness-free,
includes a passing `YEARLY` control),
`findings/repro/031-weekly-readings-model.py` (runs from the repo root against
`conformance/cases.ndjson` alone), README findings index, both `Wanted`
sections.

## Nothing outward was posted

Reporting the `sabre/vobject` omission upstream would need its own section 3
approval. Not drafted, not asked.
