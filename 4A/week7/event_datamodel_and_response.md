# Week 7 — Event Data Model & Response Templates
**Owner:** Chanakya Sairam Varma Alluri  
**Project:** JKYog / Radha Krishna Temple event ingestion for bot + WhatsApp responses  
**Date:** 2026-04-01  

---

## 1) Canonical Event JSON Schema

The schema below is designed to normalize event data from JKYog / Radha Krishna Temple pages into one canonical structure that can support:
- event search
- WhatsApp responses
- logistics questions
- sponsorship questions
- recurring event handling
- source traceability back to the website

```json
{
  "id": "string",
  "name": "string",
  "subtitle": "string | null",
  "category": "festival | retreat | satsang | youth | class | workshop | special_event | other",
  "event_type": "in_person | online | hybrid | unknown",
  "is_recurring": "boolean",
  "recurrence_text": "string | null",

  "start_datetime": "ISO-8601 string | null",
  "end_datetime": "ISO-8601 string | null",
  "timezone": "string | null",

  "location_name": "string | null",
  "address": "string | null",
  "city": "string | null",
  "state": "string | null",
  "postal_code": "string | null",
  "country": "string | null",
  "location_notes": "string | null",

  "description": "string | null",
  "highlights": ["string"],
  "audience": ["string"],

  "registration_required": "boolean | null",
  "registration_status": "open | closed | unknown",
  "registration_url": "string | null",

  "contact_email": "string | null",
  "contact_phone": "string | null",

  "parking_notes": "string | null",
  "transportation_notes": "string | null",
  "food_info": "string | null",
  "accommodation_info": "string | null",

  "pricing": {
    "adult_price_usd": "number | null",
    "child_price_usd": "number | null",
    "notes": "string | null"
  },

  "sponsorship_tiers": [
    {
      "tier_name": "string",
      "price_usd": "number | null",
      "price_inr": "number | null",
      "description": "string | null"
    }
  ],

  "tags": ["string"],
  "source_url": "string",
  "source_site": "jkyog.org | radhakrishnatemple.net",
  "source_page_type": "event_detail | upcoming_events | sponsorship_page | logistics_page",

  "scraped_at": "ISO-8601 string",
  "source_confidence": "high | medium | low",
  "notes": "string | null"
}
```

### Field design notes
- `id`: stable internal key such as `jkyog-dallas-holi-mela-2026`
- `subtitle`: useful for pages that show a short descriptor under the event title
- `category`: normalized bucket for routing user queries
- `event_type`: inferred from page labels like “In-person” or “Online”
- `is_recurring` + `recurrence_text`: helps answer “Does this happen every week/year?”
- `parking_notes`, `food_info`, `transportation_notes`, `accommodation_info`: dedicated logistics fields so the bot does not hide important practical details inside one long description
- `sponsorship_tiers`: array to support event-specific sponsorship / seva options
- `source_confidence`: marks whether a value came directly from a detailed event page or only from a summary/calendar listing

---

## 2) Sample JSON for real events from the website

Below are normalized samples based on the public event/calendar pages and related event/sponsorship pages.

### Sample 1 — Dallas Holi Mela

```json
{
  "id": "jkyog-dallas-holi-mela-2026",
  "name": "Dallas Holi Mela",
  "subtitle": "Holika dahan & Phoolon ki Holi Celebration",
  "category": "festival",
  "event_type": "in_person",
  "is_recurring": true,
  "recurrence_text": "Annual Holi festival style event",
  "start_datetime": "2026-03-01T10:30:00-06:00",
  "end_datetime": "2026-03-07T22:00:00-06:00",
  "timezone": "CST",
  "location_name": "Radha Krishna Temple of Dallas",
  "address": "1450 North Watters Road",
  "city": "Allen",
  "state": "TX",
  "postal_code": "75013",
  "country": "USA",
  "location_notes": null,
  "description": "Celebrate the Vibrant Festival of Holi in Dallas! Join us for a joyful day filled with colours, music, dancing, and traditional festivities. Experience the true essence of Holi with family and friends.",
  "highlights": [
    "Holi celebration",
    "Music",
    "Dancing",
    "Traditional festivities"
  ],
  "audience": ["families", "general_public"],
  "registration_required": null,
  "registration_status": "unknown",
  "registration_url": null,
  "contact_email": "[email protected]",
  "contact_phone": "5085966841",
  "parking_notes": null,
  "transportation_notes": null,
  "food_info": null,
  "accommodation_info": null,
  "pricing": {
    "adult_price_usd": null,
    "child_price_usd": null,
    "notes": null
  },
  "sponsorship_tiers": [],
  "tags": ["holi", "festival", "dallas", "allen", "in_person"],
  "source_url": "https://www.jkyog.org/retreat/festival-of-holi-in-dallas",
  "source_site": "jkyog.org",
  "source_page_type": "event_detail",
  "scraped_at": "2026-04-01T00:00:00Z",
  "source_confidence": "high",
  "notes": "Date/time also appears in JKYog upcoming events calendar."
}
```

