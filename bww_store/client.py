"""
BWW Store API Client Core

This module contains the core HTTP client functionality with caching,
rate limiting, circuit breaking, and basic API operations.
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import pytz

from .base import (
    APIService,
    api_error_handler,
    circuit_breaker,
    retry_on_error,
    RetryConfig,
    CircuitBreakerConfig
)
from .models import APIResponse, CacheStrategy

logger = logging.getLogger(__name__)


class BWWStoreAPIClient(APIService):
    """Core HTTP client for BWW Store API with enterprise-grade reliability features."""

    def __init__(self, language: str = "ar") -> None:
        """Initialize the BWW Store API client.

        Args:
            language: Default language for responses ("ar" for Arabic, "en" for English)
        """
        super().__init__()

        # API Configuration
        self.base_url = "https://api-v1.bww-store.com/api/v1"
        self.secret_key = "BwwSecretKey2025"
        self.language = language if language in ["ar", "en"] else "ar"

        # Enhanced Caching System
        self._cache: Dict[str, Tuple[Any, float, int]] = {}
        self._cache_ttl = {
            CacheStrategy.SHORT_TERM: 3 * 60,      # 3 minutes
            CacheStrategy.MEDIUM_TERM: 15 * 60,    # 15 minutes
            CacheStrategy.LONG_TERM: 60 * 60,      # 1 hour
        }
        self._max_cache_size = 200
        self._cache_cleanup_threshold = 150

        # Rate Limiting
        self._request_times: List[float] = []
        self._max_requests_per_minute = 60

        # Circuit Breaker State
        self._failures = 0
        self._failure_threshold = 5
        self._open_until = 0.0

        logger.info(
            "BWW Store API Client initialized: language=%s, rate_limit=%d/min",
            self.language,
            self._max_requests_per_minute
        )

    def _generate_api_password(self) -> str:
        """Generate time-based API password."""
        cairo_tz = pytz.timezone("Africa/Cairo")
        cairo_time = datetime.now(cairo_tz) - timedelta(hours=3)
        current_hour = cairo_time.strftime("%Y-%m-%d %H")
        return hashlib.sha256(f"{self.secret_key}{current_hour}".encode()).hexdigest()

    def _headers(self) -> Dict[str, str]:
        """Generate API request headers."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-API-PASSWORD": self._generate_api_password(),
            "Accept-Language": "ar" if self.language == "ar" else "en",
            "User-Agent": "Bww-AI-Assistant/1.0",
        }

    def _within_rate_limit(self) -> bool:
        """Check if request is within rate limits."""
        now = time.time()
        self._request_times = [t for t in self._request_times if now - t < 60]
        if len(self._request_times) >= self._max_requests_per_minute:
            return False
        self._request_times.append(now)
        return True

    def _cache_key(self, endpoint: str, payload: Dict[str, Any]) -> str:
        """Generate cache key for request."""
        return hashlib.md5(f"{endpoint}:{json.dumps(payload, sort_keys=True)}".encode()).hexdigest()

    def _cache_get(self, key: str, strategy: CacheStrategy) -> Optional[Any]:
        """Get cached data with access tracking."""
        if strategy == CacheStrategy.NO_CACHE:
            return None

        item = self._cache.get(key)
        if not item:
            return None

        data, ts, access_count = item
        ttl = self._cache_ttl.get(strategy, 300)

        # Check if expired
        if time.time() - ts >= ttl:
            self._cache.pop(key, None)
            return None

        # Update access count for LRU-style cleanup
        self._cache[key] = (data, ts, access_count + 1)
        return data

    def _cache_set(self, key: str, data: Any, strategy: CacheStrategy) -> None:
        """Set cached data with cleanup if needed."""
        if strategy == CacheStrategy.NO_CACHE:
            return

        # Cleanup cache if it gets too large
        if len(self._cache) >= self._max_cache_size:
            self._cleanup_cache()

        self._cache[key] = (data, time.time(), 1)

    def _cleanup_cache(self) -> None:
        """Clean up cache using LRU (Least Recently Used) strategy."""
        if len(self._cache) < self._cache_cleanup_threshold:
            return

        # Sort by access count (ascending) then by timestamp (ascending)
        items = [(k, v[2], v[1]) for k, v in self._cache.items()]
        items.sort(key=lambda x: (x[1], x[2]))  # access_count, then timestamp

        # Remove least accessed/used items (keep only 50% of capacity)
        keep_count = self._max_cache_size // 2
        to_remove = items[:len(items) - keep_count]

        for key, _, _ in to_remove:
            self._cache.pop(key, None)

    @api_error_handler
    @retry_on_error(RetryConfig(max_retries=3, delay=1.0))
    @circuit_breaker("BWWStoreAPIClient", CircuitBreakerConfig(failure_threshold=5))
    async def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None,
                      cache_strategy: CacheStrategy = CacheStrategy.MEDIUM_TERM) -> APIResponse:
        """Make HTTP request with caching and error handling."""
        if not self._within_rate_limit():
            return APIResponse(success=False, error="Rate limit exceeded", status_code=429)

        key = self._cache_key(endpoint, data or {})
        cached = self._cache_get(key, cache_strategy)
        start = time.time()

        if cached is not None:
            return APIResponse(data=cached, success=True, cached=True, response_time_ms=(time.time() - start) * 1000)

        url = f"{self.base_url}{endpoint}"
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30, connect=10)) as session:
                if method.upper() == "GET":
                    async with session.get(url, headers=self._headers()) as resp:
                        payload = await resp.json()
                        status = resp.status
                else:
                    async with session.request(method, url, json=data, headers=self._headers()) as resp:
                        payload = await resp.json()
                        status = resp.status
        except Exception as exc:
            return APIResponse(success=False, error=str(exc), status_code=500, response_time_ms=(time.time() - start) * 1000)

        rtm = (time.time() - start) * 1000
        if status == 200:
            self._cache_set(key, payload, cache_strategy)
            return APIResponse(data=payload, success=True, status_code=status, response_time_ms=rtm)
        return APIResponse(success=False, error=f"API request failed: {status}", status_code=status, response_time_ms=rtm)

    @api_error_handler
    @retry_on_error(RetryConfig(max_retries=3, delay=1.0))
    @circuit_breaker("BWWStoreAPIClient", CircuitBreakerConfig(failure_threshold=5))
    async def filter_products(self, *, search: Optional[str] = None, product_code: Optional[str] = None,
                            colors: Optional[List[str]] = None, sizes: Optional[List[str]] = None,
                            material: Optional[str] = None, sku_code: Optional[str] = None,
                            category: Optional[str] = None, min_price: Optional[float] = None,
                            max_price: Optional[float] = None, page: int = 1, page_size: int = 10,
                            cache_strategy: CacheStrategy = CacheStrategy.MEDIUM_TERM) -> APIResponse:
        """Filter products with various criteria."""
        payload: Dict[str, Any] = {}
        if search:
            payload["search"] = search
        if product_code:
            payload["product_code"] = product_code
        if colors:
            payload["colors"] = colors
        if sizes:
            payload["sizes"] = sizes
        if material:
            payload["material"] = material
        if sku_code:
            payload["sku_code"] = sku_code
        if category:
            payload["category"] = category
        if min_price is not None:
            payload["min_price"] = min_price
        if max_price is not None:
            payload["max_price"] = max_price
        payload["page"] = page
        payload["page_size"] = page_size
        return await self._request("POST", "/filter-products", payload, cache_strategy)

    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status including cache metrics."""
        total_accesses = sum(v[2] for v in self._cache.values()) if self._cache else 0
        cache_hit_rate = 0.0

        # Calculate approximate cache hit rate (simplified)
        if hasattr(self, '_total_requests'):
            cache_hit_rate = (total_accesses / self._total_requests) * 100 if self._total_requests > 0 else 0

        return {
            "name": self.__class__.__name__,
            "initialized": True,
            "api_url": self.base_url,
            "language": self.language,
            "rate_limit": {
                "current_requests": len(self._request_times),
                "max_per_minute": self._max_requests_per_minute
            },
            "cache": {
                "size": len(self._cache),
                "max_size": self._max_cache_size,
                "total_accesses": total_accesses,
                "hit_rate_percent": round(cache_hit_rate, 1),
                "ttl_settings": {
                    "short_term": self._cache_ttl[CacheStrategy.SHORT_TERM],
                    "medium_term": self._cache_ttl[CacheStrategy.MEDIUM_TERM],
                    "long_term": self._cache_ttl[CacheStrategy.LONG_TERM]
                }
            }
        }
