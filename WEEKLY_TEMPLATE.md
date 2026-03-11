# Weekly Summary Template

Use this template for your weekly progress summaries. Save as `weekly-summaries/YYYY-MM-DD-week-N.md`.

---

Copy everything below this line into your weekly summary file:

---

```markdown
# Weekly Summary — Week [N] — [Month DD, YYYY]

**Student:** [Your Full Name]  
**Group:** 4A or 4B  
**Date:** YYYY-MM-DD

---

## 📋 Summary (TL;DR)

In 2-3 sentences, summarize what you accomplished this week.

---

## ✅ Completed Tasks

List the specific tasks you completed this week. Be specific and include outcomes.

| Task | Description | Outcome/Status |
|------|-------------|----------------|
| Task 1 | Brief description | Completed — [link or result] |
| Task 2 | Brief description | In progress — X% complete |
| Task 3 | Brief description | Blocked — [reason] |

---

## 🔍 Research & Findings

Document any research you conducted, discoveries made, or knowledge gained.

### [Topic/Area 1]
- Key finding 1
- Key finding 2
- Source/link if applicable

### [Topic/Area 2]
- Key finding 1
- Key finding 2

---

## 🚧 Blockers & Challenges

List any obstacles you encountered and how you addressed them (or need help with).

| Challenge | Impact | Resolution/Help Needed |
|-----------|--------|------------------------|
| [Description] | [High/Med/Low] | [What you tried or what you need] |

---

## 📅 Next Week's Plan

What are your priorities for next week?

1. [Priority task 1]
2. [Priority task 2]
3. [Priority task 3]

---

## 📊 Time Breakdown (Optional)

Rough estimate of how you spent your time this week:

- Research: X hours
- Documentation: X hours
- Meetings: X hours
- Implementation/Development: X hours
- Other: X hours

---

## 🔗 Links & Resources

Include any relevant links, documents, or references:

- [Link name](URL) — Brief description
- [Document name](path/to/doc.md) — Brief description

---

## 💬 Questions for Friday Call

Any questions you'd like to discuss in the Friday meeting:

1. [Question 1]
2. [Question 2]

---

*Submitted: [Date] at [Time]*
```

---

## Example Completed Summary

See below for an example of a well-written weekly summary:

```markdown
# Weekly Summary — Week 1 — February 20, 2026

**Student:** Rujul Shukla  
**Group:** 4A  
**Date:** 2026-02-20

---

## 📋 Summary (TL;DR)

This week I focused on researching WhatsApp Business API providers and comparing their features, pricing, and integration complexity. I also reviewed the existing system architecture documentation and identified integration points for the multi-channel platform.

---

## ✅ Completed Tasks

| Task | Description | Outcome/Status |
|------|-------------|----------------|
| API Research | Compared Twilio, MessageBird, and 360dialog for WhatsApp Business API | Completed — [research/whatsapp-api-comparison.md](research/whatsapp-api-comparison.md) |
| Architecture Review | Reviewed existing LOS system docs | Completed — noted 3 integration points |
| Team Sync | Met with Group 4A to divide research areas | Completed — assigned topics agreed |

---

## 🔍 Research & Findings

### WhatsApp Business API Providers

| Provider | Pricing | Features | Integration Complexity |
|----------|---------|----------|----------------------|
| Twilio | $0.005/message | Reliable, good docs | Low — well-documented SDKs |
| MessageBird | $0.004/message | Multi-channel | Medium — unified API |
| 360dialog | €0.002/message | Direct Meta API | High — requires more setup |

**Recommendation:** Start with Twilio for MVP due to documentation and support quality.

### Integration Points Identified

1. **Customer Database** — Need to sync contact info with LOS
2. **Loan Application Events** — Trigger messages on status changes
3. **Document Storage** — Secure storage for document delivery confirmations

---

## 🚧 Blockers & Challenges

| Challenge | Impact | Resolution/Help Needed |
|-----------|--------|------------------------|
| Unclear on compliance requirements for financial messaging | Medium | Need clarification on FINRA/regulatory requirements |

---

## 📅 Next Week's Plan

1. Deep dive into Twilio API documentation and create prototype
2. Research SMS fallback providers and pricing
3. Draft initial data flow diagram for WhatsApp integration

---

## 🔗 Links & Resources

- [Twilio WhatsApp API Docs](https://www.twilio.com/docs/whatsapp) — Official documentation
- [research/whatsapp-api-comparison.md](research/whatsapp-api-comparison.md) — My full comparison matrix

---

## 💬 Questions for Friday Call

1. What are the specific compliance requirements for sending loan-related messages via WhatsApp?
2. Should we prioritize one channel (WhatsApp) first or build all four simultaneously?

---

*Submitted: 2026-02-20 at 6:00 PM CST*
```

---

## Submission Reminders

- **Due:** Thursday by end of day (5:00 PM CST)
- **Submit to:** Your team lead (Rujul for 4A, Sysha for 4B)
- **Format:** Markdown file committed to your GitHub folder
- **File naming:** `weekly-summaries/YYYY-MM-DD-week-N.md`

---

*Last updated: February 2026*
