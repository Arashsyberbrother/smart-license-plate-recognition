"""
In-memory LRU cache manager
مدیریت حافظه پنهان درون-حافظه
"""

from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any, Dict, Optional


class CacheManager:
    """
    Simple LRU cache with TTL-based expiry.
    Thread-safety is not guaranteed; suitable for single-process use.
    """

    def __init__(self, max_size: int = 1000, ttl: int = 300) -> None:
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._timestamps: Dict[str, float] = {}

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[Any]:
        """Return cached value or None if missing / expired"""
        if key not in self._cache:
            return None
        if self._is_expired(key):
            self.delete(key)
            return None
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        """Store a value; evicts LRU entry when capacity is reached"""
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        self._timestamps[key] = time.monotonic()
        if len(self._cache) > self.max_size:
            # Remove least-recently-used item
            oldest_key, _ = self._cache.popitem(last=False)
            self._timestamps.pop(oldest_key, None)

    def delete(self, key: str) -> None:
        """Remove a single entry"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)

    def clear(self) -> None:
        """Remove all entries"""
        self._cache.clear()
        self._timestamps.clear()

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def evict_expired(self) -> int:
        """Remove all expired entries; returns count removed"""
        expired = [k for k in list(self._cache) if self._is_expired(k)]
        for k in expired:
            self.delete(k)
        return len(expired)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> Dict[str, Any]:
        """Return cache statistics"""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
        }

    # ------------------------------------------------------------------

    def _is_expired(self, key: str) -> bool:
        ts = self._timestamps.get(key)
        if ts is None:
            return True
        return (time.monotonic() - ts) > self.ttl


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_cache_instance: Optional[CacheManager] = None


def get_cache_manager(max_size: int = 1000, ttl: int = 300) -> CacheManager:
    """Return the global CacheManager singleton"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager(max_size=max_size, ttl=ttl)
    return _cache_instance
