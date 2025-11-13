"""
Simple in-memory LRU cache with TTL for search results.

This cache is intentionally small and dependency-free to keep behavior
predictable in production. It stores recent query results and evicts
the least-recently-used entries when capacity is reached.
"""
from collections import OrderedDict
import time
from typing import Any, Optional


class SearchCache:
    """A tiny LRU cache with TTL support for query -> results.

    Usage:
        cache = SearchCache(max_size=256, ttl=60)
        value = cache.get(key)
        cache.set(key, value)
    """

    def __init__(self, max_size: int = 256, ttl: int = 60):
        self.max_size = max_size
        self.ttl = ttl
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def _evict_if_needed(self) -> None:
        while len(self._store) > self.max_size:
            self._store.popitem(last=False)

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        ts, value = item
        if (time.time() - ts) > self.ttl:
            # expired
            try:
                del self._store[key]
            except KeyError:
                pass
            return None

        # refresh order
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.time(), value)
        self._store.move_to_end(key)
        self._evict_if_needed()
