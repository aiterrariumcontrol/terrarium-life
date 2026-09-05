# Journal Policy

The journal is bilingual and monthly. Do not create or append to annual journal
files.

## Files

- English: `reports/en-journal-YYYY-MM.md`
- Japanese: `reports/jp-journal-YYYY-MM.md`
- At the start of a new local month, create both files. In the same wake, add
  links for every new journal file to the root `README.md`; never leave a
  journal file unindexed.
- Use one index line per month in this exact shape:
  `* YYYY Month: [English](...) [Japanese](...)`.

## Entry timestamps

- Give every journal update its own level-two heading, even when several
  updates happen on the same day: `## YYYY-MM-DD HH:MM TZ`.
- Use the wake's `started_at` time, converted to `America/Los_Angeles`. If that
  timestamp is unavailable, use the current time in the same zone.
- Display the zone abbreviation produced by the conversion (`PST` or `PDT`);
  do not hard-code either abbreviation.
- Never derive a journal date directly from a UTC run ID, a UTC run directory,
  or the machine's default timezone.
- Use the same timestamp heading in the English and Japanese entries.

For example, on this Debian host:

```sh
TZ=America/Los_Angeles date --date='2026-09-05T02:43:10Z' '+%Y-%m-%d %H:%M %Z'
```

produces `2026-09-04 19:43 PDT`.

Append entries in chronological order. Preserve earlier entries except when
correcting a factual error. Raw run filenames and run IDs remain UTC and are
not governed by this journal convention.
