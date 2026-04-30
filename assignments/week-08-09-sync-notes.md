# Minutes of Meeting (MOM)

**Project:** DCP x JKYog WhatsApp Bot  
**Date:** April 9  
**Attendees:** Sysha Sharma, Chanakya Alluri, Chakradhar Reddy, Rohan Bhargav, Nikita Pal, Rujul Shukla, Leena Hussein  

---

## Agenda
- Schema alignment and field finalization  
- Escalation flow updates  
- Render deployment status  
- Preparation for JKYog event (Wednesday)  

---

## Key Discussion Points

### 1. Schema Finalization
- Chanakya and Chakradhar finalized the event schema and aligned it across teams.
- Key fields include:
  - ID (integer), name, subtitle, category, event type  
  - Recurrence fields, date/time, timezone  
  - Location details (address, city, state, postal code, country)  
  - Registration details (required, status, URL)  
  - Contact info, parking notes, transportation notes, food info  
  - Price, sponsorship tiers, source metadata, notes

- Schema document uploaded in GitHub (`week 8` folder → schema alignment `.md`). 

---

### 2. Pricing & Nested Fields
- Simplified pricing structure:
  - Removed separate USD/INR fields  
  - Introduced unified nested pricing structure  
- Sponsorship tiers include:
  - Tier name, price, description  
- Multiple price tiers (e.g., VIP) will be handled within the same nested field.

---

### 3. Escalation Flow Updates
- Removed `estimated wait time` field  
- Final escalation fields:
  - success, ticket ID, queue status  
  - assigned volunteer, next state  
  - message to user, priority, errors

---

### 4. Schema Lock Decision
- Team agreed to **lock field names now**  
- No future additions unless absolutely necessary  
- All members must:
  - Review schema immediately  
  - Suggest changes now to avoid future integration issues

---

### 5. Schema Scope
- Schema is primarily designed for:
  - Website scraping (event-focused)  
- Can also capture supporting info:
  - Parking, transportation, etc.  
- Decision made **not to use calendar-based structure** 

---

### 6. Render Deployment
- Render URL is live and tested (Rohan + Chakradhar)  
- Aligned with latest database updates  
- No need to re-upload modified files to avoid duplication

---

### 7. JKYog Event Preparation (Wednesday)
- Team may be called on stage:
  - Give a **brief, high-level overview**  
  - Avoid deep technical explanations  
  - Expected duration: ~5 minutes 

---

### 8. Class Conflict (Wednesday)
- Guest lecture scheduled during event time  
- Plan:
  - Inform professor in advance  
  - Sysha and Rujul to notify on behalf of both groups  
- Action to be completed by **today/tomorrow**

---

### 9. Next Meetings
- Tomorrow's meeting:
  - Short check-in (progress + blockers)  
- Future meetings:
  - Reduced to **30 minutes duration**
- Possible requirements:
  - Live bot demo  
  - Video recording  

---

## Action Items

- Chanakya to share transcript with Sysha & Rujul for submission  
- All team members to review schema and suggest final changes ASAP  
- Team to prepare bot demo + recording for Wednesday  
- Sysha & Rujul to inform professor about class conflict  
- Nikita to coordinate with Rohan for Render deployment help (if needed)  
- Sysha to upload MOM and update group  

---

## Notes
- Avoid introducing new fields post-finalization  
- Any schema/API changes must be communicated beforehand  
- Ensure alignment across teams to prevent bot failures  

---
---

# Week 8-9 Sync — Team 4B to Team 4A (API Handoff)

**Owner (Week 8):** Rohan Kothapalli — API alignment, deployment, handoff URL.

## Live API base URL (Team 4B / Render)

**HTTPS base URL (no trailing slash):**

`https://jkyog-whatsapp-bot-week4-ffuk.onrender.com`

This is the canonical URL used by every live smoke check, demo script, and proof artifact on Team 4B (see [Week 11 demo script](../4B/week11/docs/demo-script.md) and [Week 11 live events API proof](../4B/week11/docs/live-events-api-proof.md)).

