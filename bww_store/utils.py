"""
BWW Store Utilities

This module contains utility functions and helper methods for the BWW Store API client.
"""

import asyncio
from typing import Any, Dict

from .models import APIResponse, CacheStrategy


def format_product_for_messenger(product: Any, language: str = "ar") -> str:
    """Format product information for Messenger display.

    This is a compatibility wrapper around the product_formatter module.

    Args:
        product: Product data (dict or ProductInfo)
        language: Language code ("ar" or "en")

    Returns:
        Formatted product string for Messenger
    """
    from .product_formatter import format_product_for_messenger
    return format_product_for_messenger(product, language)


class CompatibilityWrapper:
    """Compatibility wrapper for existing API usage patterns."""

    def __init__(self, client: Any) -> None:
        """Initialize compatibility wrapper.

        Args:
            client: BWWStoreAPIService instance
        """
        self.client = client

    def make_request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """Make HTTP request with synchronous interface for compatibility.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments

        Returns:
            Response data (dict from APIResponse or APIResponse object)
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        async def _async_request() -> Any:
            data = kwargs.get("data")
            cache_strategy: CacheStrategy = kwargs.get(
                "cache_strategy", CacheStrategy.MEDIUM_TERM
            )
            result: APIResponse = await self.client.client.request(
                method, endpoint, data, cache_strategy
            )
            return result.__dict__ if hasattr(result, "__dict__") else result

        result: Any = loop.run_until_complete(_async_request())
        return result


def create_error_response(error: str, status_code: int = 500) -> APIResponse:
    """Create a standardized error response.

    Args:
        error: Error message
        status_code: HTTP status code

    Returns:
        APIResponse with error
    """
    return APIResponse(success=False, error=error, status_code=status_code)


def validate_product_data(product: Dict[str, Any]) -> bool:
    """Validate basic product data structure.

    Args:
        product: Product data dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["id", "name"]
    return all(field in product and product[field] for field in required_fields)


def sanitize_search_text(text: str) -> str:
    """Sanitize and normalize search text.

    Args:
        text: Raw search text

    Returns:
        Sanitized search text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = " ".join(text.split())

    # Remove potentially harmful characters
    import re
    text = re.sub(r'[<>]', '', text)

    return text.strip()


def calculate_cache_hit_rate(total_requests: int, cache_hits: int) -> float:
    """Calculate cache hit rate percentage.

    Args:
        total_requests: Total number of requests
        cache_hits: Number of cache hits

    Returns:
        Hit rate as percentage (0.0 to 100.0)
    """
    if total_requests == 0:
        return 0.0
    return (cache_hits / total_requests) * 100.0


def format_price_range(min_price: float, max_price: float, currency: str = "جنيه") -> str:
    """Format price range for display.

    Args:
        min_price: Minimum price
        max_price: Maximum price
        currency: Currency symbol

    Returns:
        Formatted price range string
    """
    return f"{min_price}-{max_price} {currency}"


def extract_product_ids_from_text(text: str) -> list[int]:
    """Extract product IDs from text using regex.

    Args:
        text: Text containing product IDs

    Returns:
        List of extracted product IDs
    """
    import re
    # Match 3-6 digit numbers (typical product ID range)
    matches = re.findall(r'\b(\d{3,6})\b', text)
    return [int(match) for match in matches if 100 <= int(match) <= 999999]


def is_valid_product_url(url: str) -> bool:
    """Check if URL is a valid BWW Store product URL.

    Args:
        url: URL to validate

    Returns:
        True if valid product URL, False otherwise
    """
    if not url:
        return False

    return "bww-store.com" in url and (
        "/product" in url or "/product-details" in url or "/products" in url
    )
