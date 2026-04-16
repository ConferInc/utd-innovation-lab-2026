# Subodh week-8 logs

---

## Email to Confer team

**Subject:** Group 4B – Subodh Week 8/9 Update

Hi Hermes and Confer Team,

Please find my weekly update below for Week 8/9.

- Completed the Week 8 event pipeline integration coverage in `4B/week8/tests/test_event_pipeline_integration.py`, including required flows for upsert, dedup, search, today filter, recurring filter, sponsorship rendering, and KB ingestion.
- Implemented and validated bounded LRU caching with TTL in `4B/week8/events/services/event_query_cache.py` (`max_size=500` default).
- Added the missing shared-cache verification in `4B/week8/tests/test_event_query_cache.py` to confirm `get_shared_event_query_cache(max_size=...)` respects max size and evicts least-recently-used entries.
- Connected database events to the knowledge base via `ingest_events()` in `4B/week8/knowledge_base/ingestion.py` and wired it at the end of seeding in `4B/week8/scripts/seed_from_scraped_json.py`.
- Hardened test portability/import paths and completed targeted validation for Subodh-owned coverage: 14 passing tests across cache and pipeline integration suites.

Also, the event was amazing. Thank you so much for the opportunity and for the felicitation.

Thanks,  
Subodh Krishna Nikumbh  
Group 4B

---

## Short EOW bullets (Subodh only)

- Completed Week 8 event pipeline integration tests in `4B/week8/tests/test_event_pipeline_integration.py` and verified required flows (upsert, dedup, search, today, recurring, sponsorship, KB ingest).
- Implemented and validated `EventQueryCache` LRU behavior with bounded size (`max_size=500` default) and TTL in `4B/week8/events/services/event_query_cache.py`.
- Added shared-cache test path in `4B/week8/tests/test_event_query_cache.py` for `get_shared_event_query_cache(max_size=...)` and LRU eviction.
- Connected seeded DB events to KB via `ingest_events()` in `4B/week8/knowledge_base/ingestion.py` and wired seeding in `4B/week8/scripts/seed_from_scraped_json.py`.
- Hardened test imports/patching; targeted validation: **14 passed** (cache + pipeline integration suites).

---

## Reference — Subodh Week 8 scope (from assignment)

- End-to-end integration test: mock scraper JSON → `upsert_events()` → `EventService` → API response.
- `EventQueryCache`: max size + LRU; `get_shared_event_query_cache(max_size)`.
- `ingest_events()` in KB; run after seed from scraped JSON.
- In-memory SQLite per test run.