### Sample 2 — Mahashivratri retreat entry from the upcoming events calendar

```json
{
  "id": "jkyog-mahashivratri-retreat-2026-dallas",
  "name": "Mahashivratri",
  "subtitle": null,
  "category": "retreat",
  "event_type": "in_person",
  "is_recurring": true,
  "recurrence_text": "Likely annual festival/retreat entry tied to Mahashivratri",
  "start_datetime": "2026-02-13T09:30:00-06:00",
  "end_datetime": "2026-02-16T20:30:00-06:00",
  "timezone": "CST",
  "location_name": "Radha Krishna Temple of Dallas",
  "address": "1450 North Watters Road",
  "city": "Allen",
  "state": "TX",
  "postal_code": "75013",
  "country": "USA",
  "location_notes": null,
  "description": null,
  "highlights": [],
  "audience": ["general_public"],
  "registration_required": null,
  "registration_status": "unknown",
  "registration_url": null,
  "contact_email": null,
  "contact_phone": null,
  "parking_notes": null,
  "transportation_notes": null,
  "food_info": null,
  "accommodation_info": null,
  "pricing": {
    "adult_price_usd": null,
    "child_price_usd": null,
    "notes": "Calendar listing only"
  },
  "sponsorship_tiers": [],
  "tags": ["mahashivratri", "retreat", "dallas", "allen", "in_person"],
  "source_url": "https://www.jkyog.org/upcoming_events",
  "source_site": "jkyog.org",
  "source_page_type": "upcoming_events",
  "scraped_at": "2026-04-01T00:00:00Z",
  "source_confidence": "medium",
  "notes": "This record is from the aggregated upcoming events calendar and contains fewer details than a full event page."
}
```

### Sample 3 — Dallas Spiritual Retreat / Family Camp

