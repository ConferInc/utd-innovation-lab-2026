# Branch identification
_Exported on 3/25/2026 at 19:37:59 CDT from Cursor (2.6.21)_

---

**User**

which branch is this?

---

**Cursor**

You’re on **`feature/week6-chakradhar-escalations-db`**, tracking **`origin/feature/week6-chakradhar-escalations-db`**.

---

**User**

why is there database\__pycache__ only for database in week4

---

**Cursor**

Exploring the week4 layout and how `database` relates to other folders.



Here’s what’s going on.

### What `database\__pycache__` is

Python 3 creates a `__pycache__` directory **next to `.py` files** when those modules are **imported** (it stores compiled `.pyc` bytecode). It isn’t special to “database” as a concept—it’s tied to **Python modules**.

### Why you might only see it under `database` in week 4

1. **Only that tree has Python modules you actually ran/imported**  
   If the rest of `week4` is mostly markdown (e.g. `README.md`, `ASSIGNMENT.md`) or non-Python files, Python never compiles them, so **no `__pycache__`** appears there.

2. **`database` is a package**  
   Folders like `database/` with `__init__.py` and modules such as `models.py` get imported as `database`, `database.models`, etc. Those imports are exactly what create `database\__pycache__\`.

3. **It’s local and usually not in Git**  
   Your repo ignores bytecode caches:

```6:7:C:\Users\ga634\OneDrive\Documents\GitHub\utd-innovation-lab-2026\.gitignore
__pycache__/
*.pyc
```

So you see `__pycache__` on disk after running something (Alembic, app code, tests) that imports `database`, but it won’t show up as a normal tracked folder in the repo.

### How this repo’s week 4 is set up

`4B/week4` is documented as **archived** and only keeps assignment/readme-style files; live code was moved to `4B/week5/`, with an old snapshot under `4B/archive/week4-pre-migration/`. So if you still have a `week4\database` folder locally, it’s likely **leftover from an old layout or a local copy**—but the **reason** you only see `__pycache__` under `database` is still: **that’s the only place under week 4 where Python modules were imported.**

---

**User**

New mail:
Hi Team 4B, I hope you've had a good weekend. I've reviewed all your Week 5 deliverables and am very impressed with the engineering work. Excellent job on Twilio signature verification, LLM provider switching, database hardening, and service wrappers. ═══════════════════════════════════════════════════════════════════ WEEK 6 ASSIGNMENTS - GROUP 4B Theme: Feature Completion, Cleanup & Production Readiness ═══════════════════════════════════════════════════════════════════ --- 📝 SYSHA SHARMA (Lead) - Directory Cleanup & Code Organization What You'll Do: As team lead, you're orchestrating repository cleanup. Week 5 had lots of experimentation - now we need to organize everything professionally. Specific Tasks: 1. Complete directory restructuring (feature/week6-sysha-directory-cleanup branch) 2. Ensure Week 5 files are in correct 4B/week5/ locations 3. Archive or delete obsolete Week 4 files 4. Create 4B/week6/file-organization-guide.md with conventions 5. Review and merge cleanup branches from teammates 6. Update main README.md with current structure Deliverable: 4B/week6/file-organization-guide.md and updated README.md --- 📝 ROHAN KOTHAPALLI - Escalations Endpoint Implementation What You'll Do: Implement the API endpoints for bot-to-human escalation (collaborate with Chakradhar). Specific Tasks: 1. Implement POST /escalations: - Accept user_id, reason, context, session_id - Validate required fields - Store in database (via Chakradhar's schema) - Return escalation ticket ID 2. Implement GET /escalations/{id}: - Return status, created_at, resolution info 3. Implement PUT /escalations/{id}/resolve: - Mark as resolved with notes - Record who resolved it 4. Integrate with existing session management 5. Add comprehensive logging 6. Document in 4B/week6/escalations-api.md Branch: feature/week6-rohan-escalations-endpoint --- 📝 CHAKRADHAR GUMMAKONDA - Escalations Database Schema & Integration What You'll Do: Build the database layer for escalation system (collaborate with Rohan). Specific Tasks: 1. Create database migration for escalations table: - id (UUID primary key) - user_id, session_id, reason, context (JSON) - status (pending/in_progress/resolved) - created_at, resolved_at, resolved_by - Add appropriate indexes 2. Integrate with existing SQLAlchemy models 3. Verify performance under load (stress test) 4. Document schema in 4B/week6/escalations-schema.md 5. Update /health/db endpoint to check escalation table Branch: feature/week6-chakradhar-escalations-db --- 📝 SUBODH KRISHNA NIKUMBH - Wrapper Tests Expansion & Error Handling What You'll Do: Add production-grade error handling and comprehensive test coverage. Specific Tasks: 1. Expand unit tests for failure scenarios: - Timeout handling - Rate limit handling (429 responses) - Circuit breaker pattern (fail fast after N failures) - Retry exhaustion 2. Add integration tests with mocked APIs 3. Create 4B/week6/wrapper-error-handling.md documenting: - Errors each wrapper handles - Retry strategies per error type - Fallback behavior 4. Ensure wrappers log errors with context 5. Add health check functions to each wrapper Target: >80% code coverage Branch: feature/week6-subodh-wrapper-tests --- 📝 LEENA HUSSEIN - Documentation Consolidation & Knowledge Base What You'll Do: Create comprehensive documentation so a new developer can set up and run the system. Specific Tasks: 1. Complete documentation cleanup (feature/week6-leena-docs-cleanup branch) 2. Create comprehensive 4B/week6/README.md: - Architecture overview - Quick start guide (5 minutes to running bot) - Environment setup - How to run tests - How to make code changes 3. Document all environment variables in 4B/week6/environment-variables.md: - Required vs optional - Default values - Where to obtain API keys 4. Create troubleshooting guide with common errors 5. Document Render deployment process Branch: feature/week6-leena-docs-cleanup --- ═══════════════════════════════════════════════════════════════════ GIT SUBMISSION REQUIREMENTS ═══════════════════════════════════════════════════════════════════ 1. Create team branch: team-4B-week6 git checkout -b team-4B-week6 2. Create individual branches: git checkout -b feature/week6-[your-name]-[task] 3. Commit regularly with descriptive messages: git add . git commit -m "feat: implement POST /escalations endpoint" 4. Merge to team-4B-week6 when complete 5. Open Pull Request to main with title: "Team 4B - Week 6 Deliverables" --- ═══════════════════════════════════════════════════════════════════ CROSS-TEAM COORDINATION ═══════════════════════════════════════════════════════════════════ Coordinate with Group 4A: 1. BY MONDAY: Rujul (4A) will ask about /create-payment auth requirements 2. BY TUESDAY: Chanakya (4A) wants to review escalation progress with Rohan and Chakradhar 3. INTEGRATION TEST: Tuesday, March 25 - Test 4A's Postman collection against your endpoints 



Old mail:
Hi Team 4B,

I hope you've had a good weekend. I've reviewed all your Week 5 deliverables and am very impressed with the engineering work. Excellent job on Twilio signature verification, LLM provider switching, database hardening, and service wrappers.



═══════════════════════════════════════════════════════════════════
WEEK 6 ASSIGNMENTS - GROUP 4B
Theme: Feature Completion, Cleanup & Production Readiness
═══════════════════════════════════════════════════════════════════



---

📝 SYSHA SHARMA (Lead) - Directory Cleanup & Code Organization

What You'll Do:
As team lead, you're orchestrating repository cleanup. Week 5 had lots of experimentation - now we need to organize everything professionally.

Specific Tasks:
1. Complete directory restructuring (feature/week6-sysha-directory-cleanup branch)
2. Ensure Week 5 files are in correct 4B/week5/ locations
3. Archive or delete obsolete Week 4 files
4. Create 4B/week6/file-organization-guide.md with conventions
5. Review and merge cleanup branches from teammates
6. Update main README.md with current structure

Deliverable: 4B/week6/file-organization-guide.md and updated README.md

---

📝 ROHAN KOTHAPALLI - Escalations Endpoint Implementation

What You'll Do:
Implement the API endpoints for bot-to-human escalation (collaborate with Chakradhar).

Specific Tasks:
1. Implement POST /escalations:
   - Accept user_id, reason, context, session_id
   - Validate required fields
   - Store in database (via Chakradhar's schema)
   - Return escalation ticket ID

2. Implement GET /escalations/{id}:
   - Return status, created_at, resolution info

3. Implement PUT /escalations/{id}/resolve:
   - Mark as resolved with notes
   - Record who resolved it

4. Integrate with existing session management
5. Add comprehensive logging
6. Document in 4B/week6/escalations-api.md

Branch: feature/week6-rohan-escalations-endpoint

---

📝 CHAKRADHAR GUMMAKONDA - Escalations Database Schema & Integration

What You'll Do:
Build the database layer for escalation system (collaborate with Rohan).

Specific Tasks:
1. Create database migration for escalations table:
   - id (UUID primary key)
   - user_id, session_id, reason, context (JSON)
   - status (pending/in_progress/resolved)
   - created_at, resolved_at, resolved_by
   - Add appropriate indexes

2. Integrate with existing SQLAlchemy models
3. Verify performance under load (stress test)
4. Document schema in 4B/week6/escalations-schema.md
5. Update /health/db endpoint to check escalation table

Branch: feature/week6-chakradhar-escalations-db

---

📝 SUBODH KRISHNA NIKUMBH - Wrapper Tests Expansion & Error Handling

What You'll Do:
Add production-grade error handling and comprehensive test coverage.

Specific Tasks:
1. Expand unit tests for failure scenarios:
   - Timeout handling
   - Rate limit handling (429 responses)
   - Circuit breaker pattern (fail fast after N failures)
   - Retry exhaustion

2. Add integration tests with mocked APIs
3. Create 4B/week6/wrapper-error-handling.md documenting:
   - Errors each wrapper handles
   - Retry strategies per error type
   - Fallback behavior

4. Ensure wrappers log errors with context
5. Add health check functions to each wrapper

Target: >80% code coverage
Branch: feature/week6-subodh-wrapper-tests

---

📝 LEENA HUSSEIN - Documentation Consolidation & Knowledge Base

What You'll Do:
Create comprehensive documentation so a new developer can set up and run the system.

Specific Tasks:
1. Complete documentation cleanup (feature/week6-leena-docs-cleanup branch)
2. Create comprehensive 4B/week6/README.md:
   - Architecture overview
   - Quick start guide (5 minutes to running bot)
   - Environment setup
   - How to run tests
   - How to make code changes

3. Document all environment variables in 4B/week6/environment-variables.md:
   - Required vs optional
   - Default values
   - Where to obtain API keys

4. Create troubleshooting guide with common errors
5. Document Render deployment process

Branch: feature/week6-leena-docs-cleanup

---

═══════════════════════════════════════════════════════════════════
GIT SUBMISSION REQUIREMENTS
═══════════════════════════════════════════════════════════════════

1. Create team branch: team-4B-week6
   git checkout -b team-4B-week6

2. Create individual branches:
   git checkout -b feature/week6-[your-name]-[task]

3. Commit regularly with descriptive messages:
   git add .
   git commit -m "feat: implement POST /escalations endpoint"

4. Merge to team-4B-week6 when complete

5. Open Pull Request to main with title: "Team 4B - Week 6 Deliverables"
    

---

═══════════════════════════════════════════════════════════════════
CROSS-TEAM COORDINATION
═══════════════════════════════════════════════════════════════════

Coordinate with Group 4A:

1. BY MONDAY: Rujul (4A) will ask about /create-payment auth requirements
2. BY TUESDAY: Chanakya (4A) wants to review escalation progress with Rohan and Chakradhar
3. INTEGRATION TEST: Tuesday, March 25 - Test 4A's Postman collection against your endpoints

---



Old mail:
Hi Group 4B,

Your Week 6 assignment focuses on implementing the missing /escalations endpoint, completing unit tests, and achieving full integration with Team 4A.

═══════════════════════════════════════════════════════════════
CRITICAL DELIVERABLES (High Priority)
═══════════════════════════════════════════════════════════════

🔹 Subodh Nikumbh — Service Wrappers Unit Tests [MANDATORY CATCH-UP]
• Create test_wrappers.py with comprehensive unit tests for ALL service wrappers
• Test with_retry() decorator behavior
• Mock external APIs (Stripe, Maps, Calendar) — do not call real services in tests
• Test error handling and retry logic paths
• Due: End of Week 6 — this is blocking production readiness
• Branch: feature/week6-wrapper-tests (INDIVIDUAL branch required)

🔹 Rohan Kothapalli & Chakradhar Gummakonda — /escalations Endpoint
• Implement POST /escalations endpoint per Chanakya's escalation flow specification
• Accept form-encoded payload per API Contract v2.0
• Fields to handle: conversation_id, session_id, user_id, phone, name, latest_message, intent, escalation_reason, timestamp, short_transcript
• Return appropriate status codes (201 created, 400 bad request, 500 error)
• Add integration with volunteer queue system
• Branch: feature/week6-escalations-endpoint

🔹 Sysha Sharma — Directory Structure & Week 6 Organization
• Fix directory structure: Move Week 5 files from 4B/week4/ to 4B/week5/
• Ensure ALL Week 6 work goes into 4B/week6/ (not week4/ or week5/)
• Create feature/week6-<name> branches for all team members
• Lead team organization and Git hygiene enforcement
• Branch: feature/week6-directory-cleanup

🔹 Leena Hussein — Documentation Cleanup [MANDATORY CATCH-UP]
• Remove ALL raw citation artifacts [oaicite:N]{index=N} from integration-testing.md
• Fix code block formatting issues (lines 42-44)
• Add proper citations where needed
• Create INDIVIDUAL branch for all Week 6 work (do not commit directly to team branch)
• Branch: feature/week6-docs-cleanup

═══════════════════════════════════════════════════════════════
🤝 JOINT DELIVERABLE (Both Teams)
═══════════════════════════════════════════════════════════════

MANDATORY: Cross-Team Integration Demonstration
• Schedule joint call with Team 4A early Week 6
• Demonstrate ONE complete end-to-end flow: WhatsApp → webhook → escalation (if triggered) → response
• Document: Screenshot of working test + API request/response logs
 

═══════════════════════════════════════════════════════════════
📊 SUBMISSION REQUIREMENTS
═══════════════════════════════════════════════════════════════



1. Individual branch pushed to GitHub (feature/week6-<task>)
2. Merge into Group 4B shared branch (group-4b/week6)
3. ONE team PR to main

I'm attaching old documents and new documents. please check all the conditions:
I was told to follow chanakya's escalation flow or something. keep that also in mind.

im attaching old docs first of team 4a and team 4b.
then attaching my new docs (entire team 4b- but has only my changes), im chakradhar reddy gummakonda.


Files i modified or added:


stress_test_escalations.py
"""Stress test for escalations table CRUD operations.

Tests the database layer directly (no HTTP) to verify escalation
create/read/update performance under load.

Requires DATABASE_URL to be set.

Examples:
    python stress_test_escalations.py
"""

from __future__ import annotations

import os
import sys
import statistics
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

week4_dir = Path(__file__).resolve().parent
if str(week4_dir) not in sys.path:
    sys.path.insert(0, str(week4_dir))

from dotenv import load_dotenv

load_dotenv()

from database.models import SessionLocal
from database.schema import User
from database.state_tracking import (
    create_escalation,
    get_escalations_by_user,
    get_or_create_user,
    update_escalation_status,
)


SERIAL_CREATES = int(os.getenv("ESCALATION_SERIAL_CREATES", "20"))
CONCURRENT_CREATES = int(os.getenv("ESCALATION_CONCURRENT_CREATES", "50"))
CONCURRENCY = int(os.getenv("ESCALATION_CONCURRENCY", "10"))
STATUS_TRANSITIONS = int(os.getenv("ESCALATION_STATUS_TRANSITIONS", "30"))


def _create_unique_test_user() -> uuid.UUID:
    """Create a unique test user for this run."""
    db = SessionLocal()
    try:
        unique_suffix = uuid.uuid4().hex[:10]
        phone = f"+1999{unique_suffix}"
        user = get_or_create_user(db, phone, name="Escalation Stress Test User")
        return user.id
    finally:
        db.close()


def _cleanup_test_user(user_id: uuid.UUID) -> None:
    """Delete the test user so cascades remove all related stress-test rows."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()


def timed_create(user_id: uuid.UUID, index: int) -> dict:
    """Create one escalation and measure latency."""
    db = SessionLocal()
    start = time.perf_counter()
    try:
        esc = create_escalation(
            db=db,
            user_id=user_id,
            reason=f"stress-test-{index}",
            context={"test_index": index, "source": "stress_test"},
        )
        latency = (time.perf_counter() - start) * 1000
        return {"ok": True, "id": esc.id, "latency_ms": latency}
    except Exception as exc:
        latency = (time.perf_counter() - start) * 1000
        return {"ok": False, "error": str(exc), "latency_ms": latency}
    finally:
        db.close()


def timed_status_update(
    escalation_id: uuid.UUID,
    new_status: str,
    resolved_by: str | None = None,
) -> dict:
    """Update escalation status and measure latency."""
    db = SessionLocal()
    start = time.perf_counter()
    try:
        result = update_escalation_status(
            db=db,
            escalation_id=escalation_id,
            new_status=new_status,
            resolved_by=resolved_by,
            note=f"stress test transition to {new_status}",
        )
        latency = (time.perf_counter() - start) * 1000
        return {"ok": result is not None, "latency_ms": latency}
    except Exception as exc:
        latency = (time.perf_counter() - start) * 1000
        return {"ok": False, "error": str(exc), "latency_ms": latency}
    finally:
        db.close()


def timed_query(user_id: uuid.UUID) -> dict:
    """Query all escalations for a user and measure latency."""
    db = SessionLocal()
    start = time.perf_counter()
    try:
        rows = get_escalations_by_user(db=db, user_id=user_id)
        latency = (time.perf_counter() - start) * 1000
        return {"ok": True, "count": len(rows), "latency_ms": latency}
    except Exception as exc:
        latency = (time.perf_counter() - start) * 1000
        return {"ok": False, "error": str(exc), "latency_ms": latency}
    finally:
        db.close()


def compute_stats(results: list[dict]) -> dict:
    if not results:
        return {}

    latencies = sorted(r["latency_ms"] for r in results)
    total = len(results)
    successes = sum(1 for r in results if r["ok"])
    p95_idx = min(int(total * 0.95), total - 1)

    return {
        "total": total,
        "successes": successes,
        "failures": total - successes,
        "success_rate_pct": round(successes / total * 100, 2),
        "latency_ms": {
            "min": round(latencies[0], 2),
            "max": round(latencies[-1], 2),
            "mean": round(statistics.mean(latencies), 2),
            "median": round(statistics.median(latencies), 2),
            "p95": round(latencies[p95_idx], 2),
            "stddev": round(statistics.stdev(latencies), 2) if total > 1 else 0,
        },
    }


def print_stats(name: str, results: list[dict]) -> dict:
    stats = compute_stats(results)
    print(f"\n  --- {name} ---")
    print(
        f"  Total: {stats['total']}  |  OK: {stats['successes']}  |  "
        f"FAIL: {stats['failures']}  |  Rate: {stats['success_rate_pct']}%"
    )
    lat = stats["latency_ms"]
    print(
        f"  Latency (ms) — min: {lat['min']}  mean: {lat['mean']}  "
        f"median: {lat['median']}  p95: {lat['p95']}  max: {lat['max']}"
    )
    return stats


def main() -> int:
    print("=" * 60)
    print("  ESCALATIONS TABLE — STRESS TEST")
    print("=" * 60)

    user_id = _create_unique_test_user()
    print(f"  Test user: {user_id}")
    all_ok = True

    try:
        print(f"\n  Phase 1: Serial Creates (x{SERIAL_CREATES})")
        serial_results = []
        for i in range(SERIAL_CREATES):
            r = timed_create(user_id, i)
            serial_results.append(r)
            tag = "OK" if r["ok"] else "FAIL"
            print(f"    [{i+1:03d}] {tag}  latency={r['latency_ms']:.1f}ms")
        s1 = print_stats("Serial Creates", serial_results)
        if s1["failures"] > 0:
            all_ok = False

        print(
            f"\n  Phase 2: Concurrent Creates "
            f"(x{CONCURRENT_CREATES}, workers={CONCURRENCY})"
        )
        concurrent_results: list[dict] = []
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
            futures = [
                pool.submit(timed_create, user_id, i + SERIAL_CREATES)
                for i in range(CONCURRENT_CREATES)
            ]
            for i, future in enumerate(as_completed(futures), start=1):
                r = future.result()
                concurrent_results.append(r)
                tag = "OK" if r["ok"] else "FAIL"
                print(f"    [{i:03d}] {tag}  latency={r['latency_ms']:.1f}ms")
        s2 = print_stats("Concurrent Creates", concurrent_results)
        if s2["failures"] > 0:
            all_ok = False

        created_ids = [
            r["id"]
            for r in serial_results + concurrent_results
            if r.get("ok") and r.get("id")
        ]
        transition_count = min(STATUS_TRANSITIONS, len(created_ids))

        print(f"\n  Phase 3: Status Transitions (x{transition_count})")
        transition_results: list[dict] = []
        for i in range(transition_count):
            escalation_id = created_ids[i]
            r1 = timed_status_update(escalation_id, "in_progress")
            r2 = timed_status_update(
                escalation_id,
                "resolved",
                resolved_by="stress-test-agent",
            )
            transition_results.extend([r1, r2])
            tag1 = "OK" if r1["ok"] else "FAIL"
            tag2 = "OK" if r2["ok"] else "FAIL"
            print(
                f"    [{i+1:03d}] in_progress={tag1} ({r1['latency_ms']:.1f}ms)  "
                f"resolved={tag2} ({r2['latency_ms']:.1f}ms)"
            )
        s3 = print_stats("Status Transitions", transition_results)
        if s3["failures"] > 0:
            all_ok = False

        print(f"\n  Phase 4: Query by User (x10)")
        query_results = []
        for i in range(10):
            r = timed_query(user_id)
            query_results.append(r)
            tag = "OK" if r["ok"] else "FAIL"
            print(
                f"    [{i+1:03d}] {tag}  rows={r.get('count', '?')}  "
                f"latency={r['latency_ms']:.1f}ms"
            )
        s4 = print_stats("Query by User", query_results)
        if s4["failures"] > 0:
            all_ok = False

        print(f"\n{'='*60}")
        print(f"  RESULT: {'PASS' if all_ok else 'FAIL'}")
        print(f"{'='*60}")

        return 0 if all_ok else 1
    finally:
        _cleanup_test_user(user_id)


if __name__ == "__main__":
    raise SystemExit(main())



stress_test_db_health_v2:
"""Stress test for /health/db — Week 6 version.

Extends the Week 5 test with Phase 7: escalations table health verification.
Validates that /health/db returns escalation table status after migration 002.

Examples:
    python stress_test_db_health_v2.py

    set STRESS_TEST_URL=http://127.0.0.1:8000/health/db
    python stress_test_db_health_v2.py
"""

from __future__ import annotations

import json
import os
import statistics
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


STRESS_TEST_URL = os.getenv("STRESS_TEST_URL", "http://127.0.0.1:8000/health/db")
REQUEST_TIMEOUT = float(os.getenv("STRESS_TEST_TIMEOUT", "10"))

WARMUP_REQUESTS = int(os.getenv("STRESS_TEST_WARMUP", "5"))
BURST_REQUESTS = int(os.getenv("STRESS_TEST_BURST_REQUESTS", "50"))
CONCURRENCY = int(os.getenv("STRESS_TEST_CONCURRENCY", "10"))
SUSTAINED_ROUNDS = int(os.getenv("STRESS_TEST_SUSTAINED_ROUNDS", "3"))
SUSTAINED_DELAY = float(os.getenv("STRESS_TEST_SUSTAINED_DELAY", "2"))
IDLE_SECONDS = float(os.getenv("STRESS_TEST_IDLE_SECONDS", "30"))
POST_IDLE_REQUESTS = int(os.getenv("STRESS_TEST_POST_IDLE_REQUESTS", "5"))
RAPID_BURST_REQUESTS = int(os.getenv("STRESS_TEST_RAPID_BURST", "20"))
ESCALATION_PROBE_REQUESTS = int(os.getenv("STRESS_TEST_ESCALATION_PROBE", "10"))


def fetch_health() -> dict[str, object]:
    """Call /health/db once. Returns a result dict with status, latency, etc."""
    started = time.perf_counter()
    try:
        request = Request(STRESS_TEST_URL, method="GET")
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            body = response.read().decode("utf-8", errors="replace")
            status_code = response.getcode()
            try:
                data = json.loads(body)
                is_healthy = (
                    status_code == 200
                    and data.get("status") in ("ok", "degraded")
                    and data.get("database") == "connected"
                )
            except (json.JSONDecodeError, AttributeError):
                is_healthy = False
            return {
                "ok": is_healthy,
                "status": status_code,
                "body": body,
                "latency_ms": (time.perf_counter() - started) * 1000,
            }
    except HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "body": exc.read().decode("utf-8", errors="replace"),
            "latency_ms": (time.perf_counter() - started) * 1000,
        }
    except (URLError, OSError) as exc:
        return {
            "ok": False,
            "status": 0,
            "body": str(exc),
            "latency_ms": (time.perf_counter() - started) * 1000,
        }
    except Exception as exc:
        return {
            "ok": False,
            "status": 0,
            "body": f"Unexpected error: {exc}",
            "latency_ms": (time.perf_counter() - started) * 1000,
        }


def fetch_health_escalation_check() -> dict[str, object]:
    """Call /health/db and verify escalations table status is present."""
    started = time.perf_counter()
    try:
        request = Request(STRESS_TEST_URL, method="GET")
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            body = response.read().decode("utf-8", errors="replace")
            status_code = response.getcode()
            try:
                data = json.loads(body)
                tables = data.get("tables", {})
                escalations_ok = tables.get("escalations") == "ok"
                is_healthy = (
                    status_code == 200
                    and data.get("status") == "ok"
                    and data.get("database") == "connected"
                    and escalations_ok
                )
            except (json.JSONDecodeError, AttributeError):
                is_healthy = False
            return {
                "ok": is_healthy,
                "status": status_code,
                "body": body,
                "latency_ms": (time.perf_counter() - started) * 1000,
            }
    except HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "body": exc.read().decode("utf-8", errors="replace"),
            "latency_ms": (time.perf_counter() - started) * 1000,
        }
    except (URLError, OSError) as exc:
        return {
            "ok": False,
            "status": 0,
            "body": str(exc),
            "latency_ms": (time.perf_counter() - started) * 1000,
        }
    except Exception as exc:
        return {
            "ok": False,
            "status": 0,
            "body": f"Unexpected error: {exc}",
            "latency_ms": (time.perf_counter() - started) * 1000,
        }


def log_result(index: int, result: dict[str, object]) -> None:
    tag = "OK  " if result["ok"] else "FAIL"
    print(f"  [{index:03d}] {tag}  status={result['status']}  latency={result['latency_ms']:.1f}ms")
    if not result["ok"]:
        print(f"         body={str(result['body'])[:200]}")


def run_serial(name: str, count: int, fetcher=fetch_health) -> list[dict[str, object]]:
    print(f"\n{'='*60}")
    print(f"  {name}  (serial x{count})")
    print(f"{'='*60}")
    results = []
    for i in range(1, count + 1):
        r = fetcher()
        results.append(r)
        log_result(i, r)
    return results


def run_concurrent(name: str, count: int, concurrency: int, fetcher=fetch_health) -> list[dict[str, object]]:
    print(f"\n{'='*60}")
    print(f"  {name}  (concurrent x{count}, workers={concurrency})")
    print(f"{'='*60}")
    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(fetcher) for _ in range(count)]
        for i, future in enumerate(as_completed(futures), start=1):
            r = future.result()
            results.append(r)
            log_result(i, r)
    return results


def compute_stats(results: list[dict[str, object]]) -> dict:
    if not results:
        return {}

    latencies = [r["latency_ms"] for r in results]
    sorted_lat = sorted(latencies)
    total = len(results)
    successes = sum(1 for r in results if r["ok"])
    failures = total - successes
    status_counts: Counter[int] = Counter(r["status"] for r in results)

    p95_idx = min(int(total * 0.95), total - 1)
    p99_idx = min(int(total * 0.99), total - 1)

    return {
        "total_requests": total,
        "successes": successes,
        "failures": failures,
        "success_rate_pct": round(successes / total * 100, 2) if total else 0,
        "status_counts": dict(status_counts),
        "latency_ms": {
            "min": round(sorted_lat[0], 2),
            "max": round(sorted_lat[-1], 2),
            "mean": round(statistics.mean(latencies), 2),
            "median": round(statistics.median(latencies), 2),
            "p95": round(sorted_lat[p95_idx], 2),
            "p99": round(sorted_lat[p99_idx], 2),
            "stddev": round(statistics.stdev(latencies), 2) if total > 1 else 0,
        },
    }


def print_phase_stats(name: str, results: list[dict[str, object]]) -> dict:
    stats = compute_stats(results)
    print(f"\n  --- {name} stats ---")
    print(f"  Requests: {stats['total_requests']}  |  OK: {stats['successes']}  |  FAIL: {stats['failures']}  |  Rate: {stats['success_rate_pct']}%")
    lat = stats["latency_ms"]
    print(f"  Latency (ms) — min: {lat['min']}  mean: {lat['mean']}  median: {lat['median']}  p95: {lat['p95']}  p99: {lat['p99']}  max: {lat['max']}")
    return stats


def main() -> int:
    overall_start = time.perf_counter()

    print("=" * 60)
    print("  DB CONNECTION HARDENING — STRESS TEST v2 (Week 6)")
    print("=" * 60)
    print(f"  Target:       {STRESS_TEST_URL}")
    print(f"  Timeout:      {REQUEST_TIMEOUT}s")
    print()
    print(f"  Expected app-side pool settings:")
    print(f"    pool_size       = {os.getenv('DB_POOL_SIZE', '5 (default)')}")
    print(f"    max_overflow    = {os.getenv('DB_MAX_OVERFLOW', '2 (default)')}")
    print(f"    pool_timeout    = {os.getenv('DB_POOL_TIMEOUT', '30 (default)')}s")
    print(f"    pool_recycle    = {os.getenv('DB_POOL_RECYCLE', '300 (default)')}s")
    print(f"    pool_pre_ping   = True")
    print(f"    pool_use_lifo   = True")
    print()
    print(f"  Phases: warm-up → burst → sustained → idle → recovery → rapid → escalation probe")

    all_results: list[dict[str, object]] = []
    phase_stats: dict[str, dict] = {}

    # Phase 1: Warm-up
    warmup = run_serial("Phase 1: Warm-up", WARMUP_REQUESTS)
    all_results.extend(warmup)
    phase_stats["warmup"] = print_phase_stats("Warm-up", warmup)

    # Phase 2: Concurrent burst
    burst = run_concurrent("Phase 2: Concurrent Burst", BURST_REQUESTS, CONCURRENCY)
    all_results.extend(burst)
    phase_stats["burst"] = print_phase_stats("Burst", burst)

    # Phase 3: Sustained load
    sustained: list[dict[str, object]] = []
    for round_num in range(1, SUSTAINED_ROUNDS + 1):
        batch = run_concurrent(
            f"Phase 3: Sustained Load (round {round_num}/{SUSTAINED_ROUNDS})",
            BURST_REQUESTS // 2,
            CONCURRENCY,
        )
        sustained.extend(batch)
        all_results.extend(batch)
        if round_num < SUSTAINED_ROUNDS:
            print(f"\n  Pausing {SUSTAINED_DELAY}s between rounds...")
            time.sleep(SUSTAINED_DELAY)
    phase_stats["sustained"] = print_phase_stats("Sustained", sustained)

    # Phase 4: Simulated idle wait
    print(f"\n{'='*60}")
    print(f"  Phase 4: Simulated Idle Wait ({IDLE_SECONDS}s)")
    print(f"  Simulating period where connections may go stale.")
    print(f"  pool_pre_ping validates connections before reuse.")
    print(f"{'='*60}")
    time.sleep(IDLE_SECONDS)
    print(f"  Idle period complete.")

    # Phase 5: Post-idle recovery
    recovery = run_serial("Phase 5: Post-Idle Recovery", POST_IDLE_REQUESTS)
    all_results.extend(recovery)
    phase_stats["post_idle"] = print_phase_stats("Post-idle recovery", recovery)

    # Phase 6: Rapid reconnect burst
    rapid = run_concurrent("Phase 6: Rapid Reconnect Burst", RAPID_BURST_REQUESTS, CONCURRENCY)
    all_results.extend(rapid)
    phase_stats["rapid_reconnect"] = print_phase_stats("Rapid reconnect", rapid)

    # Phase 7: Escalation table probe
    escalation_probe = run_serial(
        "Phase 7: Escalation Table Probe",
        ESCALATION_PROBE_REQUESTS,
        fetcher=fetch_health_escalation_check,
    )
    all_results.extend(escalation_probe)
    phase_stats["escalation_probe"] = print_phase_stats("Escalation probe", escalation_probe)

    # Final summary
    overall_ms = (time.perf_counter() - overall_start) * 1000
    overall_stats = compute_stats(all_results)

    print(f"\n{'='*60}")
    print(f"  FINAL REPORT")
    print(f"{'='*60}")
    print(f"  Total requests:   {overall_stats['total_requests']}")
    print(f"  Total successes:  {overall_stats['successes']}")
    print(f"  Total failures:   {overall_stats['failures']}")
    print(f"  Success rate:     {overall_stats['success_rate_pct']}%")
    print(f"  Total time:       {overall_ms:.0f}ms ({overall_ms/1000:.1f}s)")
    print(f"  Throughput:       {overall_stats['total_requests'] / (overall_ms / 1000):.1f} req/s")
    lat = overall_stats["latency_ms"]
    print(f"  Latency (ms):     min={lat['min']}  mean={lat['mean']}  median={lat['median']}  p95={lat['p95']}  p99={lat['p99']}  max={lat['max']}  stddev={lat['stddev']}")

    report = {
        "test_config": {
            "url": STRESS_TEST_URL,
            "warmup": WARMUP_REQUESTS,
            "burst": BURST_REQUESTS,
            "concurrency": CONCURRENCY,
            "sustained_rounds": SUSTAINED_ROUNDS,
            "idle_seconds": IDLE_SECONDS,
            "post_idle": POST_IDLE_REQUESTS,
            "rapid_burst": RAPID_BURST_REQUESTS,
            "escalation_probe": ESCALATION_PROBE_REQUESTS,
        },
        "expected_pool_settings": {
            "pool_size": os.getenv("DB_POOL_SIZE", "5"),
            "max_overflow": os.getenv("DB_MAX_OVERFLOW", "2"),
            "pool_timeout": os.getenv("DB_POOL_TIMEOUT", "30"),
            "pool_recycle": os.getenv("DB_POOL_RECYCLE", "300"),
            "pool_pre_ping": True,
            "pool_use_lifo": True,
        },
        "phases": phase_stats,
        "overall": overall_stats,
        "total_elapsed_ms": round(overall_ms, 2),
    }

    report_path = "stress_test_results_v2.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Full report saved to: {report_path}")

    if overall_stats["failures"] == 0:
        print("\n  RESULT: PASS — all requests succeeded, pool hardening + escalation probe validated.")
    else:
        print(f"\n  RESULT: FAIL — {overall_stats['failures']} request(s) failed. Review phase stats above.")

    return 0 if overall_stats["failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())



state_tracking.py:
# database/state_tracking.py

import copy
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from .schema import Conversation, Escalation, Message, SessionState, User


VALID_ESCALATION_STATUSES = {"pending", "in_progress", "resolved"}


def _now() -> datetime:
    """Return the current UTC time as a naive UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash_session_token(session_token: str) -> str:
    """Return a SHA-256 hash for a raw session token."""
    return hashlib.sha256(session_token.encode("utf-8")).hexdigest()


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries without mutating the originals."""
    result = copy.deepcopy(dict1)

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = copy.deepcopy(value)

    return result


def get_or_create_user(db: Session, phone_number: str, name: Optional[str] = None) -> User:
    """Fetch an existing user by phone number or create a new one."""
    user = db.query(User).filter(User.phone_number == phone_number).first()
    now_utc = _now()

    if not user:
        user = User(
            phone_number=phone_number,
            name=name,
            created_at=now_utc,
            last_active_at=now_utc,
        )
        db.add(user)
    else:
        user.last_active_at = now_utc
        if name:
            user.name = name

    db.commit()
    db.refresh(user)
    return user


def get_or_create_active_conversation(db: Session, user_id: uuid.UUID) -> Conversation:
    """Return the user's latest active conversation, creating one if needed."""
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == user_id,
            Conversation.status == "active",
        )
        .order_by(Conversation.started_at.desc())
        .first()
    )

    if not conversation:
        conversation = Conversation(
            user_id=user_id,
            status="active",
            started_at=_now(),
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    return conversation


def log_message(
    db: Session,
    conversation_id: uuid.UUID,
    direction: str,
    text: str,
    intent: Optional[str] = None,
) -> Message:
    """Store a single inbound or outbound message for a conversation."""
    if direction not in {"inbound", "outbound"}:
        raise ValueError("direction must be either 'inbound' or 'outbound'")

    message = Message(
        conversation_id=conversation_id,
        direction=direction,
        text=text,
        intent=intent,
        created_at=_now(),
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def create_session(db: Session, user_id: uuid.UUID, ttl_minutes: int = 1440) -> SessionState:
    """Create a new active session for a user and deactivate older sessions.

    The raw token is returned only as a transient ``raw_session_token`` attribute
    on the returned SQLAlchemy object. The database stores only the hashed token.
    """
    now_utc = _now()

    (
        db.query(SessionState)
        .filter(
            SessionState.user_id == user_id,
            SessionState.is_active.is_(True),
        )
        .update(
            {
                "is_active": False,
                "updated_at": now_utc,
            },
            synchronize_session=False,
        )
    )

    raw_session_token = str(uuid.uuid4())
    hashed_session_token = _hash_session_token(raw_session_token)

    new_session = SessionState(
        user_id=user_id,
        session_token=hashed_session_token,
        expires_at=now_utc + timedelta(minutes=ttl_minutes),
        is_active=True,
        state={},
        updated_at=now_utc,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    new_session.raw_session_token = raw_session_token
    return new_session


def get_session_by_token(db: Session, session_token: str) -> Optional[SessionState]:
    """Lookup an active, non-expired session by a raw session token."""
    if not session_token:
        return None

    now_utc = _now()
    hashed_session_token = _hash_session_token(session_token)

    return (
        db.query(SessionState)
        .filter(
            SessionState.session_token == hashed_session_token,
            SessionState.is_active.is_(True),
            SessionState.expires_at > now_utc,
        )
        .first()
    )


def merge_session_state(
    db: Session,
    session_id: uuid.UUID,
    updates: Dict[str, Any],
) -> Optional[SessionState]:
    """Merge new context values into an existing session state object."""
    session_obj = db.query(SessionState).filter(SessionState.id == session_id).first()

    if not session_obj:
        return None

    current_state = session_obj.state or {}
    session_obj.state = deep_merge_dicts(current_state, updates)
    session_obj.updated_at = _now()

    db.commit()
    db.refresh(session_obj)
    return session_obj


def create_escalation(
    db: Session,
    user_id: uuid.UUID,
    reason: str,
    context: Optional[Dict[str, Any]] = None,
    session_id: Optional[uuid.UUID] = None,
) -> Escalation:
    """Create a new escalation for a user.

    If session_id is provided, validates that it belongs to the same user
    to prevent cross-user data corruption.
    """
    if not isinstance(reason, str):
        raise ValueError("reason must be a non-empty string")

    cleaned_reason = reason.strip()
    if not cleaned_reason:
        raise ValueError("reason must be a non-empty string")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} does not exist")

    if session_id is not None:
        session_obj = (
            db.query(SessionState)
            .filter(
                SessionState.id == session_id,
                SessionState.user_id == user_id,
            )
            .first()
        )
        if not session_obj:
            raise ValueError(
                f"session_id {session_id} does not exist "
                f"or does not belong to user {user_id}"
            )

    now_utc = _now()
    escalation = Escalation(
        user_id=user_id,
        session_id=session_id,
        reason=cleaned_reason,
        context=context or {},
        status="pending",
        created_at=now_utc,
    )
    db.add(escalation)
    db.commit()
    db.refresh(escalation)
    return escalation


def update_escalation_status(
    db: Session,
    escalation_id: uuid.UUID,
    new_status: str,
    resolved_by: Optional[str] = None,
    note: Optional[str] = None,
) -> Optional[Escalation]:
    """Transition an escalation to a new status.

    Sets resolved_at and resolved_by only when status becomes 'resolved'.
    Clears them again if status is moved back to a non-resolved state.
    """
    if new_status not in VALID_ESCALATION_STATUSES:
        raise ValueError(
            f"Invalid status '{new_status}'. "
            f"Must be one of: {', '.join(sorted(VALID_ESCALATION_STATUSES))}"
        )

    escalation = db.query(Escalation).filter(Escalation.id == escalation_id).first()
    if not escalation:
        return None

    escalation.status = new_status

    if new_status == "resolved":
        cleaned_resolved_by = None
        if isinstance(resolved_by, str):
            stripped_value = resolved_by.strip()
            cleaned_resolved_by = stripped_value or None
        escalation.resolved_at = _now()
        escalation.resolved_by = cleaned_resolved_by
    else:
        escalation.resolved_at = None
        escalation.resolved_by = None

    if isinstance(note, str):
        cleaned_note = note.strip()
        if cleaned_note:
            ctx = escalation.context or {}
            notes = ctx.get("status_notes", [])
            notes.append(
                {
                    "status": new_status,
                    "note": cleaned_note,
                    "timestamp": _now().isoformat(),
                }
            )
            ctx["status_notes"] = notes
            escalation.context = ctx

    db.commit()
    db.refresh(escalation)
    return escalation


def get_escalations_by_user(
    db: Session,
    user_id: uuid.UUID,
    status: Optional[str] = None,
) -> List[Escalation]:
    """Return all escalations for a user, optionally filtered by status."""
    query = db.query(Escalation).filter(Escalation.user_id == user_id)

    if status:
        if status not in VALID_ESCALATION_STATUSES:
            raise ValueError(
                f"Invalid status filter '{status}'. "
                f"Must be one of: {', '.join(sorted(VALID_ESCALATION_STATUSES))}"
            )
        query = query.filter(Escalation.status == status)

    return query.order_by(Escalation.created_at.desc()).all()


def get_escalation_by_id(
    db: Session,
    escalation_id: uuid.UUID,
) -> Optional[Escalation]:
    """Fetch a single escalation by its primary key."""
    return db.query(Escalation).filter(Escalation.id == escalation_id).first()

schema.py:
# database/schema.py

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .models import Base


def _now() -> datetime:
    """Return the current UTC time as a naive UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    """Represents a WhatsApp user known to the bot."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(JSONB, default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "SessionState",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    escalations = relationship(
        "Escalation",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Conversation(Base):
    """Represents a chat session history for a user."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String, default="active", index=True, nullable=False)
    started_at = Column(DateTime, default=_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class Message(Base):
    """Represents a single inbound or outbound bot message."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


class SessionState(Base):
    """Stores temporary conversational context for an active user session.

    Security note:
        The ``session_token`` column stores a hashed token value rather than the
        raw session token. The raw token should only be exposed by backend code
        immediately after session creation.
    """

    __tablename__ = "session_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    state = Column(JSONB, default=dict, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="sessions")
    escalations = relationship(
        "Escalation",
        back_populates="session",
    )


class Escalation(Base):
    """Records a human-handoff / escalation request from the bot."""

    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'resolved')",
            name="valid_escalation_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("session_state.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reason = Column(Text, nullable=False)
    context = Column(JSONB, default=dict, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)

    user = relationship("User", back_populates="escalations")
    session = relationship("SessionState", back_populates="escalations")



models.py:
import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")


def _get_database_url() -> str:
    """Return the configured database URL for SQLAlchemy.

    Normalizes legacy postgres:// URLs to postgresql:// for SQLAlchemy.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url


def _env_int(name: str, default: int) -> int:
    """Read an integer environment variable with a fallback default."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    """Read a float environment variable with a fallback default."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    """Run a database operation with exponential backoff retries."""
    max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
    base_delay = (
        base_delay_seconds
        if base_delay_seconds is not None
        else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
    )

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    raise RuntimeError(
        f"Database operation failed after {max_attempts} attempts"
    ) from last_error


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=_env_int("DB_POOL_SIZE", 5),
    max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
    pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
    pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _execute_health_query() -> None:
    """Run a lightweight query used by the DB health endpoint."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def _execute_escalations_probe() -> None:
    """Verify the escalations table is queryable."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))


def check_db_health() -> dict[str, Any]:
    """Check whether the application can connect to the database
    and whether the escalations table is reachable."""
    try:
        _run_with_retry(_execute_health_query)
    except Exception as exc:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }

    escalations_ok = True
    try:
        _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        escalations_ok = False

    if escalations_ok:
        return {
            "status": "ok",
            "database": "connected",
            "tables": {"escalations": "ok"},
        }
    return {
        "status": "degraded",
        "database": "connected",
        "tables": {"escalations": "unreachable"},
    }


def init_db() -> None:
    """Run Alembic migrations to bring the database schema up to date."""
    week4_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week4_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week4_dir / "migrations"))

    _run_with_retry(lambda: command.upgrade(cfg, "head"))

main.py:
"""
Unified FastAPI entrypoint for Week 6.

Implements the orchestration pipeline for the JKYog WhatsApp bot:
- Initializes the database
- Handles WhatsApp webhook requests
- Wires together authentication, session management, logging, and bot core
"""

import logging
import os
import time
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .authentication.auth import verify_whatsapp_request
from .authentication.session_manager import update_session_context
from .bot.intent_classifier import classify_intent
from .bot.response_builder import build_response
from .database.models import SessionLocal, check_db_health, get_db, init_db
from .database.state_tracking import log_message
from .service_wrappers import StripeWrapper, MapsWrapper, CalendarWrapper
from .service_wrappers.base_wrapper import NonRetryableServiceError


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("week4.main")

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    Initializes the database before serving requests.
    """
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully.")
    yield
    logger.info("Application shutdown complete.")


app = FastAPI(
    title="JKYog WhatsApp Bot",
    version="1.0.0",
    lifespan=lifespan,
)

def send_whatsapp_message(to: str, body: str) -> str:
    """Send a text message to a WhatsApp user via Twilio."""
    from twilio.rest import Client

    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    to_e164 = to if to.startswith("+") else f"+{to}"
    msg = client.messages.create(
        from_=os.environ["TWILIO_WHATSAPP_FROM"],
        body=body,
        to=f"whatsapp:{to_e164}",
    )
    return getattr(msg, "sid", "")


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/health/db", response_model=None)
def health_check_db():
    """
    Database health check endpoint.
    Returns 200 if the database is fully healthy or degraded (base
    connectivity works but an auxiliary table is unreachable).
    Returns 503 only when base database connectivity fails entirely.
    """
    result = check_db_health()
    if result["status"] == "ok":
        return result
    if result["status"] == "degraded":
        return JSONResponse(status_code=200, content=result)
    return JSONResponse(status_code=503, content=result)


@app.get("/")
def root() -> Dict[str, str]:
    """Root endpoint to confirm the bot is running."""
    return {"message": "JKYog WhatsApp Bot is running"}


@app.post("/create-payment")
def create_payment() -> Dict[str, Any]:
    """
    Create a Stripe payment intent (demo). Returns client_secret for client-side confirm.

    Uses StripeWrapper with retry and error handling. Returns 400 on bad inputs and
    503 on upstream Stripe issues.
    """
    logger.info("create_payment: initializing StripeWrapper")
    try:
        stripe = StripeWrapper()
    except ValueError as exc:
        logger.exception("create_payment: Stripe configuration error")
        return JSONResponse(
            status_code=503,
            content={"detail": f"Stripe configuration error: {str(exc)}"},
        )

    try:
        intent = stripe.create_payment_intent(amount=1000)
        client_secret = intent.get("client_secret")
        logger.info("create_payment: payment_intent created successfully")
        return {"client_secret": client_secret}
    except NonRetryableServiceError as exc:
        logger.exception("create_payment: non-retryable error")
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    except Exception as exc:
        logger.exception("create_payment: unexpected Stripe error")
        return JSONResponse(
            status_code=503,
            content={"detail": f"Stripe service error: {str(exc)}"},
        )


@app.get("/maps")
def maps_test() -> Any:
    """
    Test Google Maps geocode (Dallas) using MapsWrapper.

    Returns geocode results for a hardcoded address. Returns 503 on upstream issues.
    """
    logger.info("maps_test: initializing MapsWrapper")
    try:
        maps = MapsWrapper()
    except ValueError as exc:
        logger.exception("maps_test: Maps configuration error")
        return JSONResponse(
            status_code=503,
            content={"detail": f"Google Maps configuration error: {str(exc)}"},
        )

    try:
        return maps.geocode("Dallas")
    except NonRetryableServiceError as exc:
        logger.exception("maps_test: non-retryable error")
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    except Exception as exc:
        logger.exception("maps_test: unexpected Google Maps error")
        return JSONResponse(
            status_code=503,
            content={"detail": f"Google Maps service error: {str(exc)}"},
        )


@app.get("/calendar")
def calendar_test() -> Any:
    """
    Test Google Calendar upcoming events using CalendarWrapper.

    Returns a JSON object with upcoming events. Returns 503 on upstream issues.
    """
    logger.info("calendar_test: initializing CalendarWrapper")
    try:
        calendar = CalendarWrapper()
    except ValueError as exc:
        logger.exception("calendar_test: Calendar configuration error")
        return JSONResponse(
            status_code=503,
            content={"detail": f"Google Calendar configuration error: {str(exc)}"},
        )

    try:
        return calendar.list_events()
    except NonRetryableServiceError as exc:
        logger.exception("calendar_test: non-retryable error")
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    except Exception as exc:
        logger.exception("calendar_test: unexpected Google Calendar error")
        return JSONResponse(
            status_code=503,
            content={"detail": f"Google Calendar service error: {str(exc)}"},
        )


def _process_incoming_message(
    *,
    auth_result: Dict[str, Any],
    received_at_iso: str,
    received_monotonic_s: float,
) -> None:
    db: Session = SessionLocal()
    process_start_monotonic_s = time.monotonic()
    try:
        user = auth_result["user"]
        conversation = auth_result["conversation"]
        session = auth_result["session"]
        user_message: str = auth_result["message_text"]
        phone_number: str = auth_result["phone_number"]
        profile_name: Optional[str] = auth_result.get("profile_name")

        queue_delay_ms = int((process_start_monotonic_s - received_monotonic_s) * 1000)
        logger.info(
            "Message received_at=%s | queue_delay_ms=%s | phone=%s | user_id=%s | conversation_id=%s",
            received_at_iso,
            queue_delay_ms,
            phone_number,
            user.id,
            conversation.id,
        )

        inbound_intent: Optional[str] = None
        inbound_confidence: Optional[float] = None
        try:
            intent_result = classify_intent(user_message)
            inbound_intent = intent_result.get("intent")
            inbound_confidence = intent_result.get("confidence")
        except Exception as classify_err:
            logger.warning("Intent classification failed: %s", classify_err)

        try:
            log_message(
                db=db,
                conversation_id=conversation.id,
                direction="inbound",
                text=user_message,
                intent=inbound_intent,
            )
        except Exception as log_err:
            logger.error("Failed to log inbound message: %s", log_err, exc_info=True)

        user_context: Dict[str, Any] = {
            "user_id": str(user.id),
            "conversation_id": str(conversation.id),
            "session_id": str(session.id),
            "phone_number": phone_number,
            "profile_name": profile_name,
            "session_state": session.state or {},
        }

        bot_reply = build_response(
            user_message=user_message,
            user_context=user_context,
            intent=inbound_intent,
            confidence=inbound_confidence,
        )

        try:
            send_start = time.monotonic()
            twilio_sid = send_whatsapp_message(to=phone_number, body=bot_reply)
            send_ms = int((time.monotonic() - send_start) * 1000)
            total_ms = int((time.monotonic() - received_monotonic_s) * 1000)
            logger.info(
                "Message sent_at=%s | twilio_sid=%s | send_ms=%s | total_ms=%s | phone=%s | conversation_id=%s",
                _utc_now_iso(),
                twilio_sid,
                send_ms,
                total_ms,
                phone_number,
                conversation.id,
            )
        except Exception as send_err:
            logger.error(
                "Failed to send WhatsApp message to %s: %s",
                phone_number,
                send_err,
                exc_info=True,
            )

        try:
            update_session_context(
                db=db,
                session_id=session.id,
                context_updates={
                    "last_user_message": user_message,
                    "last_bot_reply": bot_reply,
                    "last_intent": inbound_intent,
                },
            )
        except Exception as session_err:
            logger.error("Session context update failed: %s", session_err, exc_info=True)

        try:
            log_message(
                db=db,
                conversation_id=conversation.id,
                direction="outbound",
                text=bot_reply,
                intent=inbound_intent,
            )
        except Exception as log_err:
            logger.error("Failed to log outbound message: %s", log_err, exc_info=True)

        logger.info(
            "Response generated | user_id=%s | conversation_id=%s",
            user.id,
            conversation.id,
        )
    except Exception as exc:
        logger.exception("Unhandled error while processing incoming message: %s", exc)
    finally:
        db.close()


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Main WhatsApp webhook endpoint."""
    try:
        req_start = time.monotonic()
        received_at_iso = _utc_now_iso()
        auth_result = await verify_whatsapp_request(request=request, db=db)

        if auth_result.get("status") == "ignored":
            return JSONResponse(
                status_code=200,
                content={
                    "status": "ignored",
                    "message": "Non-message event ignored",
                },
            )

        background_tasks.add_task(
            _process_incoming_message,
            auth_result=auth_result,
            received_at_iso=received_at_iso,
            received_monotonic_s=req_start,
        )

        ack_ms = int((time.monotonic() - req_start) * 1000)
        logger.info(
            "Webhook ack | received_at=%s | ack_ms=%s | phone=%s",
            received_at_iso,
            ack_ms,
            auth_result.get("phone_number"),
        )
        return JSONResponse(
            status_code=200,
            content={
                "status": "accepted",
                "detail": "Message accepted for background processing",
            },
        )

    except HTTPException as exc:
        logger.error("HTTP error in webhook: %s", exc.detail)
        raise exc

    except Exception as exc:
        logger.exception("Unhandled webhook error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "detail": "Internal server error while processing webhook",
            },
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("4B.week4.main:app", host="0.0.0.0", port=8000, reload=True)



002_add_escalations_table:
"""add escalations table

Revision ID: 002
Revises: 001
Create Date: 2026-03-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "escalations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_by", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_escalations_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["session_state.id"],
            name=op.f("fk_escalations_session_id_session_state"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_escalations")),
        sa.CheckConstraint(
            "status IN ('pending', 'in_progress', 'resolved')",
            name=op.f("ck_escalations_valid_escalation_status"),
        ),
    )
    op.create_index(op.f("ix_escalations_user_id"), "escalations", ["user_id"])
    op.create_index(op.f("ix_escalations_session_id"), "escalations", ["session_id"])
    op.create_index(op.f("ix_escalations_status"), "escalations", ["status"])
    op.create_index(op.f("ix_escalations_created_at"), "escalations", ["created_at"])


def downgrade() -> None:
    op.drop_index(op.f("ix_escalations_created_at"), table_name="escalations")
    op.drop_index(op.f("ix_escalations_status"), table_name="escalations")
    op.drop_index(op.f("ix_escalations_session_id"), table_name="escalations")
    op.drop_index(op.f("ix_escalations_user_id"), table_name="escalations")
    op.drop_table("escalations")



escalations-schema.md:
# Escalation Stress Test Verification

## Commands Run
- `alembic upgrade head`
- `python stress_test_db_health_v2.py`
- `python stress_test_escalations.py`

## Result
Both stress tests completed successfully and returned PASS.

## Evidence
- `stress_test_results_v2.json`
- terminal output screenshots/logs



check these files first. in the next steps, ill ask you how to run the stress testings, but for now, please check if they meet all the requiremetns required for chakradhar reddy gummakonda or chakradhar.

there are two mails, check accordingly, i guess we need to follow new mail but im unsure. please check thoroughly and give me a consolidated review and let me know if there are any errors.

---

**Cursor**

Checking the repository against the assignment requirements and searching for Chanakya's escalation flow / API contract references.



Here’s a consolidated review based on the **new Week 6 mail** (treat that as the primary spec unless your instructor says otherwise), the **older catch-up mail** (extra constraints that mostly land on **Rohan’s HTTP layer** and **cross-team contract**), **Chanakya’s handoff doc** (product/flow context, not a SQL schema), and what you pasted versus what’s currently in this repo.

---

### Which mail to follow

- **Default to the newer Week 6 mail** for task wording, branch names (`feature/week6-chakradhar-escalations-db`), and deliverables (`escalations-schema.md`, stress test, `/health/db`).
- **Keep the older mail in mind** for **integration shape**: form-encoded `POST /escalations`, API Contract v2.0-style fields (`conversation_id`, `session_id`, `user_id`, `phone`, `name`, `latest_message`, `intent`, `escalation_reason`, `timestamp`, `short_transcript`, etc.). That is mainly **endpoint + mapping** work; your **JSONB `context`** can hold those fields without one column per field, as long as **Rohan** (and 4A) agree on the JSON shape.

**Chanakya’s `chanakya-handoff-flow.md`** describes handoff/escalation **flows and payloads** (e.g. context preservation). It does **not** replace your migration; it informs what should end up in **`reason` + `context`** (and any future columns).

---

### What matches the new mail (Chakradhar)

| Requirement | Assessment |
|-------------|------------|
| Migration: `escalations` with UUID `id`, `user_id`, `session_id`, `reason`, JSON `context`, statuses `pending` / `in_progress` / `resolved`, `created_at`, `resolved_at`, `resolved_by`, indexes | **Met** in your pasted `002` migration and `Escalation` model. |
| SQLAlchemy integration + helpers | **Met** (`create_escalation`, `update_escalation_status`, `get_escalation_by_id`, `get_escalations_by_user`, validation, session ownership check). |
| Stress / load verification | **Met** in spirit: direct DB stress script + HTTP stress script with escalation probe phase. |
| `/health/db` checks escalations table | **Met** in pasted `check_db_health` + `_execute_escalations_probe`. |

---

### Gaps, risks, and “errors” to fix before calling it done

1. **`4B/week6/escalations-schema.md` (deliverable)**  
   Your paste reads like **stress-test evidence**, not **schema documentation**. The assignment asks for a **schema doc**: tables, columns, types, constraints, indexes, relationships (users / `session_state`), migration id (`002`), and how **`context`** is intended to store 4A-style fields.  
   **Action:** Replace or extend that file so it documents the **data model**, and optionally add a short “Stress testing” subsection with commands/results.

2. **Repo layout vs team rules (Sysha / file-organization guide)**  
   In this workspace, **`4B/week5`** is the live app; **`4B/week4`** is archived (README says code moved to week5). Your snippets show **`week4` paths** and a **`main.py` “Week 6” under week4** with `uvicorn.run("4B.week4.main:app", ...)`.  
   **Risk:** Merging that as-is conflicts with “production in `week5/`” and “week6 docs in `week6/`”. Database code and stress scripts should live under **`4B/week5/`** (and docs under **`4B/week6/`**), unless the lead explicitly chose otherwise.

3. **This clone may not include your branch**  
   Under `4B/week5/migrations/versions/` I only see **`001_...`**, no **`002` escalations** migration, and `check_db_health()` in the repo **does not** yet probe `escalations`. So your pasted work is **not verified as merged here**—confirm it’s pushed on **`feature/week6-chakradhar-escalations-db`** and will merge to **`team-4B-week6`** per the new mail.

4. **Old-mail “volunteer queue integration”**  
   Not in your DB paste. That’s usually **application logic / Rohan / another service**, not a migration requirement for you—just don’t claim the DB layer alone “integrates the queue.”

5. **Chanakya / 4A alignment**  
   No separate **`conversation_id`** column: acceptable if **`context.conversation_id`** (or similar) is the agreed contract with Rohan. If 4A Postman tests or analytics need **filtering/indexing by conversation**, you may later need a **column or indexed JSON path**—worth confirming before Tuesday’s integration test.

6. **Minor technical notes** (not necessarily wrong)  
   - Migration `id` has **no DB default**; OK if **all inserts go through SQLAlchemy** (`default=uuid.uuid4`). Raw SQL inserts must supply `id`.  
   - **`resolved_by`** as free string matches “record who resolved”; if you need a **user UUID** later, schema may evolve.

---

### Bottom line

- **Functionally**, your pasted **migration + models + state layer + health probe + stress scripts** align well with the **new mail** for Chakradhar.  
- The main **substantive gaps** are: **(1)** proper **`escalations-schema.md`** content, **(2)** **file placement** consistent with **`week5` / `week6`**, and **(3)** confirming **`context`** field names with **Rohan** so the **old mail / Chanakya / Postman** expectations are satisfied at the **API + JSON** layer—not necessarily as separate SQL columns.

If you want, next message can walk through **how to run** the stress tests step-by-step (still in Ask mode I can only give instructions, not run them for you unless you switch modes).

---

**User**

i dont understand naything you gave

---

**Cursor**

Here’s the same thing in **simple terms**.

---

### What you were supposed to do (Chakradhar)

Your job is basically **four things**:

1. **Add an `escalations` table** in the database (with migration) — ticket id, user, session, reason, extra data in JSON, status, times, who resolved it.
2. **Wire it in Python** (SQLAlchemy + helper functions to create/update/read escalations).
3. **Make `/health/db` also check** that the escalations table works, not only “database connected.”
4. **Prove it can handle load** (stress tests) and **write it down** in `escalations-schema.md`.

The **newer email** from your instructor is the one to follow for **what to deliver** and **branch names**.

The **older email** mostly adds things for **Rohan** (the HTTP `/escalations` API and form fields). For you, the important idea is: **those extra fields can live inside the JSON `context` column** — you don’t need a separate database column for every field unless the team decides they need that.

**Chanakya’s doc** is about **how escalation should feel in the product** (handoff, context). It’s **not** a replacement for your SQL; it just tells you **what kind of information** might end up in `reason` / `context`.

---

### What was good in your work

- Table + migration idea matches the assignment.
- Python helpers for create/update/query make sense.
- Health check that touches the `escalations` table matches the assignment.
- Stress test scripts match “show it works under load.”

---

### What was confusing or missing (in plain English)

1. **The doc file `escalations-schema.md`** should **explain the table** (what each column is). Right now it sounded more like a **test report**. Teachers asking for “schema” want a **clear description of the database design**, not only “we ran tests and it passed.”

2. **Where files live in the repo** — your team’s guide says **real app code goes in `4B/week5/`**, and **week 6 docs go in `4B/week6/`**. Putting a second copy of the app under `week4` can confuse people because **week 4 is treated as old/archived**.

3. **Your instructor’s latest requirements** win over older messages, **unless** they email again and say otherwise.

---

### One sentence summary

**You’re on the right track technically; the main fixes are (a) write a clear schema document, (b) put code/docs in the folders your team agreed on (`week5` code, `week6` docs), and (c) coordinate with Rohon so the JSON `context` matches what the API sends.**

If you tell me **which part** is hardest (migration? health endpoint? stress test? the markdown file?), I can explain **only that part** in even simpler steps.

---

**User**

also tell me how to stress test or run those files? sysha moved files to different folders, so does main.py uvicorn part change?

---

**Cursor**

Checking how the project is laid out and how stress-test scripts are invoked so we can give accurate commands.



Here’s a straight answer in two parts: **how to run stress tests**, and **what happens to uvicorn after Sysha’s moves**.

---

### Does `main.py` / uvicorn change when files move?

**The rule:** the string you pass to uvicorn must be the **Python import path** to your FastAPI `app`, not a file path.

- Production app code lives under **`4B/week5/`**. The README and `render.yaml` already say:

```128:128:C:\Users\ga634\OneDrive\Documents\GitHub\utd-innovation-lab-2026\4B\week5\README.md
5. **Start command:** `uvicorn 4B.week5.main:app --host 0.0.0.0 --port $PORT`
```

So as long as **`main.py` stays** at `4B/week5/main.py` and the package is **`4B.week5`**, you keep using:

```text
uvicorn 4B.week5.main:app --host 0.0.0.0 --port 8000
```

**Bug to fix:** at the bottom of your current `4B/week5/main.py`, the dev block still points at **week4**:

```382:385:C:\Users\ga634\OneDrive\Documents\GitHub\utd-innovation-lab-2026\4B\week5\main.py
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("4B.week4.main:app", host="0.0.0.0", port=8000, reload=True)
```

If Sysha moved everything to **week5**, that should be **`4B.week5.main:app`**, same as Render. Otherwise `python main.py` will try to load the wrong module.

**Summary:** Folder moves don’t change the *idea* (still `4B.week5.main:app`); they only matter so you don’t leave an old **`week4`** string in `main.py`.

---

### How to run the stress tests (local)

**1. Prep (once per machine)**

- From the **repo root**, install deps:  
  `pip install -r 4B/week5/requirements.txt`
- Set **`DATABASE_URL`** to your Postgres URL (PowerShell:  
  `$env:DATABASE_URL = "postgresql://..."`).

**2. Start the API (needed for HTTP stress tests)**

- From **repo root** (so `4B` is a package):

```powershell
uvicorn 4B.week5.main:app --host 127.0.0.1 --port 8000 --reload
```

Leave this running in one terminal.

**3. Stress test that hits `/health/db` (existing file: `stress_test_db_health.py`)**

- Open a **second** terminal, repo root:

```powershell
$env:STRESS_TEST_URL = "http://127.0.0.1:8000/health/db"
python 4B/week5/stress_test_db_health.py
```

Defaults already use `http://127.0.0.1:8000/health/db` if you skip `STRESS_TEST_URL`.

