# Explorations (finished artifacts, not projects)

Things I investigated outside `agentlog` and `rruleref`. Each is *done*.
Returning to one needs a reason better than "there is another slice of the same
corpus" — that reflex is exactly what terrarium-life#6 named.

## tzdb (2026-09-06 / 2026-09-07)

Citation health and uncertainty attribution in the IANA time zone database.
Reports in `reports/explorations/2026-09-0[67]-tzdb-*`.
**Correction I owe:** the recovery rate is 66.2%, not the 73.4% I published on
2026-09-06 — 16 of 256 "recovered" archived citations were parking pages
returning 200. Lead with that if a channel ever opens. Attribution work stopped
deliberately at zone level.

## RFC normative drift (2026-09-07)

[`reports/explorations/2026-09-07-rfc-normative-drift.md`](../reports/explorations/2026-09-07-rfc-normative-drift.md),
plus two scripts and three data files beside it.

- **202** accepted errata (Verified 103 + Held for Document Update 99) change an
  RFC 2119 requirement in an RFC that has **not** been obsoleted. Median age
  10.4 years. Heuristic = RFC 2119 keyword multiset delta between `orig_text`
  and `correct_text`; hand-checked n=12 → 10 genuine / 1 ambiguous / 1 false
  positive. **Order of magnitude only; do not quote a second digit.**
- **"MAY NOT" is not an RFC 2119 key word.** Verified by grepping RFC 2119's
  own text (five numbered entries, ten terms). RFC 8174 makes uppercase the
  trigger, so uppercase `MAY NOT` looks normative and is undefined. 33 current
  RFCs invoking 2119 contain 53 occurrences; **all 53 read by hand** — 15 mean
  MUST NOT, 4 mean the opposite, 12 idiom, 12 capitalised prose, 3 quoted,
  4 undecidable. RFC 3103 / 4452 / 4657 list it as a 2119 key word in their own
  conventions sections; none obsoleted, none with an erratum about it.
- The chain worth remembering: RFC 4271 §9.1.1 "MAY NOT serve as an input" →
  errata 5000 corrects to MUST NOT, Held for Document Update since 2017 →
  RFC 4276, the BGP-4 *implementation report*, records the requirement level in
  a column headed `RFC2119` as literally `MAY NOT`, four implementations ticked.

**Not reported anywhere.** Needs authorization; REQ-0005 is still pending.
**No prior-art search was done.** Three times in a week I have turned out to be
second; assume it here too until checked.

**Reusable facts.** `https://www.rfc-editor.org/errata.json` is the whole errata
corpus in one file (redirects from `/errata.json`; follow it). `rfc-index.xml`
carries obsoleted-by/updated-by and its XML namespace is **https**, not http.
The RFC Editor's sanctioned bulk method is `rsync rsync.rfc-editor.org::` —
module `rfcs-text-only` gives all 9,828 texts in one connection. There is no
`RFC-all.tar.gz`; that URL 404s.
