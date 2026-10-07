"""Disposable synthetic benchmark for canonical O(N) recovery scanning.

Manual diagnostic only. No provider, network, production or real corpus.
Run on the authorized isolated KGM host.
"""
from __future__ import annotations
import argparse
import statistics
import tempfile
import time
from .research_durable_lifecycle_v1 import admit, recovery_snapshot


def _request(i):
    consumer = f"benchmark-{i // 1000:02d}"
    return {
        "request_id": f"bench-{i:06d}", "consumer_id": consumer,
        "requested_at_utc": "2026-10-07T00:00:00Z", "mode": "CURRENT",
        "symbols": ["BTCUSDT"], "period_start_utc": "2026-10-06T00:00:00Z",
        "period_end_utc": "2026-10-07T00:00:00Z", "max_results": 1,
        "policy_version": "bench-v1",
    }


def measure(count, runs=3):
    policy = {f"benchmark-{i:02d}": "bench-v1" for i in range((count + 999) // 1000)}
    with tempfile.TemporaryDirectory(prefix="kgm-recovery-benchmark-") as root:
        for i in range(count):
            admit(root, _request(i), allowed_consumers=policy,
                  max_pending_per_consumer=1000)
        samples = []
        for _ in range(runs):
            started = time.perf_counter()
            found = recovery_snapshot(root, allowed_consumers=policy)
            samples.append(time.perf_counter() - started)
            if len(found) != count:
                raise RuntimeError("benchmark recovery count mismatch")
        return {"count": count, "runs": runs, "seconds": samples,
                "median_seconds": statistics.median(samples)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, required=True,
                        choices=(100, 1000, 5000, 10000))
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()
    if not 3 <= args.runs <= 20:
        raise SystemExit("runs must be 3..20")
    print(measure(args.count, args.runs))


if __name__ == "__main__":
    main()