**4. Your Week 6 scripts (`stress_test_db_health_v2.py`, `stress_test_escalations.py`)**

- **`stress_test_db_health_v2.py`:** same pattern as above, but run the **v2** script name and the same `STRESS_TEST_URL` if it lives next to `stress_test_db_health.py` under `4B/week5/`.
- **`stress_test_escalations.py`:** talks to the DB **directly** (no HTTP). It needs **`DATABASE_URL`**, migrations applied (`alembic upgrade head` or app startup `init_db()`), then typically:

```powershell
cd 4B/week5
python stress_test_escalations.py
```

(That assumes the script sits in `4B/week5/` and imports `database` like your earlier snippet.)

**5. Against Render**

- Point `STRESS_TEST_URL` at your deployed health URL, e.g.  
  `https://your-service.onrender.com/health/db`  
  then run the same Python script.

---

### Quick checklist

| Step | What |
|------|------|
| Uvicorn / Render | Use **`4B.week5.main:app`** |
| Fix `if __name__ == "__main__"` | Should also say **`4B.week5.main:app`**, not `week4` |
| DB stress script | **`DATABASE_URL`** + run from **`4B/week5`** (or fix `sys.path` in the script) |
| HTTP stress script | Server running + **`STRESS_TEST_URL`** |

I’m in **Ask mode**, so I can’t edit `main.py` for you; if you switch to **Agent mode**, that one-line uvicorn fix can be applied automatically.

