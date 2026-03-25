"""Stress test for database connection pooling and /health/db endpoint.

Validates the full connection hardening strategy:
1. Warm-up         — baseline connectivity and pool initialization
2. Concurrent burst — pool_size + max_overflow under pressure
3. Sustained load   — connection stability over repeated bursts
4. Idle wait        — simulated idle period (free-tier scenario)
5. Post-idle recovery — validates pool_pre_ping detects stale connections
6. Rapid reconnect  — back-to-back bursts after recovery

Uses only the Python standard library.

Examples:
    python stress_test_db_health.py

    set STRESS_TEST_URL=http://127.0.0.1:8000/health/db
    python stress_test_db_health.py
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
                    and data.get("status") == "ok"
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


def log_result(index: int, result: dict[str, object]) -> None:
    tag = "OK  " if result["ok"] else "FAIL"
    print(f"  [{index:03d}] {tag}  status={result['status']}  latency={result['latency_ms']:.1f}ms")
    if not result["ok"]:
        print(f"         body={str(result['body'])[:200]}")


def run_serial(name: str, count: int) -> list[dict[str, object]]:
    print(f"\n{'='*60}")
    print(f"  {name}  (serial x{count})")
    print(f"{'='*60}")
    results = []
    for i in range(1, count + 1):
        r = fetch_health()
        results.append(r)
        log_result(i, r)
    return results


def run_concurrent(name: str, count: int, concurrency: int) -> list[dict[str, object]]:
    print(f"\n{'='*60}")
    print(f"  {name}  (concurrent x{count}, workers={concurrency})")
    print(f"{'='*60}")
    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(fetch_health) for _ in range(count)]
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
    print("  DB CONNECTION HARDENING — STRESS TEST")
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
    print(f"  Phases: warm-up → burst → sustained → idle → recovery → rapid")

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
    print(f"  Note: This is a simulated idle period. Free-tier databases")
    print(f"  are reported to close idle connections after a period of")
    print(f"  inactivity. This test uses a shorter simulated interval.")
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

    report_path = "stress_test_results.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Full report saved to: {report_path}")

    if overall_stats["failures"] == 0:
        print("\n  RESULT: PASS — all requests succeeded, pool hardening behavior validated under this test scenario.")
    else:
        print(f"\n  RESULT: FAIL — {overall_stats['failures']} request(s) failed. Review phase stats above for details.")

    return 0 if overall_stats["failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())