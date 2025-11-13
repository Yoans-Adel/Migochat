"""
Lightweight metrics helpers for search instrumentation.

This module provides small counters and a timing context manager used by
the search engine to measure latency and basic hit/miss statistics.
It is intentionally simple and file-local to avoid external deps.
"""
import time
from typing import Dict


class Metrics:
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.timings: Dict[str, list[float]] = {}

    def incr(self, name: str, amount: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + amount

    def get(self, name: str) -> int:
        return self.counters.get(name, 0)

    def record_timing(self, name: str, value: float) -> None:
        self.timings.setdefault(name, []).append(value)

    def avg_timing(self, name: str) -> float:
        vals = self.timings.get(name, [])
        if not vals:
            return 0.0
        return sum(vals) / len(vals)


class Timer:
    def __init__(self, metrics: Metrics, name: str):
        self.metrics = metrics
        self.name = name
        self.start = 0.0

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = time.time() - self.start
        self.metrics.record_timing(self.name, elapsed)


# Module-level default metrics instance (used by search engine)
default_metrics = Metrics()