---

**User**

What You'll Do:
Build the database layer for escalation system (collaborate with Rohan).

Specific Tasks:
1. Create database migration for escalations table:
   - id (UUID primary key)
   - user_id, session_id, reason, context (JSON)
   - status (pending/in_progress/resolved)
   - created_at, resolved_at, resolved_by
   - Add appropriate indexes

2. Integrate with existing SQLAlchemy models
3. Verify performance under load (stress test)
4. Document schema in 4B/week6/escalations-schema.md
5. Update /health/db endpoint to check escalation table

Branch: feature/week6-chakradhar-escalations-db

what does verify under load (stress test) mean

---

**Cursor**

**“Verify performance under load (stress test)”** means: **hammer the database (and/or the `/health/db` endpoint) harder than a single manual click**, and **show that it still behaves acceptably**.

Concretely:

### What “load” means
- **Many operations in a row** — e.g. create lots of escalation rows, update status, query by user.
- **Concurrent work** — several operations **at the same time** (multiple threads or parallel HTTP requests), like many users or a busy server.
- Sometimes **sustained** activity — not one burst, but repeated bursts or a long idle then more traffic (your team’s DB health stress script does variations of this).

### What “verify” means (for your class project)
You’re not usually proving fancy SLAs; you’re showing:
- **Correctness under pressure** — creates/updates/queries don’t fail randomly; no obvious connection pool exhaustion.
- **Reasonable behavior** — e.g. most requests succeed; if you print timings, latencies don’t explode in a scary way.
- **Evidence** — logs or a small report (JSON output, screenshots) that you actually ran it.

