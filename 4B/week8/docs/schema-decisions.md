# Week 8 Schema Decisions - Locked Canonical Contract

**Owner:** Chakradhar Gummakonda (Team 4B)  
**Alignment:** Chanakya (Team 4A)  
**Status:** Locked

## Canonical event core fields

`id`, `name`, `subtitle`, `category`, `event_type`, `is_recurring`, `recurrence_text`, `start_datetime`, `end_datetime`, `timezone`, `location_name`, `address`, `city`, `state`, `postal_code`, `country`, `description`, `registration_required`, `registration_status`, `registration_url`, `contact_email`, `contact_phone`, `parking_notes`, `transportation_notes`, `food_info`, `price`, `sponsorship_tiers`, `source_url`, `source_site`, `source_page_type`, `scraped_at`, `source_confidence`, `notes`

## Canonical nested shapes

- `price`: `{amount, notes}`
- `sponsorship_tiers[]`: `{tier_name, price, description}`

## Canonical escalation response fields

`success`, `ticket_id`, `queue_status`, `assigned_volunteer`, `next_state`, `message_for_user`, `priority`, `errors`

## Backward-compat normalization (ingestion-only)

Legacy keys are accepted only at validation/storage boundaries and normalized into canonical keys before persistence:

| Legacy key | Canonical key |
|---|---|
| `location` | `location_name` |
| `special_notes` | `notes` |
| `sponsorship_data` | `sponsorship_tiers` |
| `recurrence_pattern` | `recurrence_text` |

Legacy sponsorship tier keys are normalized as:

| Legacy tier key | Canonical tier key |
|---|---|
| `name` | `tier_name` |
| `amount` | `price` |
| `link` | `description` |

## Validation assumptions

- `recurrence_text` is treated as the machine-readable recurrence value for recurring events and must be one of the allowed values (`daily`, `weekdays`, `weekends`, `weekly:<day>`, `monthly`, `annually`).
- If `is_recurring=true` and `recurrence_text` is missing or invalid, validation fails at write time.
- Category, registration status, and priority values are strict enumerations validated before write.

## SQLite fallback

- Local fallback uses `DATABASE_URL=sqlite:///./local_dev.db`.
- SQLAlchemy SQLite engine is configured with `connect_args={"check_same_thread": False}`.
