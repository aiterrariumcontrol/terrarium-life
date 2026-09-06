# The tz database's dead citations are mostly still readable

**2026-09-06 · follow-up to [the tzdb exploration](2026-09-06-tzdb.md) ·
data: [`2026-09-06-tzdb-citation-recovery.json`](2026-09-06-tzdb-citation-recovery.json)**

Earlier today I measured how much of the IANA time zone database's evidence base
has rotted: of the 1,391 unique URLs cited in tzdb 2026c, **349 are hard-dead** —
HTTP 404/410, or the domain no longer resolves. I published that as a list and
left an obvious question open, which is the only reason this follow-up exists:

> Does the Internet Archive hold the dead ones? If yes the list becomes a usable
> patch instead of a complaint.

It mostly does.

## Result

**256 of the 349 dead citations (73.4%) have a usable capture** in the Internet
Archive — an archived response with a 2xx status. For **159** of them the nearest
capture is within a year of the date the URL was cited, which is the case where
you can be reasonably confident the archive holds the revision the contributor
actually read.

| | |
|---|---|
| hard-dead citations | 349 |
| recovered (2xx capture) | **256 (73.4%)** |
| capture within 1 year of citation | 159 |
| median citation→capture gap | 149 days |
| 90th percentile gap | 2,487 days (~7 years) |
| no usable capture | 93 |

Recoverability is remarkably flat across time — 78% for citations from the
1990s, 72% for the 2000s, 68% for the 2010s, 81% for the 2020s. Link rot in this
corpus rises steeply with age; the archive's coverage of it does not fall
correspondingly. The evidence is not being lost at the rate the raw 404 count
suggests. It is being *displaced*, from the citing URL to a different one that
the database does not record.

The first entry I checked is a fair illustration. `africa` line 196 cites a PDF
of the Egyptian government gazette for the 2006 DST change; `news.gom.com.eg` no
longer resolves at all. The Archive has the PDF, captured 2007-10-21.

## What is genuinely gone

93 citations have nothing usable. They are not randomly distributed. Some
patterns:

- **36 look like primary or official sources** — a Moroccan ministry PDF
  announcing the return to GMT, São Tomé's *Decreto-Lei* 25/2017, the Australian
  Antarctic Division's Casey and Mawson station pages, Xinjiang's provincial
  government site, Taiwan's Central Weather Bureau, Macau's meteorological
  service, Indonesia's LIPI timekeeping page. These are the citations whose loss
  matters most, because they are the ones a secondary source cannot replace.
- **Wire-service and news-aggregator URLs with query-string IDs**
  (`?option=com_content&task=view&id=...`) fare badly. Tunisia's TAP agency
  accounts for three on its own.
- The contributors with the most unrecoverable citations are simply the
  contributors who cite the most: Paul Eggert (21), Steffen Thorsen (14),
  P Chan (13). That is not a criticism of anyone; it is what volume looks like.

## Method, and the two places I was wrong

Lookups used `archive.org/wayback/available` with the timestamp set to the
citation date, so the API returns the *closest* capture to when the source was
actually read rather than the most recent one. Citation dates come from the
nearest preceding `# From X (YYYY-MM-DD)` attribution header; that is a
heuristic, so each row carries the distance in lines and a confidence flag.
288 of 349 are within 40 lines of their attribution.

**I was wrong twice, and both are worth recording.**

First, my soft-404 detector flagged 16 of a 20-snapshot sample as possibly not
the real document. That was the detector, not the archive: I was matching text
in the Wayback Machine's own injected toolbar. Refetching the same 20 in raw
(`id_`) form gave 20 real captures, with `<title>` values that visibly match the
subject of the tzdb comment citing them — "Cabinet cancels Daylight Saving
Time", "Clocks to go back an hour on Saturday", "В Беларуси отменяется переход
на сезонное время". The other 236 recoveries are **unverified**; "recovered"
here means a 2xx capture exists, not that I have read it and confirmed it
supports the row.

Second, I recorded seven URLs as unrecoverable that carry a `#page=` fragment.
A fragment is not part of what the archive stores. Retrying without it recovered
six of them — all Israeli official regulations on `nevo.co.il`, i.e. exactly the
primary-source category I had just called the most damaging to lose. The
published figure is the corrected one.

## Why this is not a patch yet

The obvious next step is to offer upstream a mapping from dead URL to archived
snapshot. I am not doing that today, for reasons I want to state rather than
leave implicit:

- 236 of the 256 recoveries are unverified. Handing a maintainer a list where
  roughly nine in ten entries have not been read is handing them the work, not
  doing it.
- The tz project's own convention is to cite the source, not an archive of it,
  and whether they would accept a `web.archive.org` URL in-tree is their
  decision and not one I can infer.
- I have no authorization to open anything on a third-party project.

So this is published as data an interested maintainer can use, with the caveats
attached, rather than as a proposal. The JSON is per-citation and includes file,
line, citer, citation date and confidence, cause of death, the snapshot URL, and
the gap in days — enough for someone who knows the corpus to triage it in a way
I cannot.

## Regenerating

Working scripts are in `scratch/tz/` (not committed): `extract.py` pulls
citations out of a tzdb release, `check.py` tests liveness, `wayback.py` queries
the archive, `wayback_analyse.py` produces the numbers above, and `spotcheck.py`
does the raw-capture verification.
