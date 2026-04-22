# Week 8 Scraper Pipeline -> Week 10 Cleanup: Task 2 Upcoming Events Filter Investigation

Author: Chakradhar Gummakonda
Date: 2026-04-22
Branch: `4B-week10-chakradhar`

## Objective

Investigate why `GET /api/v2/events` returns a small number of upcoming events
even though multiple events are scraped and stored. Determine whether the low
count is caused by historical-heavy source data, by the upcoming filter, or by
the seed pipeline. Fix filter/seed only if a bug is confirmed.

## Method

1. Ran scraper fresh against both temple sources (`python -m scripts.scrape_events`).
2. Seeded live Postgres with `seed_from_scraped_json`.
3. Queried Postgres to classify date/state buckets.
4. Compared DB results with live API responses.

## Scrape funnel (2026-04-22)

From `data/scrape-run-2026-04-22.log`:

- Total scraped: **56**
- Passed `start_datetime` parse: **41**
- Failed `start_datetime` parse (missing/invalid): **15**
- Deduped events written to JSON: **30**
- Parse rate: **73.2%**
- Category not `other`: **38**
- Duplicates removed before JSON: **11**

By source site:
- Raw: `jkyog=50`, `radhakrishnatemple=6`
- Validated: `jkyog=39`, `radhakrishnatemple=2`
- Deduped: `jkyog=28`, `radhakrishnatemple=2`

## Database state (after seed)

Seed output:
- `inserted=0, updated=30, failed=0, input_count=30, pruned_deleted=0`

Postgres counts:
- `total_events = 21`
- `past_events (start_datetime < now()) = 15`
- `future_events (start_datetime >= now()) = 6`
- `missing_start_datetime = 0`

Observation:
- 30 JSON rows -> 21 DB rows via upsert dedup (`dedup_key` + source uniqueness).
- This collapse is expected dedup behavior, not a seed bug.

## Additional SQL checks (production)

Executed to validate filter edge buckets:

- `recurring_count = 0`
- `currently_running = 0`
- `placeholder_like = 11` (rows where `EXTRACT(SECOND FROM start_datetime) != 0`)

Interpretation:
- No recurring rows currently exist in DB.
- No non-recurring rows are currently active with `start < now <= end`.
- 11 rows have odd-second timestamps, consistent with inferred/fallback datetime parsing rather than clean schedule-time extraction.

## Sample `start_datetime` values (from scrape output)

Future (6 rows — eligible for upcoming):

- `2026-04-26T15:30:00Z` (Sunday Satsang)
- `2026-05-28T13:30:00Z` (Youth Leadership Workshop 2026)
- `2026-07-02T16:30:00Z` (Sri Venkateswara Pran Pratistha Mahotsavam)
- `2026-07-04T12:00:00Z` (RKT Spiritual Retreat & Family Camp 2026)
- `2026-08-21T16:00:00Z` (JKYog Dallas Spiritual Retreat 2026)
- `2026-10-14T05:30:35Z` (Swami Mukundananda at UNT)

Past samples (15+ rows — not eligible for upcoming):

- `2026-04-19T05:30:28Z`
- `2026-04-17T12:00:00Z`
- `2026-04-15T23:15:00Z`
- `2026-03-14T15:00:24Z`
- `2026-02-13T15:30:00Z`
- `2025-09-24T20:00:43Z`
- `2025-04-14T23:30:33Z`
- `2024-10-05T16:30:35Z`
- `2024-06-01T01:30:38Z`

## Live API results

Base: `https://jkyog-whatsapp-bot-week4-ffuk.onrender.com`

| Endpoint | Response count |
|---|---:|
| `GET /api/v2/events?limit=20` | **6** |
| `GET /api/v2/events/today` | 0 |
| `GET /api/v2/events/recurring` | 0 |

## Code-level validation

### Upcoming filter logic

`get_upcoming_events` in `4B/week8/events/storage/event_storage.py` includes:
- one-off upcoming: `is_recurring = False` and `(start >= now OR end >= now)`
- recurring active: `is_recurring = True` and `(end is null OR end >= now)`

This logic is correct and matches intended behavior.

### Why recurring path is empty in production

Current scrapers hardcode non-recurring output:
- `4B/week8/events/scrapers/jkyog.py` (line 220): `"is_recurring": False`
- `4B/week8/events/scrapers/jkyog.py` (line 392): `"is_recurring": False`
- `4B/week8/events/scrapers/radhakrishnatemple.py` (line 396): `"is_recurring": False`

So the recurring branch of the filter is currently unused with production data.

### Timestamp quality caveat source

In `4B/week8/events/scrapers/datetime_extract.py`, fuzzy parsing uses:
- line 210: `dateutil_parser.parse(... default=now_local ...)`
- line 280: `dateutil_parser.parse(... default=now_local ...)`

When source text lacks explicit time, inherited `now_local` components can leak into parsed output (including non-zero seconds), explaining `placeholder_like = 11`.

## Conclusion

The upcoming-events filter and seed pipeline are functioning correctly for current data.

However, low `/events` count is not only a data-recency issue. It is driven by two factors:

1. Historical-heavy source content (15 past vs 6 future in DB after this run).
2. Zero recurring rows in DB (`recurring_count=0`) because scraper outputs currently hardcode `is_recurring=False`.

So the final diagnosis is:
- **No bug in filter logic**
- **No bug in seed logic**
- **Primary production gap is scraper-side recurrence and timestamp quality**


## Evidence / artifacts

- Scrape run log: `4B/week8/data/scrape-run-2026-04-22.log`
- Investigation doc: `4B/week8/data/task2-upcoming-analysis.md`
- Seed output (terminal): `inserted=0, updated=30, failed=0`
- SQL outputs:
  - `total=21`, `past=15`, `future=6`, `missing=0`
  - `recurring_count=0`
  - `currently_running=0`
  - `placeholder_like=11`
- Live API captures:
  - `/events?limit=20` returned 6 events
  - `/today` returned 0
  - `/recurring` returned 0
