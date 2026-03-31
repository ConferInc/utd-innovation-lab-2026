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
import json
import statistics
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

week7_dir = Path(__file__).resolve().parent.parent
if str(week7_dir) not in sys.path:
    sys.path.insert(0, str(week7_dir))

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
ESCALATIONS_REPORT_PATH = os.getenv(
    "ESCALATIONS_REPORT_PATH", "stress_test_escalations_results_localv1.json"
)


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

        overall_results = (
            serial_results + concurrent_results + transition_results + query_results
        )
        overall_stats = compute_stats(overall_results)
        report = {
            "test_config": {
                "serial_creates": SERIAL_CREATES,
                "concurrent_creates": CONCURRENT_CREATES,
                "concurrency": CONCURRENCY,
                "status_transitions_requested": STATUS_TRANSITIONS,
                "status_transitions_executed": transition_count,
                "query_requests": 10,
            },
            "phases": {
                "serial_creates": s1,
                "concurrent_creates": s2,
                "status_transitions": s3,
                "query_by_user": s4,
            },
            "overall": overall_stats,
            "result": "PASS" if all_ok else "FAIL",
        }
        with open(ESCALATIONS_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\n{'='*60}")
        print(f"  RESULT: {'PASS' if all_ok else 'FAIL'}")
        print(f"  JSON report saved to: {ESCALATIONS_REPORT_PATH}")
        print(f"{'='*60}")

        return 0 if all_ok else 1
    finally:
        _cleanup_test_user(user_id)


if __name__ == "__main__":
    raise SystemExit(main())