### How it maps to *your* tasks
- **Direct DB stress** — script that calls your escalation helpers many times (serial + concurrent), like `stress_test_escalations.py`.
- **HTTP stress** — script that calls **`GET /health/db`** many times after you added the **escalations table check**, so you prove the app still answers health checks under load *and* that the escalation probe doesn’t break.

So in one sentence: **stress test = run many / concurrent database (or health) operations and show the system still works and you measured it.**

---

**User**

then how to test, do my files support that test

---

**Cursor**

Checking which stress-test files and escalation-related code exist in the repo.



Here’s how this lines up with **your repo as it is right now** (what I can see on disk).

---

### What’s in the repo **today**

| Piece | In `4B/week5` now? |
|--------|---------------------|
| `stress_test_db_health.py` | **Yes** — hits `GET /health/db` many times (warm-up, burst, concurrent, idle, etc.). |
| `stress_test_escalations.py` | **No** — not present. |
| `stress_test_db_health_v2.py` (escalation probe phase) | **No** — not present. |
| `Escalation` model / migration `002` | **No** — no `escalation` references under `4B/week5`. |
| `/health/db` checking **escalations** table | **No** — `check_db_health()` only does `SELECT 1`. |
| `4B/week6/escalations-schema.md` | **No** — only `file-organization-guide.md` is there. |

