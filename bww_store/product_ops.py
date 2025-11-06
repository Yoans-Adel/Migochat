"""
BWW Store Product Operations

This module contains product-related operations including product details,
comparison, card generation, and data downloading functionality.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .card_generator import generate_product_card
from .client import BWWStoreAPIClient
from .comparison_tool import format_comparison_ar, format_comparison_en
from .models import APIResponse, CacheStrategy

logger = logging.getLogger(__name__)


class BWWStoreProductOperations:
    """Product operations for BWW Store API."""

    def __init__(self, client: BWWStoreAPIClient):
        """Initialize product operations with API client.

        Args:
            client: BWWStoreAPIClient instance
        """
        self.client = client

    async def get_product_details(self, product_id: int, *, cache_strategy: CacheStrategy = CacheStrategy.LONG_TERM) -> APIResponse:
        """Get detailed information for a specific product.

        Tries multiple API endpoints to ensure compatibility:
        1. /product-details/{product_id} (newer format)
        2. /product/{product_id} (fallback format)

        Args:
            product_id: The product ID to fetch
            cache_strategy: Caching strategy for the request

        Returns:
            APIResponse with product details or error
        """
        # Try the newer product-details endpoint first
        result = await self.client._request("GET", f"/product-details/{product_id}", cache_strategy=cache_strategy)  # type: ignore[attr-defined]
        if result.success:
            return result

        # Fallback to the older product endpoint
        logger.debug(f"Product-details endpoint failed for {product_id}, trying fallback endpoint")
        return await self.client._request("GET", f"/product/{product_id}", cache_strategy=cache_strategy)  # type: ignore[attr-defined]

    async def search_products_by_text(self, search_text: str, *, page: int = 1, page_size: int = 10) -> APIResponse:
        """Search products by text query.

        Args:
            search_text: Search query
            page: Page number
            page_size: Number of products per page

        Returns:
            APIResponse with search results
        """
        return await self.client.filter_products(search=search_text, page=page, page_size=page_size, cache_strategy=CacheStrategy.SHORT_TERM)

    async def get_products_by_category(self, category: str, *, page: int = 1, page_size: int = 10) -> APIResponse:
        """Get products by category.

        Args:
            category: Category name
            page: Page number
            page_size: Number of products per page

        Returns:
            APIResponse with products
        """
        return await self.client.filter_products(category=category, page=page, page_size=page_size)

    async def get_products_by_color(self, colors: List[str], *, page: int = 1, page_size: int = 10) -> APIResponse:
        """Get products by color.

        Args:
            colors: List of colors
            page: Page number
            page_size: Number of products per page

        Returns:
            APIResponse with products
        """
        return await self.client.filter_products(colors=colors, page=page, page_size=page_size)

    async def get_products_by_price_range(self, min_price: float, max_price: float, *, page: int = 1, page_size: int = 10) -> APIResponse:
        """Get products within a specific price range with local filtering since API price filtering doesn't work.

        Args:
            min_price: Minimum price
            max_price: Maximum price
            page: Page number
            page_size: Number of products per page

        Returns:
            APIResponse with filtered products
        """
        # Get a larger set of products and filter locally since API price filtering is broken
        result = await self.client.filter_products(page_size=page_size * 3)  # Get more products to filter from

        if not result.success:
            return result

        all_products = result.data.get("data", {}).get("products", [])

        # Filter products by price range locally
        filtered_products: List[Dict[str, Any]] = []
        for product in all_products:
            price = product.get("final_price", 0)
            if min_price <= price <= max_price:
                filtered_products.append(product)

        # Apply pagination to filtered results
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_products: List[Dict[str, Any]] = filtered_products[start_idx:end_idx]

        # Return filtered results in the same API format
        filtered_response: Dict[str, Any] = {
            "data": {
                "products": paginated_products,
                "total": len(filtered_products),
                "page": page,
                "page_size": page_size
            }
        }

        return APIResponse(data=filtered_response, success=True)

    async def generate_product_card(self, product: Dict[str, Any], *, language: str = "ar") -> Dict[str, Any]:
        """Generate a clean product card for Messenger display.

        Args:
            product: Product data dictionary
            language: Language code ("ar" for Arabic, "en" for English)

        Returns:
            Dictionary with card content and metadata
        """
        return generate_product_card(product, language)

    async def compare_products(self, product_ids: List[int], *, language: str = "ar") -> str:
        """Compare multiple products side by side.

        Args:
            product_ids: List of product IDs to compare
            language: Language code

        Returns:
            Formatted comparison string
        """
        if not product_ids:
            return "❌ لم يتم تحديد منتجات للمقارنة" if language == "ar" else "❌ No products specified for comparison"
        product_ids = product_ids[:4]

        all_products: List[Dict[str, Any]] = []
        res = await self.client.filter_products(page_size=100)
        if res.success and isinstance(res.data, dict):
            all_products = res.data.get("data", {}).get("products", []) or []

        found: List[Dict[str, Any]] = []
        for pid in product_ids:
            for pr in all_products:
                if pr.get("id") == pid:
                    found.append(pr)
                    break
            else:
                detail = await self.get_product_details(pid)
                if detail.success and isinstance(detail.data, dict):
                    found.append(detail.data)

        if not found:
            return "❌ لم يتم العثور على المنتجات المطلوبة" if language == "ar" else "❌ Products not found"
        return format_comparison_en(found) if language == "en" else format_comparison_ar(found)

    async def download_products_for_comparison(self, *, limit: int = 100, save_to_temp: bool = True) -> Dict[str, Any]:
        """Download products to temp directory for comparison analysis.

        Downloads a comprehensive set of products and saves them to temp files
        for offline comparison of prices, deals, sizes, categories, etc.

        Args:
            limit: Maximum number of products to download (default: 100)
            save_to_temp: Whether to save to temp directory (default: True)

        Returns:
            Dictionary with download statistics and file paths
        """
        try:
            # Create temp directory if it doesn't exist
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)

            logger.info(f"Starting product download for comparison (limit: {limit})")

            # Get products from API
            result = await self.client.filter_products(page_size=min(limit, 100))
            if not result.success:
                return {
                    "success": False,
                    "error": f"Failed to fetch products: {result.error}",
                    "downloaded": 0,
                    "files": []
                }

            products = result.data.get("data", {}).get("products", [])
            if not products:
                return {
                    "success": False,
                    "error": "No products found",
                    "downloaded": 0,
                    "files": []
                }

            # Limit the products
            products = products[:limit]

            saved_files: List[str] = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if save_to_temp:
                # Save all products to a single file
                all_products_file = temp_dir / f"bww_products_comparison_{timestamp}.json"
                with open(all_products_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "metadata": {
                            "downloaded_at": datetime.now(timezone.utc).isoformat(),
                            "total_products": len(products),
                            "language": self.client.language,
                            "api_url": self.client.base_url
                        },
                        "products": products
                    }, f, ensure_ascii=False, indent=2)
                saved_files.append(str(all_products_file))

                # Save products by category
                categories: Dict[str, List[Dict[str, Any]]] = {}
                for product in products:
                    category_name = str(product.get("category", {}).get("name", "unknown")).lower().replace(" ", "_")
                    if category_name not in categories:
                        categories[category_name] = []
                    categories[category_name].append(product)

                for category_name, category_products in categories.items():
                    if len(category_products) >= 3:  # Only save categories with multiple products
                        category_file = temp_dir / f"bww_{category_name}_{timestamp}.json"
                        with open(category_file, 'w', encoding='utf-8') as f:
                            json.dump({
                                "metadata": {
                                    "category": category_name,
                                    "downloaded_at": datetime.now(timezone.utc).isoformat(),
                                    "total_products": len(category_products),
                                    "language": self.client.language
                                },
                                "products": category_products
                            }, f, ensure_ascii=False, indent=2)
                        saved_files.append(str(category_file))

                # Save price analysis data
                prices: List[float] = [p.get("final_price", 0) for p in products if p.get("final_price", 0) > 0]
                if prices:
                    price_analysis: Dict[str, Any] = {
                        "metadata": {
                            "analysis_type": "price_comparison",
                            "downloaded_at": datetime.now(timezone.utc).isoformat(),
                            "total_products": len(prices)
                        },
                        "price_stats": {
                            "min_price": min(prices),
                            "max_price": max(prices),
                            "avg_price": sum(prices) / len(prices),
                            "total_range": max(prices) - min(prices)
                        },
                        "price_ranges": {
                            "under_100": len([p for p in prices if p < 100]),
                            "100_500": len([p for p in prices if 100 <= p < 500]),
                            "500_1000": len([p for p in prices if 500 <= p < 1000]),
                            "over_1000": len([p for p in prices if p >= 1000])
                        },
                        "products_by_price": sorted(products, key=lambda x: x.get("final_price", 0))
                    }

                    price_file = temp_dir / f"bww_price_analysis_{timestamp}.json"
                    with open(price_file, 'w', encoding='utf-8') as f:
                        json.dump(price_analysis, f, ensure_ascii=False, indent=2)
                    saved_files.append(str(price_file))

            logger.info(f"Successfully downloaded {len(products)} products to {len(saved_files)} files")

            # Initialize with defaults for potentially unbound variables
            categories_count = len(categories) if 'categories' in locals() else 0
            price_stats = None
            if 'prices' in locals() and prices:
                price_stats = {
                    "min": min(prices),
                    "max": max(prices),
                    "avg": sum(prices) / len(prices)
                }

            return {
                "success": True,
                "downloaded": len(products),
                "files": saved_files,
                "categories_found": categories_count,
                "timestamp": timestamp,
                "price_range": price_stats
            }

        except Exception as exc:
            logger.error(f"Error downloading products for comparison: {exc}")
            return {
                "success": False,
                "error": str(exc),
                "downloaded": 0,
                "files": []
            }

    async def load_products_from_temp(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load previously downloaded products from temp directory.

        Args:
            filename: Name of the file to load (without path)

        Returns:
            Product data dictionary or None if file not found
        """
        try:
            temp_dir = Path("temp")
            file_path = temp_dir / filename

            if not file_path.exists():
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as exc:
            logger.error(f"Error loading products from temp file {filename}: {exc}")
            return None

    async def find_product_by_input(self, input_text: str) -> Optional[Dict[str, Any]]:
        """Find a product by ID or search term.

        Args:
            input_text: Product ID (number) or search term

        Returns:
            Product data dictionary or None if not found
        """
        try:
            input_text = input_text.strip()

            # Try to parse as direct product ID
            try:
                product_id = int(input_text)
                result = await self.get_product_details(product_id)
                if result.success and isinstance(result.data, dict):
                    return result.data
            except ValueError:
                pass

            # Try search
            result = await self.search_products_by_text(input_text, page_size=5)
            if result.success and isinstance(result.data, dict):
                products = result.data.get("data", {}).get("products", [])
                if products:
                    # Return the best match (first result)
                    return products[0]

            return None

        except Exception as exc:
            logger.error(f"Error finding product by input '{input_text}': {exc}")
            return None
