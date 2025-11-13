# BWW Store Package - Development Guide

> **Complete Development and Architecture Guide for BWW Store API Client**

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Module Structure](#module-structure)
3. [Core Components](#core-components)
4. [Development Setup](#development-setup)
5. [Code Organization](#code-organization)
6. [Design Patterns](#design-patterns)
7. [Testing Strategy](#testing-strategy)
8. [Contributing Guidelines](#contributing-guidelines)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   BWWStoreAPIService                        │
│                    (Main Interface)                         │
└───────────┬─────────────────────────────────────────────────┘
            │
            ├──► BWWStoreClient (HTTP Client + Caching)
            │    ├── Request Manager
            │    ├── LRU Cache (200 items, TTL 5-60 min)
            │    ├── Rate Limiter (60 req/min)
            │    ├── Circuit Breaker (5 failures threshold)
            │    └── Retry Logic (exponential backoff)
            │
            ├──► SearchEngine (Smart Search)
            │    ├── Egyptian Dialect Processor
            │    ├── Fuzzy Matcher (rapidfuzz)
            │    ├── Keyword Extractor
            │    └── Query Normalizer
            │
            ├──► ProductOperations (Product Management)
            │    ├── Filtering (category, color, price)
            │    ├── Sorting
            │    └── Pagination
            │
            ├──► ProductFormatter (Messenger Integration)
            │    ├── Card Formatter
            │    ├── Button Generator
            │    └── Image URL Builder
            │
            ├──► CardGenerator (Card Templates)
            │    └── Messenger Card Builder
            │
            └──► ComparisonTool (Product Comparison)
                 ├── Price Comparison
                 ├── Rating Comparison
                 └── Best Deal Finder
```

### Layer Architecture

```
┌──────────────────────────────────────┐
│   Presentation Layer (API Service)   │  ← BWWStoreAPIService
├──────────────────────────────────────┤
│   Business Logic Layer               │  ← SearchEngine, ProductOps
├──────────────────────────────────────┤
│   Infrastructure Layer               │  ← BWWStoreClient, Cache
├──────────────────────────────────────┤
│   Data Layer (Models)                │  ← ProductInfo, APIResponse
└──────────────────────────────────────┘
```

---

## Module Structure

### Package Layout

```
bww_store/
├── __init__.py              # Package exports
├── api_client.py            # Main API service interface
├── client.py                # HTTP client + cache + reliability
├── search.py                # Smart search engine
├── product_ops.py           # Product operations (filter, sort)
├── product_formatter.py     # Messenger card formatting
├── card_generator.py        # Card template generation
├── comparison_tool.py       # Product comparison logic
├── models.py                # Data models (dataclasses)
├── constants.py             # Static data (keywords, corrections)
├── base.py                  # Base classes and utilities
├── utils.py                 # Helper functions
├── pyproject.toml           # Package metadata
├── README.md                # User documentation
├── CHANGELOG.md             # Version history
├── LICENSE                  # MIT License
└── docs/
    ├── PRODUCTION.md        # Production deployment guide
    └── DEVELOPMENT.md       # This file
```

### Module Dependencies

```
api_client.py
    ├── client.py
    ├── search.py
    ├── product_ops.py
    ├── product_formatter.py
    ├── card_generator.py
    ├── comparison_tool.py
    └── models.py

client.py
    ├── models.py
    ├── base.py
    └── utils.py

search.py
    ├── constants.py
    └── models.py

product_ops.py
    └── models.py

All modules depend on:
    └── typing, logging, asyncio
```

---

## Core Components

### 1. BWWStoreAPIService (`api_client.py`)

**Purpose**: Main interface for all BWW Store operations

**Key Methods**:
```python
class BWWStoreAPIService:
    # Search
    async def search_and_format_products(query: str, limit: int) -> List[Dict]
    
    # Product Details
    async def get_product_details(product_id: int) -> APIResponse
    
    # Filtering
    async def search_products_by_text(query: str) -> List[Dict]
    async def get_products_by_category(category: str) -> List[Dict]
    async def get_products_by_color(color: str) -> List[Dict]
    async def get_products_by_price_range(min_price: float, max_price: float) -> List[Dict]
    async def filter_products(**filters) -> List[Dict]
    
    # Cards & Comparison
    async def generate_product_card(product: Dict, language: str) -> Dict
    async def compare_products(product_ids: List[int], language: str) -> Dict
    
    # Status
    def get_service_status() -> Dict
```

**Design Pattern**: Facade Pattern
- Provides unified interface to complex subsystem
- Delegates to specialized components

### 2. BWWStoreClient (`client.py`)

**Purpose**: HTTP client with enterprise reliability features

**Key Features**:
- **LRU Cache**: 200 items max, TTL-based expiration
- **Rate Limiting**: 60 requests/minute
- **Circuit Breaker**: 5 failures → open circuit for 60s
- **Retry Logic**: 3 attempts with exponential backoff
- **Request Queuing**: Automatic when rate limit reached

**Key Methods**:
```python
class BWWStoreClient(BaseClient):
    async def make_request(
        endpoint: str,
        method: str = "GET",
        params: Dict = None,
        cache_strategy: CacheStrategy = CacheStrategy.MEDIUM_TERM
    ) -> APIResponse
    
    def _get_cached_response(cache_key: str) -> Optional[APIResponse]
    def _cache_response(cache_key: str, response: APIResponse, ttl: int)
    def _is_rate_limited() -> bool
    def _is_circuit_breaker_open() -> bool
```

**Design Patterns**:
- Circuit Breaker Pattern (fault tolerance)
- Cache-Aside Pattern (performance)
- Rate Limiting Pattern (API protection)

### 3. SearchEngine (`search.py`)

**Purpose**: Intelligent search with Egyptian dialect support

**Key Features**:
- Egyptian dialect normalization
- Fuzzy matching (typo tolerance)
- Keyword extraction
- Multi-language support

**Key Methods**:
```python
class SearchEngine:
    def normalize_egyptian_query(query: str) -> str
    def extract_keywords(query: str, language: str) -> List[str]
    def fuzzy_match_products(query: str, products: List[Dict]) -> List[Dict]
    async def search(query: str, language: str) -> List[Dict]
```

**Algorithm**:
1. Normalize Egyptian dialect → Standard Arabic
2. Extract clothing keywords
3. Call API with normalized query
4. Apply fuzzy matching to results
5. Rank by relevance

### 4. ProductOperations (`product_ops.py`)

**Purpose**: Product filtering and manipulation

**Key Methods**:
```python
class ProductOperations:
    def filter_by_category(products: List[Dict], category: str) -> List[Dict]
    def filter_by_color(products: List[Dict], color: str) -> List[Dict]
    def filter_by_price_range(products: List[Dict], min_price: float, max_price: float) -> List[Dict]
    def filter_by_text(products: List[Dict], query: str) -> List[Dict]
    def sort_by_price(products: List[Dict], ascending: bool = True) -> List[Dict]
    def sort_by_rating(products: List[Dict], ascending: bool = False) -> List[Dict]
```

**Design Pattern**: Strategy Pattern
- Filters are interchangeable strategies
- Can combine multiple filters

### 5. ProductFormatter (`product_formatter.py`)

**Purpose**: Format products for Messenger cards

**Key Methods**:
```python
class ProductFormatter:
    def format_product_for_messenger(product: Dict, language: str) -> Dict
    def format_multiple_products(products: List[Dict], language: str) -> List[Dict]
    def build_product_url(product_id: int, slug: str, language: str) -> str
```

**Output Structure**:
```python
{
    "id": 123,
    "name": "Product Name",
    "price": "299.99 EGP",
    "rating": "⭐⭐⭐⭐⭐ (4.5)",
    "stock": "متوفر (50)",
    "image_url": "https://...",
    "link": "https://bww-store.com/ar/product-details/slug/123"
}
```

### 6. CardGenerator (`card_generator.py`)

**Purpose**: Generate Messenger card templates

**Key Methods**:
```python
class CardGenerator:
    def generate_product_card(product: Dict, language: str) -> Dict
    def generate_comparison_card(products: List[Dict], language: str) -> Dict
```

**Card Structure**:
```python
{
    "card_content": {
        "title": "Product Name",
        "subtitle": "299 EGP • ⭐ 4.5 • متوفر",
        "image_url": "https://...",
        "buttons": [
            {
                "type": "web_url",
                "url": "https://bww-store.com/ar/product-details/slug/123",
                "title": "🛒 عرض المنتج"
            }
        ]
    }
}
```

### 7. ComparisonTool (`comparison_tool.py`)

**Purpose**: Compare products side-by-side

**Key Methods**:
```python
class ComparisonTool:
    async def compare_products(product_ids: List[int], language: str) -> Dict
    def find_best_deal(products: List[Dict]) -> Dict
```

**Output Structure**:
```python
{
    "title": "مقارنة المنتجات",
    "items": [
        {"name": "Product 1", "price": 299, "rating": 4.5},
        {"name": "Product 2", "price": 399, "rating": 4.0}
    ],
    "best_deal": {"name": "Product 1", "price": 299},
    "summary": "أفضل سعر: Product 1 (299 EGP)"
}
```

---

## Development Setup

### 1. Prerequisites

```bash
# Python 3.9+
python --version

# Virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install aiohttp>=3.8.0 pytz>=2023.0 rapidfuzz>=3.0.0

# Development dependencies
pip install pytest pytest-asyncio pytest-mock black flake8 mypy
```

### 3. Project Structure

```bash
cd f:\working - yoans\Migochat
ls bww_store/  # Verify package exists
```

### 4. Run Tests

```bash
# Run all BWW Store tests
pytest tests/test_bww_store.py -v

# Run specific test category
pytest tests/test_bww_store.py -m bww_store -v
pytest tests/test_bww_store.py -m unit -v
pytest tests/test_bww_store.py -m critical -v

# Run with coverage
pytest tests/test_bww_store.py --cov=bww_store --cov-report=html
```

---

## Code Organization

### Naming Conventions

```python
# Classes: PascalCase
class BWWStoreAPIService:
    pass

# Functions/Methods: snake_case
async def search_and_format_products(query: str) -> List[Dict]:
    pass

# Constants: UPPER_SNAKE_CASE
EGYPTIAN_CORRECTIONS = {...}
MAX_CACHE_SIZE = 200

# Private methods: _snake_case
def _get_cached_response(self, key: str) -> Optional[APIResponse]:
    pass

# Type hints: Always use typing module
from typing import List, Dict, Optional, Any
```

### File Organization

```python
# Standard structure for each module:

"""
Module docstring explaining purpose
"""

# 1. Imports
import asyncio
import logging
from typing import List, Dict, Optional

from .models import APIResponse
from .constants import KEYWORDS

# 2. Module-level constants
logger = logging.getLogger(__name__)

# 3. Classes
class MyClass:
    """Class docstring"""
    
    def __init__(self):
        """Initialize"""
        pass
    
    def public_method(self):
        """Public method docstring"""
        pass
    
    def _private_method(self):
        """Private method docstring"""
        pass

# 4. Module-level functions
def utility_function():
    """Utility function docstring"""
    pass
```

### Logging Standards

```python
import logging

logger = logging.getLogger(__name__)

# Log levels:
logger.debug("Detailed diagnostic info")    # Development only
logger.info("Normal operation info")        # General info
logger.warning("Warning condition")          # Potential issues
logger.error("Error occurred")               # Errors
logger.critical("Critical failure")          # System failures

# Log format:
logger.info(f"Product {product_id} fetched in {elapsed_ms}ms")
logger.error(f"API request failed: {error}", exc_info=True)
```

---

## Design Patterns

### 1. Facade Pattern

**Where**: `BWWStoreAPIService`

**Purpose**: Provide simple interface to complex subsystem

```python
class BWWStoreAPIService:
    """Facade for all BWW Store operations"""
    
    def __init__(self, language: str = "ar"):
        # Initialize all subsystems
        self.client = BWWStoreClient()
        self.search = SearchEngine()
        self.products = ProductOperations()
        # ... etc
    
    async def search_and_format_products(self, query: str, limit: int):
        # Delegate to multiple subsystems
        results = await self.search.search(query, self.language)
        filtered = self.products.filter_by_text(results, query)
        formatted = self.formatter.format_multiple_products(filtered)
        return formatted[:limit]
```

### 2. Strategy Pattern

**Where**: `ProductOperations` filters

**Purpose**: Interchangeable filtering strategies

```python
class ProductOperations:
    def filter_products(self, products: List[Dict], **filters) -> List[Dict]:
        """Apply multiple filter strategies"""
        result = products
        
        if 'category' in filters:
            result = self.filter_by_category(result, filters['category'])
        
        if 'color' in filters:
            result = self.filter_by_color(result, filters['color'])
        
        if 'min_price' in filters and 'max_price' in filters:
            result = self.filter_by_price_range(
                result, filters['min_price'], filters['max_price']
            )
        
        return result
```

### 3. Circuit Breaker Pattern

**Where**: `BWWStoreClient`

**Purpose**: Prevent cascading failures

```python
class BWWStoreClient:
    def __init__(self):
        self._circuit_breaker_state = "closed"  # closed, open, half_open
        self._failure_count = 0
        self._circuit_breaker_threshold = 5
        self._circuit_open_time = None
    
    def _is_circuit_breaker_open(self) -> bool:
        if self._circuit_breaker_state == "open":
            # Check if recovery time has passed (60 seconds)
            if time.time() - self._circuit_open_time > 60:
                self._circuit_breaker_state = "half_open"
                return False
            return True
        return False
    
    async def make_request(self, endpoint: str) -> APIResponse:
        if self._is_circuit_breaker_open():
            return APIResponse(
                success=False,
                error="Service temporarily unavailable",
                status_code=503
            )
        
        try:
            response = await self._do_request(endpoint)
            self._failure_count = 0  # Reset on success
            return response
        except Exception as e:
            self._failure_count += 1
            if self._failure_count >= self._circuit_breaker_threshold:
                self._circuit_breaker_state = "open"
                self._circuit_open_time = time.time()
            raise
```

### 4. Cache-Aside Pattern

**Where**: `BWWStoreClient`

**Purpose**: Improve performance with caching

```python
class BWWStoreClient:
    async def make_request(self, endpoint: str, cache_strategy: CacheStrategy) -> APIResponse:
        # 1. Check cache first
        cache_key = self._build_cache_key(endpoint)
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        # 2. Cache miss - fetch from API
        response = await self._do_request(endpoint)
        
        # 3. Store in cache
        ttl = self._get_ttl_for_strategy(cache_strategy)
        self._cache_response(cache_key, response, ttl)
        
        return response
```

### 5. Builder Pattern

**Where**: `CardGenerator`

**Purpose**: Construct complex Messenger cards

```python
class CardGenerator:
    def generate_product_card(self, product: Dict, language: str) -> Dict:
        # Build card step by step
        card = {}
        
        # 1. Build title
        card["title"] = product.get("name", "Unknown")
        
        # 2. Build subtitle (price + rating + stock)
        subtitle_parts = []
        if product.get("final_price"):
            subtitle_parts.append(f"{product['final_price']} EGP")
        if product.get("rating"):
            subtitle_parts.append(f"⭐ {product['rating']}")
        if product.get("stock_quantity"):
            stock_text = "متوفر" if language == "ar" else "In Stock"
            subtitle_parts.append(stock_text)
        card["subtitle"] = " • ".join(subtitle_parts)
        
        # 3. Build image
        card["image_url"] = product.get("main_image", "")
        
        # 4. Build buttons
        card["buttons"] = self._build_buttons(product, language)
        
        return {"card_content": card}
```

---

## Testing Strategy

### Test Categories

```python
# 1. Unit Tests - Test individual components
@pytest.mark.bww_store
@pytest.mark.unit
class TestBWWStoreModels:
    def test_api_response_success(self):
        response = APIResponse(data={}, success=True)
        assert response.success is True

# 2. Integration Tests - Test component interactions
@pytest.mark.bww_store
@pytest.mark.integration
class TestBWWStoreProjectIntegration:
    def test_imported_in_routes_api(self):
        from Server.routes.api import BWWStoreAPIService
        assert BWWStoreAPIService is not None

# 3. Critical Tests - Must pass for package to work
@pytest.mark.bww_store
@pytest.mark.critical
class TestBWWStoreCritical:
    def test_can_import_main_service(self):
        from bww_store import BWWStoreAPIService
        assert BWWStoreAPIService is not None

# 4. Smoke Tests - Quick health checks
@pytest.mark.bww_store
@pytest.mark.smoke
class TestBWWStoreSmoke:
    def test_import_package(self):
        import bww_store
        assert bww_store is not None
```

### Test Coverage Goals

- **Unit Tests**: 80% coverage minimum
- **Integration Tests**: 60% coverage minimum
- **Critical Paths**: 100% coverage required
- **Overall**: 75% coverage target

### Running Tests

```bash
# All tests
pytest tests/test_bww_store.py -v

# By marker
pytest tests/test_bww_store.py -m unit
pytest tests/test_bww_store.py -m critical

# With coverage
pytest tests/test_bww_store.py --cov=bww_store --cov-report=term-missing
```

---

## Contributing Guidelines

### 1. Code Style

```bash
# Use Black for formatting
black bww_store/

# Use flake8 for linting
flake8 bww_store/ --max-line-length=100

# Use mypy for type checking
mypy bww_store/ --strict
```

### 2. Type Hints

```python
# Always use type hints
from typing import List, Dict, Optional, Any

def my_function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """Function with proper type hints"""
    return {"result": param1}

# Use Protocol for interfaces
from typing import Protocol

class Searchable(Protocol):
    async def search(self, query: str) -> List[Dict]:
        ...
```

### 3. Documentation

```python
def complex_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    Short description of function (one line)
    
    Longer description with more details about what the function does,
    any important considerations, and usage examples.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Dictionary containing:
            - key1: Description
            - key2: Description
    
    Raises:
        ValueError: When param2 is negative
        TypeError: When param1 is not a string
    
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result["key1"])
        "value1"
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")
    
    return {"key1": param1, "key2": param2}
```

### 4. Commit Messages

```
Format: <type>(<scope>): <subject>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes (formatting)
- refactor: Code refactoring
- test: Test additions/changes
- chore: Maintenance tasks

Examples:
feat(search): Add Egyptian dialect support
fix(cache): Fix TTL calculation for long-term cache
docs(readme): Update installation instructions
refactor(client): Simplify retry logic
test(search): Add fuzzy matching tests
```

---

## Appendix

### A. Egyptian Dialect Examples

```python
EGYPTIAN_CORRECTIONS = {
    "عايز": "أريد",          # I want
    "محتاج": "أحتاج",        # I need
    "كتير": "كثير",         # Many/much
    "جميل": "جميل",         # Beautiful
    "حلو": "جميل",          # Nice/beautiful
    # ... 50+ corrections
}
```

### B. Cache TTL Values

```python
CacheStrategy.NO_CACHE: 0 seconds
CacheStrategy.SHORT_TERM: 300 seconds (5 minutes)
CacheStrategy.MEDIUM_TERM: 900 seconds (15 minutes)
CacheStrategy.LONG_TERM: 3600 seconds (60 minutes)
```

### C. API Endpoints

```python
BASE_URL = "https://api-v1.bww-store.com"

Endpoints:
- GET /products              # List all products
- GET /products/{id}         # Get product by ID
- GET /products/search       # Search products
- GET /categories            # List categories
```

---

**Version**: 1.0.0  
**Last Updated**: November 13, 2025  
**Maintainer**: BWW Store AI Assistant
