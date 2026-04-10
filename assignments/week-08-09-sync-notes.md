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
  - Prize, sponsorship tiers, source metadata, notes :contentReference[oaicite:1]{index=1}  

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
- Tomorrow’s meeting:
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
