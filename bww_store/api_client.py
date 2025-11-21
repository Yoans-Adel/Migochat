"""
BWW Store API Client - Main Service Interface

This module provides the main BWWStoreAPIService class that combines all
modular components into a unified API client interface.

The service integrates:
- HTTP client with caching and rate limiting (client.py)
- Intelligent search capabilities (search.py)
- Product operations and utilities (product_ops.py)
- Helper functions and compatibility (utils.py)

Usage:
    client = BWWStoreAPIService(language="ar")
    result = await client.search_and_format_products("طقم صيفي")
"""

from typing import Any, Dict, List, Optional

from .client import BWWStoreAPIClient
from .models import CacheStrategy
from .product_formatter import format_product_for_messenger
from .product_ops import BWWStoreProductOperations
from .search import BWWStoreSearchEngine
from .utils import CompatibilityWrapper


class BWWStoreAPIService:
    """Main BWW Store API Service - Unified interface combining all modules.

    This service integrates all modular components into a single, easy-to-use
    interface for interacting with the BWW Store API.

    Features:
    - HTTP client with caching and rate limiting
    - Intelligent search with Egyptian dialect support
    - Product operations and card generation
    - Enterprise-grade reliability patterns

    Example:
        >>> client = BWWStoreAPIService(language="ar")
        >>> result = await client.search_and_format_products("طقم صيفي")
        >>> print(result[0])  # Formatted product
    """

    def __init__(self, language: str = "ar"):
        """Initialize the BWW Store API service.

        Args:
            language: Default language ("ar" for Arabic, "en" for English)
        """
        # Initialize core components
        self.client = BWWStoreAPIClient(language)
        self.search = BWWStoreSearchEngine(self.client)
        self.products = BWWStoreProductOperations(self.client)
        self.compatibility = CompatibilityWrapper(self)

        # Expose key attributes
        self.language = language

    # Search methods
    async def search_and_format_products(self, search_text: str, *, limit: int = 3, language: str = "ar") -> list[str]:
        """Smart search with multiple fallback strategies."""
        return await self.search.search_and_format_products(search_text, limit=limit, language=language)

    # Product methods

    async def get_product_details(self, product_id: int, *, cache_strategy: Optional[CacheStrategy] = None):
        """Get detailed information for a specific product."""
        strategy = cache_strategy or CacheStrategy.MEDIUM_TERM
        return await self.products.get_product_details(product_id, cache_strategy=strategy)

    async def search_products_by_text(self, search_text: str, *, page: int = 1, page_size: int = 10):
        """Search products by text query."""
        return await self.products.search_products_by_text(search_text, page=page, page_size=page_size)

    async def get_products_by_category(self, category: str, *, page: int = 1, page_size: int = 10):
        """Get products by category."""
        return await self.products.get_products_by_category(category, page=page, page_size=page_size)

    async def get_products_by_color(self, colors: list[str], *, page: int = 1, page_size: int = 10):
        """Get products by color."""
        return await self.products.get_products_by_color(colors, page=page, page_size=page_size)

    async def get_products_by_price_range(self, min_price: float, max_price: float, *, page: int = 1, page_size: int = 10):
        """Get products within a price range."""
        return await self.products.get_products_by_price_range(min_price, max_price, page=page, page_size=page_size)

    async def filter_products(self, *, search: Optional[str] = None, product_code: Optional[str] = None,
                              colors: Optional[List[str]] = None, sizes: Optional[List[str]] = None,
                              material: Optional[str] = None, sku_code: Optional[str] = None,
                              category: Optional[str] = None, min_price: Optional[float] = None,
                              max_price: Optional[float] = None, page: int = 1, page_size: int = 10,
                              cache_strategy: Optional[CacheStrategy] = None):
        """Filter products with various criteria."""
        strategy = cache_strategy or CacheStrategy.MEDIUM_TERM
        return await self.client.filter_products(
            search=search, product_code=product_code, colors=colors, sizes=sizes,
            material=material, sku_code=sku_code, category=category,
            min_price=min_price, max_price=max_price, page=page, page_size=page_size,
            cache_strategy=strategy
        )

    async def generate_product_card(self, product: Dict[str, Any], *, language: str = "ar") -> Dict[str, Any]:
        """Generate a product card for Messenger display."""
        return await self.products.generate_product_card(product, language=language)

    async def compare_products(self, product_ids: List[int], *, language: str = "ar") -> str:
        """Compare multiple products side by side."""
        return await self.products.compare_products(product_ids, language=language)

    async def download_products_for_comparison(self, *, limit: int = 100, save_to_temp: bool = True) -> Dict[str, Any]:
        """Download products for offline comparison."""
        return await self.products.download_products_for_comparison(limit=limit, save_to_temp=save_to_temp)

    async def load_products_from_temp(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load products from temp directory."""
        return await self.products.load_products_from_temp(filename)

    async def find_product_by_input(self, input_text: str) -> Optional[Dict[str, Any]]:
        """Find product by ID or search term."""
        return await self.products.find_product_by_input(input_text)

    # Utility methods
    def format_product_for_messenger(self, product: Any, language: str = "ar") -> str:
        """Format product for Messenger display."""
        return format_product_for_messenger(product, language)

    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status."""
        return self.client.get_service_status()

    # Compatibility methods
    def make_request(self, method: str, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Make HTTP request (synchronous compatibility)."""
        return self.compatibility.make_request(method, endpoint, **kwargs)