> Note: the [`4B/week11/render.yaml`](../4B/week11/render.yaml) service-name string still reads `jkyog-whatsapp-bot-week8`, but the deployed Render service captured the URL above (with the `-week4-ffuk` suffix) on first deploy and has kept it ever since. The yaml service-name string is cosmetic at this point — Render uses the dashboard URL. Do not rename the service on the dashboard; that would mint a new URL and break every existing integration.

**Slack (manual checklist):**

- [x] Render base URL is documented in this handoff file for Team 4A integration use.
- [x] Linked [API security](../4B/week8/docs/api-security.md) and [Escalations API](../4B/week8/escalations-api.md) for integrators who need Bearer auth on `/escalations`.
- [ ] Slack post confirmation (manual): add Slack permalink once posted/verified.

## Events API (Team 4A contract v2.1)

All paths below are **public GET** — **no** `Authorization` header required. See [api-security.md](../4B/week8/docs/api-security.md).

| Endpoint |
|----------|
| `GET {BASE}/api/v2/events` |
| `GET {BASE}/api/v2/events/today` |
| `GET {BASE}/api/v2/events/recurring` |
| `GET {BASE}/api/v2/events/search?q={query}` |
| `GET {BASE}/api/v2/events/{event_id}` |

Replace `{BASE}` with the URL above (no trailing slash). Example:  
`https://jkyog-whatsapp-bot-week4-ffuk.onrender.com/api/v2/events/today`

## Post-deploy checklist (operator)

1. **Blueprint / service:** Build uses `4B/week8/requirements.txt`; start command is `uvicorn 4B.week8.main:app --host 0.0.0.0 --port $PORT` (see `render.yaml`).
2. **Environment:** Set `DATABASE_URL`, Twilio, `GOOGLE_API_KEY`, `ESCALATIONS_API_TOKEN`, and other vars per [`4B/week8/docs/environment-variables.md`](../4B/week8/docs/environment-variables.md).
3. **Event data:** Run the scraper and seed pipeline against production so the `events` table is populated (e.g. from repo root with `PYTHONPATH` including the repo, run [`4B/week8/scripts/scrape_events.py`](../4B/week8/scripts/scrape_events.py) then [`4B/week8/scripts/seed_database.py`](../4B/week8/scripts/seed_database.py) or `seed_from_scraped_json`, with `DATABASE_URL` pointing at the Render Postgres instance — often easiest via **Render Shell** once the service is live).
4. **Smoke test:** `GET {BASE}/health`, `GET {BASE}/health/db`, then each of the five event URLs above.
   - Proof (latest): [Live events API proof](../4B/week8/docs/live-events-api-proof.md)
5. **Escalations (Bearer):** Create a ticket, fetch it, resolve it (replace `TOKEN` and use a real `ticket_id` from the create response):

```bash
export TOKEN="<ESCALATIONS_API_TOKEN>"
curl -s -X POST "{BASE}/escalations" -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"priority":"medium","queue_status":"queued","message_for_user":"Test handoff","errors":[]}'
# Then GET {BASE}/escalations/<ticket_id> and PUT {BASE}/escalations/<ticket_id>/resolve with Bearer.
```

---

## April 9, 2026 sync — meeting notes

**Due in this file by 9:00 PM CST** (same night as the sync).

- **Schema lock (Chakradhar + Chanakya):** Confirmed in [schema-decisions.md](../4B/week8/docs/schema-decisions.md) as locked canonical contract (`sponsorship_tiers[]: {tier_name, price, description}` and stable event IDs).
- **Live URL check:** Verified reachable with successful live responses for all 5 Team 4A event endpoints. Evidence: [Live events API proof](../4B/week8/docs/live-events-api-proof.md) (run against `https://jkyog-whatsapp-bot-week4-ffuk.onrender.com` on 2026-04-16 UTC).
- **Blockers / follow-ups:** No API-path blocker remains (`/api/v2/events` is active). Manual Slack permalink and Team 4A acknowledgement are still pending capture.
- **Week 10 external dependency:** Harshith webhook confirmation (after hardcoded response removal) remains pending external confirmation.

## Other auth-sensitive routes (not Team 4A events)

- **`/escalations`** — requires `Authorization: Bearer` matching `ESCALATIONS_API_TOKEN`.
- **`POST /stripe/webhook`** — uses Stripe `Stripe-Signature`, not Bearer.

Details: [api-security.md](../4B/week8/docs/api-security.md).
