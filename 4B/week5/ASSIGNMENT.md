# Week 4 Assignment — Group 4B

**Deadline:** Thursday, March 12, 2025 at 11:59 PM CST

## ✅ Deliverables — Working Integration System

### Core Requirements
1. **FastAPI entry point** (`main.py` or `app.py`) runs without errors
2. **All modules wired together:**
   - Authentication module
   - Response builder
   - Integrations (WhatsApp)
   - Database layer
3. **WhatsApp webhook** properly routed and handled
4. **Complete `requirements.txt`** with all dependencies
5. **Comprehensive `README.md`** enables fresh clone → running bot in <10 minutes
6. **Demo video** recorded and shared (3-5 minutes)

### Integration Focus
Your code must demonstrate **all components working together**. This is not individual modules — this is a working system that:

1. Receives a WhatsApp message via webhook
2. Authenticates/validates the request
3. Processes through response builder logic
4. Stores/retrieves data from database
5. Returns appropriate response to WhatsApp

## ✅ Git Workflow
- Create individual branches: `firstname-week4`
- Merge individual work into shared team branch: `Team-4B-Week4`
- Submit **ONE final Pull Request** from `Team-4B-Week4` to `main`

## 📋 Submission Requirements
1. **Weekly summary email** due Thursday EOD (reply to assignment thread)
2. **GitHub PR** must include:
   - Working code with all modules integrated
   - Updated `requirements.txt`
   - Comprehensive `README.md`
   - Setup instructions
3. **Demo video** must show:
   - The bot running locally
   - Responding to at least one WhatsApp test message
   - All components working together
4. **Documentation** must be clear enough for a new developer to run the system

## ✅ Success Criteria
- **System runs end-to-end** without manual intervention (50%)
- **Code quality and organization** (20%)
- **Documentation completeness** (15%)
- **Demo video clarity** (10%)
- **On-time submission** (5%)

## 🚫 Common Pitfalls to Avoid
1. **Module isolation** — Components must be wired together, not separate scripts
2. **Incomplete requirements** — `requirements.txt` must install everything needed
3. **Missing webhook handling** — WhatsApp integration must be functional
4. **Poor documentation** — README must work for fresh clone
5. **No demo** — Video is required to prove working system

## 📞 Contact for Blockers
Reach out immediately via email (reply to this assignment thread) if you encounter blockers. **No late submissions without prior approval.**

---

*Assigned: March 10, 2026 • Last updated: March 10, 2026 • Version: 1.0*