```json
{
  "id": "jkyog-dallas-spiritual-retreat-family-camp",
  "name": "Dallas Spiritual Retreat with Swami Mukundananda",
  "subtitle": "JKYog Family Camp",
  "category": "retreat",
  "event_type": "in_person",
  "is_recurring": true,
  "recurrence_text": "Recurring retreat/family camp program",
  "start_datetime": null,
  "end_datetime": null,
  "timezone": null,
  "location_name": "Hyatt Place Garland / Radha Krishna Temple of Dallas",
  "address": "5101 N President George Bush Hwy, Garland, TX 75040, USA",
  "city": "Garland",
  "state": "TX",
  "postal_code": "75040",
  "country": "USA",
  "location_notes": "Page lists hotel contact/location and separately mentions transportation between hotel and temple.",
  "description": "Immerse in three days of bliss with yoga, meditation, kirtans, discourses by Swami Mukundananda, festival celebrations, and special programs for kids & youth!",
  "highlights": [
    "Yoga",
    "Meditation",
    "Kirtans",
    "Discourses",
    "Festival celebrations",
    "Kids and youth programs"
  ],
  "audience": ["families", "kids", "youth", "general_public"],
  "registration_required": true,
  "registration_status": "closed",
  "registration_url": null,
  "contact_email": "[email protected]",
  "contact_phone": "(469) 795-9130",
  "parking_notes": null,
  "transportation_notes": "Guests are responsible for arranging their own transportation from the airport to their hotel, as well as between the hotel and the temple.",
  "food_info": "Three meals (breakfast, lunch, dinner) are covered by the retreat registration fee.",
  "accommodation_info": "Accommodation and all three meals for the entire duration of the retreat are included in the fees. Private room available at an additional charge.",
  "pricing": {
    "adult_price_usd": 275,
    "child_price_usd": 140,
    "notes": "Page lists both in-person and online pricing and states children are ages 4–12."
  },
  "sponsorship_tiers": [
    {
      "tier_name": "Grand Sponsor",
      "price_usd": 2501,
      "price_inr": 50001,
      "description": "Seva opportunity listed on Family Camp sponsorship page"
    },
    {
      "tier_name": "Daily Yajman",
      "price_usd": 500,
      "price_inr": 10000,
      "description": "Seva opportunity listed on Family Camp sponsorship page"
    },
    {
      "tier_name": "Daily Lunch",
      "price_usd": 251,
      "price_inr": 5001,
      "description": "Meal sponsorship"
    },
    {
      "tier_name": "Daily Dinner",
      "price_usd": 251,
      "price_inr": 5001,
      "description": "Meal sponsorship"
    },
    {
      "tier_name": "Daily Breakfast",
      "price_usd": 151,
      "price_inr": 3001,
      "description": "Meal sponsorship"
    },
    {
      "tier_name": "Guru Purnima Daavat for Maharaj Ji",
      "price_usd": 101,
      "price_inr": 2001,
      "description": "Seva opportunity"
    },
    {
      "tier_name": "Pagadi for Maharaj Ji",
      "price_usd": 101,
      "price_inr": 2001,
      "description": "Seva opportunity"
    },
    {
      "tier_name": "Fruits & Flowers",
      "price_usd": 101,
      "price_inr": 2001,
      "description": "Seva opportunity"
    },
    {
      "tier_name": "Radha Krishna Abhishek",
      "price_usd": 51,
      "price_inr": 1001,
      "description": "Seva opportunity"
    },
    {
      "tier_name": "Maharaj Ji Jhoolan (Fri)",
      "price_usd": 51,
      "price_inr": 1000,
      "description": "Seva opportunity"
    },
    {
      "tier_name": "Aarti",
      "price_usd": 25,
      "price_inr": 501,
      "description": "Seva opportunity"
    }
  ],
  "tags": ["retreat", "family_camp", "swami_mukundananda", "kids", "youth"],
  "source_url": "https://www.jkyog.org/dallas-spiritual-retreat-with-swami-mukundananda",
  "source_site": "jkyog.org",
  "source_page_type": "event_detail",
  "scraped_at": "2026-04-01T00:00:00Z",
  "source_confidence": "high",
  "notes": "Sponsorship tiers supplemented from the related Family Camp sevas page."
}
```

### Sample 4 — Bhakti Kirtan Retreat entry visible on the retreat page

```json
{
  "id": "jkyog-bhakti-kirtan-retreat-2025",
  "name": "Bhakti Kirtan Retreat",
  "subtitle": null,
  "category": "retreat",
  "event_type": "in_person",
  "is_recurring": false,
  "recurrence_text": null,
  "start_datetime": "2025-04-18T00:00:00-05:00",
  "end_datetime": "2025-04-20T23:59:59-05:00",
  "timezone": "CDT",
  "location_name": null,
  "address": null,
  "city": null,
  "state": null,
  "postal_code": null,
  "country": null,
  "location_notes": null,
  "description": "Join us for the inspiring Bhakti Kirtan Retreat with Swami Mukundananda from April 18–20, 2025.",
  "highlights": ["Bhakti", "Kirtan", "Retreat"],
  "audience": ["general_public"],
  "registration_required": true,
  "registration_status": "unknown",
  "registration_url": null,
  "contact_email": null,
  "contact_phone": null,
  "parking_notes": null,
  "transportation_notes": null,
  "food_info": null,
  "accommodation_info": null,
  "pricing": {
    "adult_price_usd": null,
    "child_price_usd": null,
    "notes": null
  },
  "sponsorship_tiers": [],
  "tags": ["bhakti", "kirtan", "retreat"],
  "source_url": "https://www.jkyog.org/dallas-spiritual-retreat-with-swami-mukundananda",
  "source_site": "jkyog.org",
  "source_page_type": "event_detail",
  "scraped_at": "2026-04-01T00:00:00Z",
  "source_confidence": "medium",
  "notes": "Visible in the 'Upcoming Events with Swamiji' section on the retreat page."
}
```

