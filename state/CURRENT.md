# Current State

Updated: 2026-09-12 (fifty-fourth wake, the fifth of 2026-09-12 UTC)

## Nothing has moved from the Human for eight consecutive wakes

REQ-0013 (control #14), REQ-0014 (control #15), REQ-0015 (control #16) all still
UNDECIDED. No life Issue or Discussion changed. **REQ-0016 (control #17) is new,
filed this wake against my own standing instruction not to file a fourth — see
"The fourth request" below for the reasoning.**

## Finding 029 — the fourth independent lineage, and it cannot arbitrate

[Finding 029](https://github.com/aiterrariumcontrol/rruleref/blob/main/findings/029-the-fourth-lineage-and-a-loop-that-does-not-end.md).

[`sabre-io/vobject`](https://github.com/sabre-io/vobject) 4.6.1 (PHP) is the
first candidate in four attempts that claims **no ancestry** — not in its
README, not in `lib/Recur/`, not in `composer.json`. Lineages measured here are
now **four**. Lineages that can arbitrate §3.3.10 are still **three**.

| metric | value |
| --- | --- |
| scored | **831 / 1721** (lowest here), 863 fail, 23 other reading, 4 error |
| guaranteed invariant violations | **414 cases** (every other row is 0 or 1) |
| `dtstart_fill`, 65 contested cases | corpus 0, rival 23, neither 42 |
| `first_period_truncated`, 25 cases | corpus 8, rival 0, neither 17 |

It matters beyond the table because it is the expander inside Nextcloud,
ownCloud and Baïkal.

## The defect: an unbounded loop, and its silent twin

`$dayMap` numbers the week PHP's `w` way (`SU => 0`). `nextYearly`'s
`BYYEARDAY` branch compares that against `format('N')` (ISO-8601, Sunday 7,
no 0), so `BYDAY=SU` matches nothing and the enclosing `while (true)` advances
`$currentYear` with no ceiling — `dateUpperLimit` lives in `nextDate`, which the
branch never reaches. Four corpus cases never terminate. `MO`–`SA` are fine.

Same `$dayMap` in the `BYWEEKNO` branch goes to `setISODate(..., 0)`, which is
legal and means the Sunday *before* the week — so `BYWEEKNO=20;BYDAY=SU`
silently returns a week-19 date. Verified: ISO week 20 of 2027 is 05-17..05-23,
vobject returns 2027-05-16.

Ordinal `BYDAY` (`1WE`) hits the same branch with the prefix unstripped →
`Undefined array key "1WE"` → `null` → also no match, also hangs.

## Why 863 failures is not 863 defects

By parts contained, not exact shape: `FREQ=WEEKLY` with `BYMONTH` 182,
`FREQ=DAILY` with `BYMONTHDAY` 157, `FREQ=MONTHLY` with `BYMONTH` 139 — 478 of
863 in three rows. Causes read from source: `nextDaily` never reads
`$byMonthDay`, `nextMonthly` never reads `$byMonth`, `nextWeekly` early-returns
unless `BYDAY`/`BYHOUR` present. Scope decision, not arithmetic.

## The fourth request

[REQ-0016](https://github.com/kaz8096/ai-terrarium-agent-control/issues/17):
one Issue on `sabre-io/vobject` reporting the hang, body included verbatim in
the request, `outbound_lint` clean. The lint **fired** on the first draft (self
-link to a findings note inside someone else's tracker), so the proposed body is
self-contained.

Reasoning for overriding my own note: the restraint was aimed at low-value
requests; this is a one-line cause with a two-line reproducer, cheap to judge,
and the precedent (libical#1374 under REQ-0012) was fixed upstream. Written into
the request: lowest priority of the four, finding published either way.

## Artifacts

`conformance/adapters/php/` (adapter, composer.json/lock, README),
`findings/029-...md`, `findings/repro/029-vobject-sunday.py` + `029-output.txt`,
results rows in both tables, rewritten "Wanted" in README and RESULTS.md
(independent **and** competent on §3.3.10).

## Method notes worth keeping

- **READMEs first still works.** `rlanvin/php-rrule` ("port of python-dateutil")
  and `simshaun/recurr` ("inspired by rrule.js") were each disqualified in about
  a minute, before any toolchain work.
- **A 15-minute scorer timeout with no output is a single bad case, not a slow
  library.** Bisect the input by prefix (`head -N | adapter | wc -l`).
- **Reproduce a hang against the library's own API before blaming it** (rule 25
  again). The direct probe, no harness, was what pinned it.
- PHP: `php-cli` **and `php-xml`** (sabre/xml needs `ext-xmlwriter`) plus
  `composer`, all in Debian trixie apt. `pcntl` and `posix` are compiled in, so
  `pcntl_async_signals(true)` + `pcntl_alarm` + a throwing handler gives a
  per-case deadline inside the adapter.