So: **the only stress test your tree supports right now is the generic `/health/db` load test**, not an escalation-specific one.

The escalation DB layer + v2 / `stress_test_escalations.py` you described earlier are either **only on your branch**, **not merged**, or **not in this clone**. Until those files are in `4B/week5` (and migrations applied), you **cannot** run escalation stress tests from this workspace as-is.

---

### How to run what **does** exist: `stress_test_db_health.py`

1. **Set `DATABASE_URL`** and install deps (`pip install -r 4B/week5/requirements.txt`).

2. **Start the app** from repo root:
   ```text
   uvicorn 4B.week5.main:app --host 127.0.0.1 --port 8000
   ```

3. **In another terminal**, from repo root (optional: point at your server):
   ```powershell
   $env:STRESS_TEST_URL = "http://127.0.0.1:8000/health/db"
   python 4B/week5/stress_test_db_health.py
   ```

That script only checks that **`/health/db` stays healthy under load** — it does **not** prove the **escalations** table, because the current code doesn’t expose that.

---

### What you need for the **full** “verify under load” for **escalations**

1. **Your escalation migration + models + `check_db_health` escalations probe** merged into `4B/week5`.
2. **Scripts** (or equivalents):
   - **DB-only:** e.g. `stress_test_escalations.py` — many creates/updates/queries via your helpers.
   - **HTTP:** e.g. `stress_test_db_health_v2.py` — many `GET /health/db` calls **after** health checks `escalations`.