---

## 3) WhatsApp response templates
These templates are designed to remain safely under WhatsApp’s 4096-character message limit.

### A. Single event result
```text
📅 *{{name}}*
{{subtitle_line}}

🕒 {{date_time_text}}
📍 {{location_text}}

{{description_short}}

{{pricing_line}}
{{food_line}}
{{parking_line}}
{{registration_line}}

{{contact_line}}
🔗 More info: {{source_url}}
```

**Rendering rules**
- `subtitle_line`: include only if subtitle exists
- `pricing_line`: include only when pricing is known
- `food_line`: include only when food info exists
- `parking_line`: include only when parking notes exist
- `registration_line`: e.g. `Registration: Required` / `Registration: Closed` / `Registration: Check website`
- `contact_line`: include phone or email if available

---

### B. Event list result
```text
Here are the events I found for *{{query}}*:

1) *{{event_1_name}}*  
   🕒 {{event_1_time}}  
   📍 {{event_1_location}}

2) *{{event_2_name}}*  
   🕒 {{event_2_time}}  
   📍 {{event_2_location}}

3) *{{event_3_name}}*  
   🕒 {{event_3_time}}  
   📍 {{event_3_location}}

Reply with:
- *1*, *2*, or *3* for full details
- *logistics* for parking/food/travel info
- *sponsorship* for seva or sponsorship options
```

**Bot behavior**
- Cap to 3–5 events per message
- If more than 5 matches, send the first 5 and ask a narrowing follow-up

---

### C. No results
```text
I couldn’t find any matching events for *{{query}}* right now.

You can try:
- an event name (example: *Holi*, *retreat*, *family camp*)
- a month or date
- a category like *festival*, *weekly satsang*, or *youth*

If you want, I can also show the latest upcoming events.
```

---

### D. Sponsorship info
```text
🙏 *Sponsorship / Seva Information for {{name}}*

Available options:
{{sponsorship_bullets}}

If you want, I can also help with:
- event dates and venue
- food / accommodation details
- registration / contact information
```

**Example bullet rendering**
```text
• Grand Sponsor — $2501 / Rs.50,001
• Daily Yajman — $500 / Rs.10,000
• Daily Lunch — $251 / Rs.5,001
• Daily Dinner — $251 / Rs.5,001
```

---

### E. Logistics response
```text
🚗 *Logistics for {{name}}*

📍 Venue: {{location_text}}
🅿️ Parking: {{parking_text}}
🍽️ Food: {{food_text}}
🛏️ Stay: {{accommodation_text}}
🚕 Transportation: {{transportation_text}}

{{registration_line}}
{{contact_line}}
🔗 More info: {{source_url}}
```

**Fallback logic**
- If a logistics field is missing, say `Not listed on the event page`
- Never fabricate parking or food details

---

## 4) Data source mapping
This table documents where each field should be captured from on the website.

