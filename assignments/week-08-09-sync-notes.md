# Week 8–9 sync — Team 4B ↔ Team 4A (integration)

**Owner (Week 8):** Rohan Kothapalli — API alignment, deployment, handoff URL.

## Live API base URL (Team 4B / Render)

**HTTPS base URL (no trailing slash):**

`https://jkyog-whatsapp-bot-week8.onrender.com`

This matches the Render **service name** `jkyog-whatsapp-bot-week8` in [`4B/week8/render.yaml`](../4B/week8/render.yaml). After the first deploy, **confirm the exact URL** in the Render dashboard (Settings → your Web Service → URL) and use that value if it differs.

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
`https://jkyog-whatsapp-bot-week8.onrender.com/api/v2/events/today`

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
- **Blockers / follow-ups:** No API-path blocker remains (`/api/v2/events` is active). Keep manual Slack permalink and Team 4A acknowledgement in this section once captured.

## Other auth-sensitive routes (not Team 4A events)

- **`/escalations`** — requires `Authorization: Bearer` matching `ESCALATIONS_API_TOKEN`.
- **`POST /stripe/webhook`** — uses Stripe `Stripe-Signature`, not Bearer.

Details: [api-security.md](../4B/week8/docs/api-security.md).