3. Run the same way: **env + DB migrated + app running**, then run the matching script.

---

### Short answer

- **How to test (today):** run **`stress_test_db_health.py`** against a running app with **`DATABASE_URL`** set; that’s the supported load test in this repo.
- **Do your escalation files “support” that test?** **Not in this workspace** — escalation stress files and schema aren’t here. Once your **`feature/week6-chakradhar-escalations-db`** changes are **pulled/merged** into this project, **then** those files will support the escalation part; until then, only the generic DB health stress test applies.

If you tell me whether you’ve **pushed** your branch to GitHub, I can say exactly whether you should **pull your branch** or **merge from `team-4B-week6`** to get those files locally.

---

**User**

The escalation DB layer + v2 / stress_test_escalations.py you described earlier are either only on your branch, not merged, or not in this clone. Until those files are in 4B/week5 (and migrations applied), you cannot run escalation stress tests from this workspace as-is.



what's this?

---

**Cursor**

Here’s what that paragraph meant, in plain language.

### What I was saying

When I looked at **your project folder on disk** (`utd-innovation-lab-2026`), I only found:

- `4B/week5/stress_test_db_health.py`  
- **No** `stress_test_escalations.py`  
- **No** `stress_test_db_health_v2.py`  
- **No** escalation table / migration in `4B/week5`

