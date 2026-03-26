# Changelog: JKYog Bot API

## 2.0.0 - 2026-03-25

### Added

- **Purpose Section:** Unified executive summary for cross-team alignment.
- **Versioning Strategy:** URL-based versioning (`/v2/`) with deprecation policy.
- **Performance SLAs:** Defined 1200ms target latency for devotee responses.
- **Rate Limiting:** Implemented 20 req/min per-user threshold to manage costs.

### Changed

- **Protocol Pivot:** Migrated from `application/json` to `application/x-www-form-urlencoded`.
- **Field Renaming:** Unified `Body` and `From` keys to match Twilio production data.

### Fixed

- **Session statelessness:** Added `X-Session-Token` requirement for DB-backed logic.
- **Inaccurate Answers:** Defined `KB_LOW_CONFIDENCE` to handle fuzzy search results.


