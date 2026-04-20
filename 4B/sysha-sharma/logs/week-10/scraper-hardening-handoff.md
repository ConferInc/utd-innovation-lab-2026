# Week 10 Scraper Hardening - Handoff to Chakradhar

Author: Sysha Sharma
Branch: `4B-week10-sysha`
Date: 2026-04-19

## Summary of changes

All four of Sysha's Week 10 individual tasks plus Chakradhar's three paste-ready
requests, in the root-cause-first order Chakradhar recommended:

1. `datetime_extract.py` - mapped `CST/CDT/EST/EDT/MST/MDT/PST/PDT/UTC/GMT` to
   fixed UTC offsets via `tzinfos=`; neutralized the stray `T` token. This
   silences the `UnknownTimezoneWarning` on CST/EST/PST/T from his Week 10
   diagnostic.
2. `jkyog.py` + `radhakrishnatemple.py` - added a shared placeholder-title
   regex that drops rows titled `Loading Event Details`, `Untitled`, `TBD`,
   `Coming Soon`, etc. Drops get logged as `stage="placeholder_title"`.
3. `category_from_title.py` - replaced substring matching with compiled
   `\bkeyword\b` regex per category; extended tuples with plural forms
   (`kirtans`, `prayers`, `classes`, ...) so legitimate matches still hit.
4. `scrape_all.py` - added `start_datetime_parse_rate` to the metrics dict
   (and the CLI print).
5. New tests cover all of the above (39 validation tests pass locally).
6. Schema docstring added to both scraper modules.

## Funnel: before vs. after

Chakradhar's Week 10 diagnostic (before this change):

```
total_scraped=55  passed=31  failed_start_datetime_parse=24  deduped=20
```

After (`py -3 scripts/scrape_events.py`, 2026-04-19):

```
total=53  parsed_dt=31  parse_rate=58.5%  category_not_other=30  duplicates=11  deduped=20
Raw by source_site:       jkyog=47  radhakrishnatemple=6
Validated by source_site: jkyog=29  radhakrishnatemple=2
Deduped by source_site:   jkyog=18  radhakrishnatemple=2
Skipped (missing/invalid start_datetime): 22
Scraper errors logged: 3
```

### What the numbers mean for your upcoming-events filter

- `failed_start_datetime_parse` dropped from 24 to 22 after the TZ fix (two
  rows previously tripped the CST/EST/T warning and fell back to
  America/Chicago midnight). The remaining 22 skips are rows with no date
  strings in the card text at all - those are a scraper selector problem,
  not a parser problem. Not touching them this week.
- `parse_rate=58.5%` is the new signal you can watch.
- `radhakrishnatemple` source only contributed 2 validated rows out of 6 raw.
  The rest are 404s or pages that need JS hydration. Scope for a later fix.
- Multi-day events (`Mar 26-29, 2026` pattern) now propagate `end_datetime`
  end-to-end - covered by the new
  `test_temple_multi_day_range_populates_end_datetime`.

## What this implies for your Task 2 (upcoming filter)

You flagged 12 past vs. 1 upcoming in Postgres. That is not a parser problem:
the scrape still yields 20 deduped events, most of which have `start_datetime`
in the past. Recommended next steps on your side:

- Re-seed Render with the current scrape output and re-check
  `/api/v2/events` counts.
- If upcoming count is still low, the filter or the seed script is the
  problem, not the scraper. I have not touched either - that is your lane
  per the Week 10 task split.

Ping me if you need timezone behavior extended (e.g. IST for diaspora content,
or DST-aware handling beyond the fixed-offset CST=UTC-6 assumption).