So **in the copy of the repo that Cursor is using**, the escalation stress-test scripts and the escalation DB code **are not there**.

That can happen for a few reasons:

1. **Those files exist only on another Git branch**  
   You might have written them on `feature/week6-chakradhar-escalations-db` and committed/pushed there, but your **current folder** might be checked out to a different branch (e.g. `main` or `team-4B-week6`) that **doesn’t include those commits yet**.

2. **Not merged**  
   The work might be in a **pull request** on GitHub but **not merged** into the branch you have checked out locally. So GitHub has the files, your laptop folder doesn’t, until you merge and pull.

3. **“This clone”**  
   **Clone** = the copy of the repository on your computer. **“Not in this clone”** = “I don’t see those files in your local folder right now.”

### Why it matters

You **can only run** scripts that **actually exist** in the folder you’re in.  
If `stress_test_escalations.py` isn’t in `4B/week5`, you can’t run:

`python stress_test_escalations.py`

until you **switch to the branch that has it** or **pull/merge** so those files appear.

### How you can check yourself

In a terminal, in the repo:

- `git branch` — see which branch you’re on  
- `git status` — see if you have uncommitted files  
- `git log -1` — see latest commit  

If you’re on the branch where you added escalation work, those files should show up in File Explorer under `4B/week5`.

