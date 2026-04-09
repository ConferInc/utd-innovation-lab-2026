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
    get_escalation_by_id,
    update_escalation_status,
)


SERIAL_CREATES = int(os.getenv("ESCALATION_SERIAL_CREATES", "20"))
CONCURRENT_CREATES = int(os.getenv("ESCALATION_CONCURRENT_CREATES", "50"))
CONCURRENCY = int(os.getenv("ESCALATION_CONCURRENCY", "10"))
STATUS_TRANSITIONS = int(os.getenv("ESCALATION_STATUS_TRANSITIONS", "30"))
ESCALATIONS_REPORT_PATH = os.getenv(
    "ESCALATIONS_REPORT_PATH", "stress_test_escalations_results_localv1.json"
)


def _create_unique_test_user() -> str:
    """No longer used for escalations, but kept for compatibility with other tests."""
    return "N/A"


def _cleanup_test_user(user_id: str) -> None:
    """No longer used for escalations."""
    pass


def timed_create(index: int) -> dict:
    """Create one escalation and measure latency."""
    db = SessionLocal()
    start = time.perf_counter()
    try:
        esc = create_escalation(
            db=db,
            priority="medium",
        )
        latency = (time.perf_counter() - start) * 1000
        return {"ok": True, "id": esc.ticket_id, "latency_ms": latency}
    except Exception as exc:
        latency = (time.perf_counter() - start) * 1000
        return {"ok": False, "error": str(exc), "latency_ms": latency}
    finally:
        db.close()


def timed_status_update(
    escalation_id: uuid.UUID,
    queue_status: str,
    assigned_volunteer: str | None = None,
) -> dict:
    """Update escalation status and measure latency."""
    db = SessionLocal()
    start = time.perf_counter()
    try:
        result = update_escalation_status(
            db=db,
            ticket_id=escalation_id,
            queue_status=queue_status,
            assigned_volunteer=assigned_volunteer,
            error_note=f"stress test transition to {queue_status}",
        )
        latency = (time.perf_counter() - start) * 1000
        return {"ok": result is not None, "latency_ms": latency}
    except Exception as exc:
        latency = (time.perf_counter() - start) * 1000
        return {"ok": False, "error": str(exc), "latency_ms": latency}
    finally:
        db.close()


def timed_query() -> dict:
    """Query all escalations and measure latency."""
    db = SessionLocal()
    start = time.perf_counter()
    try:
        from database.state_tracking import get_escalations_by_status
        rows = get_escalations_by_status(db=db)
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
            r = timed_create(i)
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
                pool.submit(timed_create, i + SERIAL_CREATES)
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
            r1 = timed_status_update(escalation_id, "assigned")
            r2 = timed_status_update(
                escalation_id,
                "resolved",
                assigned_volunteer="stress-test-agent",
            )
            transition_results.extend([r1, r2])
            tag1 = "OK" if r1["ok"] else "FAIL"
            tag2 = "OK" if r2["ok"] else "FAIL"
            print(
                f"    [{i+1:03d}] assigned={tag1} ({r1['latency_ms']:.1f}ms)  "
                f"resolved={tag2} ({r2['latency_ms']:.1f}ms)"
            )
        s3 = print_stats("Status Transitions", transition_results)
        if s3["failures"] > 0:
            all_ok = False

        print(f"\n  Phase 4: Global Query (x10)")
        query_results = []
        for i in range(10):
            r = timed_query()
            query_results.append(r)
            tag = "OK" if r["ok"] else "FAIL"
            print(
                f"    [{i+1:03d}] {tag}  rows={r.get('count', '?')}  "
                f"latency={r['latency_ms']:.1f}ms"
            )
        s4 = print_stats("Global Query", query_results)
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
                "global_query": s4,
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