| Schema field | Website source | Where it comes from on the website | Notes |
|---|---|---|---|
| `id` | Internal/generated | Generated from normalized event slug + year | Not scraped directly |
| `name` | Event page / calendar | Event title heading or event name in upcoming events calendar | Primary display field |
| `subtitle` | Event detail page | Subtitle / short descriptor under title | Example: Holi page subtitle |
| `category` | Inferred | Derived from title, page label, or section taxonomy | Controlled vocabulary |
| `event_type` | Event page / calendar | Labels such as “In-person” / “Online” | Direct scrape where shown |
| `is_recurring` | Inferred | Determined from event pattern or repeated annual/weekly occurrence | Mark as inferred |
| `recurrence_text` | Event page / temple programs page | Weekly/annual wording if explicitly mentioned | Otherwise null |
| `start_datetime` | Event page / calendar | Date-time row on event page or date range in upcoming events calendar | Convert to ISO-8601 |
| `end_datetime` | Event page / calendar | Same as above | Convert to ISO-8601 |
| `timezone` | Event page / calendar | Timezone marker like CST / EST / IST | Preserve source timezone |
| `location_name` | Event page / calendar | Venue line | Example: Radha Krishna Temple of Dallas |
| `address` | Event page / calendar | Full address line | Parse into structured parts where possible |
| `city` / `state` / `postal_code` / `country` | Event page / calendar | Parsed from venue/address string | Derived from address |
| `location_notes` | Event page / logistics section | Extra venue instructions or hotel/temple split notes | Useful for handoff replies |
| `description` | Event detail page | “Description of the Event” block or event intro text | Keep concise version for WhatsApp |
| `highlights` | Event detail page | Highlights/features section | Optional array |
| `audience` | Event detail page | Kids, youth, family, public wording | Inferred but grounded |
| `registration_required` | Event page / FAQ | Registration text, forms, FAQ | Boolean |
| `registration_status` | Event page | Text such as “registration is closed” | Normalize to enum |
| `registration_url` | Event page | Register button/form link | If directly exposed |
| `contact_email` | Event page | Contact row / email text | Direct scrape |
| `contact_phone` | Event page | Contact row / phone text | Direct scrape |
| `parking_notes` | Logistics / visitor / event-specific page | Parking instructions on dedicated page or event note | Null if not listed |
| `transportation_notes` | Event detail page | Transport policy section | Example: airport-hotel-temple note |
| `food_info` | FAQ / event details / retreat pricing section | Meals included, prasad, food booth references | Keep literal summary |
| `accommodation_info` | Event details / terms | Stay included, hotel info, private room info | Important for retreat queries |
| `pricing` | Event detail page | Pricing or fee block | Store as structured object |
| `sponsorship_tiers` | Sponsorship / seva page | Dedicated sponsorship table or donation listing | Array of tiers |
| `tags` | Internal/inferred | Derived from event metadata | Improves retrieval |
| `source_url` | Scrape metadata | URL of source page | Required for traceability |
| `source_site` | Scrape metadata | Domain name | Useful for trust/source grouping |
| `source_page_type` | Scrape metadata | Event detail / upcoming events / sponsorship / logistics | Helps confidence scoring |
| `scraped_at` | Scrape metadata | Timestamp of extraction | Operational field |
| `source_confidence` | Internal quality field | Based on page richness and directness | High for detail pages; medium for calendar-only entries |
| `notes` | Internal | Any extraction caveat | Example: “calendar only” |

---

## 5) Recommended extraction logic

### Priority order for extraction
1. **Event detail page**  
   Best source for title, subtitle, description, contact info, venue, logistics, pricing
2. **Upcoming events calendar**  
   Best backup source for date/time and venue when a detail page is missing
3. **Sponsorship / seva page**  
   Best source for `sponsorship_tiers`
4. **Temple logistics / visitor pages**  
   Best source for parking and arrival guidance when event page lacks logistics

### Normalization rules
- Convert all event dates to ISO-8601, but keep original source timezone
- Preserve raw descriptive text in notes if parsing is uncertain
- Do not invent missing values; set them to `null`
- Use `source_confidence = medium` when only a calendar listing is available
- Keep sponsorship tiers in an array so the bot can answer partial queries like “daily lunch sponsorship”

---

## 6) Bot-facing recommendations

### Recommended response strategy
- For “What events are coming up?” → use compact event list template
- For “Tell me about Holi” → use single event template
- For “What are the sponsorship options?” → use sponsorship template
- For “Parking / food / accommodation?” → use logistics template

### Recommended fallback strategy
- If multiple events match the same keyword, ask the user to choose one
- If logistics are missing, explicitly say they are not listed on the current page
- If sponsorship info exists on a separate page, merge it into the event response but preserve the source URL list internally

---

## 7) Submission note
This deliverable provides:
- a canonical event schema
- 4 sample event JSON records from real JKYog / temple web pages
- WhatsApp-safe response templates
- a field-to-source mapping for scraping and normalization