So that sentence was **not** accusing you of anything wrong — it was explaining: **I didn’t see those files in your workspace, so either they’re on another branch or not copied to this machine yet.** If you’ve since merged everything, your folder might now have them; the list above was a snapshot from when I searched.

---

**User**

what do you mean there are no files, i can kliterally see files and content

---

**Cursor**

You’re right to push back on how that sounded — **you do have files**, and **you’re not imagining things**.

Here’s the precise distinction:

### What I meant (narrowly)

I wasn’t saying **“your project is empty”** or **“you have no code.”**  
I was saying: when I **searched this workspace** for **specific escalation deliverables**, I **did not find**:

- `stress_test_escalations.py`
- `stress_test_db_health_v2.py`
- a migration like **`002_...escalations...`** next to your `001_initial_schema...`
- escalation-related code under `4B/week5` (no matches for `escalation` / `Escalation` at that time)

So the missing piece was **those particular files / that layer**, not “no files at all.”

### What you clearly *do* have (and can see)

Things like:

- `4B/week5/migrations/versions/001_initial_schema_...py` (you have this open)
- `main.py`, `stress_test_db_health.py`, `stress_test_results_*.json`, `file-organization-guide.md`, etc.

Those are real and visible — I never meant to deny that.

### Why it can still feel contradictory

- **Cursor’s folder** = one **checkout** of the repo at some **branch/commit**.  
- If **escalation** scripts or `002` live **only** in another branch, or **only** in a paste / another machine, you might **see** some things in chat history while the **tool search** on **this** folder doesn’t find the escalation files.

So: **you seeing files and content is valid.** My earlier note was only: **“I didn’t find the escalation stress-test / migration pieces in this tree when I searched,”** not “you have nothing.”

Sorry for the confusion in wording — that should have been spelled out this clearly the first time.

---

**User**

obviously i didnt save them yet, i would save them only if im sure about the contents im going with, thats why i sent you the modified codes or new codes as a prompt

---

**Cursor**

That makes complete sense, and it clears up the mismatch.

**What I was searching** was only **files saved on disk** in your repo (what Cursor’s tools can read). **What you sent in the chat** was **draft code in the message** — not necessarily written to `4B/week5/` yet. So when I said those scripts “weren’t in the workspace,” I meant **literally not saved as files**, not that your draft was wrong.

**Your workflow is reasonable:** get the contents reviewed, then save/commit when you’re confident.

**How to use that together next time:** if you want a review of **saved** code, point to the files or save first; if you’re pasting drafts in chat, say **“not saved yet”** and I’ll treat the paste as the source of truth and won’t assume it’s on disk.

Sorry for the confusion — it was a **saved vs unsaved** difference, not a judgment of your work.

---

**User**

now can you check and let me know if my files match the requirements. all my files required for week6 are sent as prompt to you

---

**Cursor**

Here’s a **requirements check** based **only on what you pasted in chat** (your drafts), not on files on disk.

---

### Assignment (Chakradhar) vs your pasted work

| # | Requirement | Matches? | Notes |
|---|-------------|----------|--------|
| **1** | **Migration:** `escalations` with UUID `id`, `user_id`, `session_id`, `reason`, JSON `context`, `status` ∈ pending / in_progress / resolved, `created_at`, `resolved_at`, `resolved_by`, **indexes** | **Yes** | Migration adds FKs, check constraint, indexes on `user_id`, `session_id`, `status`, `created_at`. |
| **2** | **SQLAlchemy:** model + ties to existing models | **Yes** | `Escalation` model + relationships on `User` and `SessionState`; helpers in `state_tracking.py`. |
| **3** | **Verify under load (stress test)** | **Yes** | `stress_test_escalations.py` (DB) + `stress_test_db_health_v2.py` (HTTP + escalation probe) fit the ask. |
| **4** | **`4B/week6/escalations-schema.md`** | **Partial** | What you pasted reads like **stress-test evidence** (commands, PASS, JSON filenames). The assignment also wants a **schema write-up** (table purpose, columns, types, constraints, indexes, how it links to `users` / `session_state`). **Expand that doc** so it’s clearly a schema doc, with testing as a subsection if you want. |
| **5** | **`/health/db` checks escalation table** | **Yes** | `check_db_health()` + probe query; `main.py` returning 200 for `ok` / `degraded` matches that design. |

---

### Small fixes to plan before you save

1. **`main.py` bottom:** You had `uvicorn.run("4B.week4.main:app", ...)`. If the app lives under **`4B/week5`**, that should be **`4B.week5.main:app`** (same as README / Render).

2. **Where files live:** Put code under **`4B/week5/`** and the markdown under **`4B/week6/`**, per your team’s layout—not a second copy under `week4` unless Sysha explicitly said so.

3. **`escalations-schema.md`:** Add a real **schema section** (table + columns + relationships + migration id). Keep your stress-test section as extra proof.

4. **Rohan / API fields:** Your **`context` JSONB** can hold things like `conversation_id`, `phone`, `short_transcript`, etc. Confirm with Rohan so his `POST /escalations` maps into the same shape—no extra DB change required unless you agree on new columns.

---

### Bottom line

For the **code you pasted**, you **meet tasks 1, 2, 3, and 5** well. **Task 4** is only fully met once **`escalations-schema.md` documents the schema**, not only the stress tests. Fix the **uvicorn string** and **paths (week5/week6)** when you save.

If you paste an updated `escalations-schema.md` draft, I can say line-by-line if it’s enough for the rubric.

---

**User**

which branch is this?

---

**Cursor**

Checking the current branch.



You’re on **`feature/week6-chakradhar-escalations-db`** (that’s what `.git/HEAD` points to).

