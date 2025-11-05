"""
Core Data Models and Type Definitions

This module defines the fundamental data structures used throughout the BWW Store
API client. These models provide type safety, serialization support, and consistent
interfaces for API responses and product information.

The models are designed to be immutable where possible (using frozen dataclasses)
and include comprehensive type hints for better IDE support and runtime validation.

Classes:
    CacheStrategy: Enumeration of available caching strategies
    APIResponse: Standardized response format for all API operations
    ProductInfo: Complete product data structure with all metadata

Enums:
    CacheStrategy: Defines TTL-based caching policies

Example:
    >>> response = APIResponse(data={"products": []}, success=True)
    >>> product = ProductInfo(id=123, name="Laptop", final_price=999.99)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class CacheStrategy(Enum):
    """Caching strategy enumeration with predefined TTL policies.

    Defines the available caching strategies for API responses, each with
    different time-to-live durations optimized for different types of data.

    Attributes:
        NO_CACHE: Disable caching entirely (useful for real-time data)
        SHORT_TERM: 5-minute TTL for frequently changing data
        MEDIUM_TERM: 30-minute TTL for moderately stable data
        LONG_TERM: 2-hour TTL for relatively static reference data
    """
    NO_CACHE = "no_cache"
    SHORT_TERM = "short_term"      # 5 minutes - search results, dynamic content
    MEDIUM_TERM = "medium_term"    # 30 minutes - product listings, categories
    LONG_TERM = "long_term"        # 2 hours - product details, static metadata


@dataclass(frozen=True)
class APIResponse:
    """Standardized response structure for all API operations.

    This class provides a consistent interface for all API client operations,
    encapsulating both successful responses and error conditions. It includes
    metadata for performance monitoring, caching status, and debugging.

    Attributes:
        data: The actual response payload (dict, list, or other types)
        success: Boolean indicating if the operation succeeded
        error: Error message if operation failed (None for success)
        status_code: HTTP status code (200 for success, error codes for failures)
        cached: True if response came from cache, False if fresh API call
        response_time_ms: Time taken for the operation in milliseconds
        timestamp: When the response was created/generated

    Example:
        >>> # Successful response
        >>> resp = APIResponse(data={"products": []}, success=True, status_code=200)
        >>> # Error response
        >>> err = APIResponse(success=False, error="Network timeout", status_code=504)
    """
    data: Any = None
    success: bool = True
    error: Optional[str] = None
    status_code: int = 200
    cached: bool = False
    response_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ProductInfo:
    """Comprehensive product information structure.

    Represents a complete product entity from the BWW Store API, including
    all metadata, pricing, availability, and business attributes. This
    structure is used throughout the client for formatting, comparison,
    and display operations.

    Attributes:
        id: Unique product identifier
        name: Product display name
        final_price: Current selling price in EGP
        original_price: Original price before discounts
        discount: Discount percentage (0.0 to 100.0)
        store_name: Name of the selling store/brand
        rating: Average customer rating (0.0 to 5.0)
        count_rating: Number of customer reviews
        stock_quantity: Available inventory count
        main_image: URL to primary product image
        category: Category information dictionary
        is_best_seller: Whether product is marked as best seller
        is_new_arrival: Whether product is newly added
        is_free_delivery: Whether free shipping is available
        is_refundable: Whether product can be returned
        colors: List of available color options
        sizes: List of available size options
        material: Primary material composition
        description: Detailed product description

    Example:
        >>> product = ProductInfo(
        ...     id=12345,
        ...     name="Wireless Bluetooth Headphones",
        ...     final_price=299.99,
        ...     rating=4.5,
        ...     colors=["Black", "White", "Blue"]
        ... )
    """
    id: int
    name: str
    final_price: float
    original_price: float
    discount: float
    store_name: str
    rating: float
    count_rating: int
    stock_quantity: int
    main_image: str
    category: Dict[str, Any]
    is_best_seller: bool = False
    is_new_arrival: bool = False
    is_free_delivery: bool = False
    is_refundable: bool = False
    colors: List[str] = field(default_factory=lambda: [])
    sizes: List[str] = field(default_factory=lambda: [])
    material: str = ""
    description: str = ""
