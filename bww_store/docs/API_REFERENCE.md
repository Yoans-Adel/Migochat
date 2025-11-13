# BWW Store Package - API Reference

> **Complete API Reference for all BWW Store Package Components**

## 📋 Table of Contents

1. [BWWStoreAPIService](#bwwstoreapiservice) - Main Interface
2. [BWWStoreClient](#bwwstoreclient) - HTTP Client
3. [SearchEngine](#searchengine) - Smart Search
4. [ProductOperations](#productoperations) - Product Filtering
5. [ProductFormatter](#productformatter) - Messenger Formatting
6. [CardGenerator](#cardgenerator) - Card Generation
7. [ComparisonTool](#comparisontool) - Product Comparison
8. [Models](#models) - Data Models
9. [Constants](#constants) - Static Data

---

## BWWStoreAPIService

**Module**: `bww_store.api_client`

**Purpose**: Main interface for all BWW Store operations

### Initialization

```python
from bww_store import BWWStoreAPIService

client = BWWStoreAPIService(language: str = "ar")
```

**Parameters**:
- `language` (str, optional): Language code - `"ar"` (Arabic) or `"en"` (English). Default: `"ar"`

### Methods

#### `search_and_format_products()`

Smart search with Egyptian dialect support and Messenger formatting.

```python
async def search_and_format_products(
    query: str,
    limit: int = 10
) -> List[Dict[str, Any]]
```

**Parameters**:
- `query` (str): Search query (supports Egyptian dialect)
- `limit` (int, optional): Maximum number of results. Default: 10

**Returns**: List of formatted product dictionaries
```python
[
    {
        "id": 123,
        "name": "Product Name",
        "price": "299.99 EGP",
        "rating": "⭐⭐⭐⭐⭐ (4.5)",
        "stock": "متوفر (50)",
        "image_url": "https://...",
        "link": "https://bww-store.com/ar/product-details/slug/123"
    }
]
```

**Example**:
```python
results = await client.search_and_format_products("عايز طقم صيفي", limit=5)
```

---

#### `get_product_details()`

Get detailed information for a specific product.

```python
async def get_product_details(
    product_id: int
) -> APIResponse
```

**Parameters**:
- `product_id` (int): Product ID

**Returns**: `APIResponse` object
```python
APIResponse(
    data={
        "id": 123,
        "name": "Product Name",
        "final_price": 299.99,
        "original_price": 399.99,
        "discount": 25.0,
        "rating": 4.5,
        "count_rating": 100,
        "stock_quantity": 50,
        "category": {...},
        "colors": [...],
        "sizes": [...],
        # ... more fields
    },
    success=True,
    status_code=200,
    cached=False,
    response_time_ms=245.5
)
```

**Example**:
```python
response = await client.get_product_details(53)
if response.success:
    product = response.data
    print(product["name"])
```

---

#### `search_products_by_text()`

Search products by text query (exact match from API).

```python
async def search_products_by_text(
    query: str
) -> List[Dict[str, Any]]
```

**Parameters**:
- `query` (str): Search text

**Returns**: List of product dictionaries

**Example**:
```python
products = await client.search_products_by_text("طقم رجالي")
```

---

#### `get_products_by_category()`

Filter products by category.

```python
async def get_products_by_category(
    category: str
) -> List[Dict[str, Any]]
```

**Parameters**:
- `category` (str): Category name (e.g., "رجالي", "أطفال", "نسائي")

**Returns**: List of product dictionaries

**Example**:
```python
men_products = await client.get_products_by_category("رجالي")
```

---

#### `get_products_by_color()`

Filter products by color (local filtering).

```python
async def get_products_by_color(
    color: str
) -> List[Dict[str, Any]]
```

**Parameters**:
- `color` (str): Color name (e.g., "أسود", "أبيض", "أزرق")

**Returns**: List of product dictionaries

**Example**:
```python
black_products = await client.get_products_by_color("أسود")
```

---

#### `get_products_by_price_range()`

Filter products by price range (local filtering).

```python
async def get_products_by_price_range(
    min_price: float,
    max_price: float
) -> List[Dict[str, Any]]
```

**Parameters**:
- `min_price` (float): Minimum price (EGP)
- `max_price` (float): Maximum price (EGP)

**Returns**: List of product dictionaries

**Example**:
```python
budget_products = await client.get_products_by_price_range(100, 500)
```

---

#### `filter_products()`

Apply multiple filters to products.

```python
async def filter_products(
    category: Optional[str] = None,
    color: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    text: Optional[str] = None
) -> List[Dict[str, Any]]
```

**Parameters**:
- `category` (str, optional): Category filter
- `color` (str, optional): Color filter
- `min_price` (float, optional): Minimum price
- `max_price` (float, optional): Maximum price
- `text` (str, optional): Text search

**Returns**: List of product dictionaries

**Example**:
```python
filtered = await client.filter_products(
    category="رجالي",
    min_price=200,
    max_price=600,
    color="أسود"
)
```

---

#### `generate_product_card()`

Generate Messenger card for a product.

```python
async def generate_product_card(
    product: Dict[str, Any],
    language: str = "ar"
) -> Dict[str, Any]
```

**Parameters**:
- `product` (dict): Product data from `get_product_details()`
- `language` (str, optional): Language for card text. Default: `"ar"`

**Returns**: Messenger card dictionary
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

**Example**:
```python
response = await client.get_product_details(53)
if response.success:
    card = await client.generate_product_card(response.data, language="ar")
```

---

#### `compare_products()`

Compare multiple products side-by-side.

```python
async def compare_products(
    product_ids: List[int],
    language: str = "ar"
) -> Dict[str, Any]
```

**Parameters**:
- `product_ids` (List[int]): List of product IDs (2-4 products)
- `language` (str, optional): Language for comparison text. Default: `"ar"`

**Returns**: Comparison dictionary
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

**Example**:
```python
comparison = await client.compare_products([53, 50, 48], language="ar")
```

---

#### `get_service_status()`

Get current service status and metrics.

```python
def get_service_status() -> Dict[str, Any]
```

**Returns**: Status dictionary
```python
{
    "service_name": "BWW Store API Client",
    "version": "1.0.0",
    "language": "ar",
    "base_url": "https://api-v1.bww-store.com",
    "cache": {
        "size": 45,
        "max_size": 200,
        "hits": 120,
        "misses": 30,
        "hit_rate": 0.80
    },
    "rate_limit": {
        "max_requests_per_minute": 60,
        "current_requests": 12,
        "requests_remaining": 48
    },
    "circuit_breaker": {
        "state": "closed",  # closed/open/half_open
        "failure_count": 0,
        "threshold": 5
    }
}
```

**Example**:
```python
status = client.get_service_status()
print(f"Cache: {status['cache']['size']}/{status['cache']['max_size']}")
```

---

## Models

**Module**: `bww_store.models`

### APIResponse

Data class for API responses.

```python
@dataclass
class APIResponse:
    data: Optional[Any] = None
    success: bool = False
    error: Optional[str] = None
    status_code: int = 0
    cached: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    response_time_ms: Optional[float] = None
```

**Fields**:
- `data`: Response data (dict, list, etc.)
- `success`: Whether request succeeded
- `error`: Error message (if failed)
- `status_code`: HTTP status code
- `cached`: Whether response came from cache
- `timestamp`: Response timestamp (UTC)
- `response_time_ms`: Response time in milliseconds

**Example**:
```python
from bww_store.models import APIResponse

response = APIResponse(
    data={"products": [...]},
    success=True,
    status_code=200,
    response_time_ms=245.5
)
```

---

### CacheStrategy

Enum for cache TTL strategies.

```python
class CacheStrategy(Enum):
    NO_CACHE = "no_cache"          # 0 seconds (no caching)
    SHORT_TERM = "short_term"      # 5 minutes (300 seconds)
    MEDIUM_TERM = "medium_term"    # 15 minutes (900 seconds)
    LONG_TERM = "long_term"        # 60 minutes (3600 seconds)
```

**Usage**:
```python
from bww_store.models import CacheStrategy

# Use in client requests
response = await client.client.make_request(
    endpoint="/products",
    cache_strategy=CacheStrategy.LONG_TERM
)
```

---

### ProductInfo

Data class for product information.

```python
@dataclass(frozen=True)
class ProductInfo:
    # Required fields
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
    
    # Optional fields
    is_best_seller: bool = False
    is_new_arrival: bool = False
    is_free_delivery: bool = False
    is_refundable: bool = False
    colors: List[str] = field(default_factory=list)
    sizes: List[str] = field(default_factory=list)
    material: Optional[str] = None
    description: Optional[str] = None
```

**Example**:
```python
from bww_store.models import ProductInfo

product = ProductInfo(
    id=123,
    name="Summer T-Shirt",
    final_price=299.99,
    original_price=399.99,
    discount=25.0,
    store_name="BWW Store",
    rating=4.5,
    count_rating=100,
    stock_quantity=50,
    main_image="https://...",
    category={"id": 1, "name": "Men's"},
    colors=["Black", "White"],
    sizes=["M", "L", "XL"]
)
```

---

## Constants

**Module**: `bww_store.constants`

### EGYPTIAN_CORRECTIONS

Dictionary mapping Egyptian dialect to Standard Arabic.

```python
EGYPTIAN_CORRECTIONS = {
    "عايز": "أريد",          # I want
    "محتاج": "أحتاج",        # I need
    "كتير": "كثير",         # Many/much
    "جميل": "جميل",         # Beautiful
    "حلو": "جميل",          # Nice
    # ... 50+ more corrections
}
```

**Usage**:
```python
from bww_store.constants import EGYPTIAN_CORRECTIONS

query = "عايز طقم"
normalized = query
for egyptian, standard in EGYPTIAN_CORRECTIONS.items():
    normalized = normalized.replace(egyptian, standard)
# normalized = "أريد طقم"
```

---

### CLOTHING_KEYWORDS_AR

Arabic clothing keywords with categories.

```python
CLOTHING_KEYWORDS_AR = {
    "قميص": "قميص",           # Shirt
    "بنطال": "بنطلون",        # Pants
    "جاكيت": "جاكت",         # Jacket
    "طقم": "طقم",            # Suit/outfit
    "حذاء": "حذاء",          # Shoes
    # ... more keywords
}
```

---

### CLOTHING_KEYWORDS_EN

English clothing keywords with categories.

```python
CLOTHING_KEYWORDS_EN = {
    "suit": "suit",
    "pants": "pants",
    "shirt": "shirt",
    "jacket": "jacket",
    "shoes": "shoes",
    # ... more keywords
}
```

---

### BWW_SEARCH_SUGGESTIONS_AR

Search suggestions for common queries (Arabic).

```python
BWW_SEARCH_SUGGESTIONS_AR = {
    "رجالي": ["طقم رجالي", "قميص رجالي", "بنطال رجالي"],
    "نسائي": ["فستان", "بلوزة", "تنورة"],
    "أطفال": ["طقم أطفال", "ملابس أطفال"],
    # ... more suggestions
}
```

---

### BWW_PRIORITY_ITEMS_AR

Priority search items (Arabic).

```python
BWW_PRIORITY_ITEMS_AR = [
    "طقم رجالي",
    "طقم أطفال",
    "فستان",
    "قميص",
    # ... more items
]
```

---

## Error Handling

### Common Errors

```python
# Network timeout
APIResponse(
    success=False,
    error="Request timeout",
    status_code=408
)

# Product not found
APIResponse(
    success=False,
    error="Product not found",
    status_code=404
)

# Rate limit exceeded
APIResponse(
    success=False,
    error="Rate limit exceeded",
    status_code=429
)

# Circuit breaker open
APIResponse(
    success=False,
    error="Service temporarily unavailable",
    status_code=503
)
```

### Best Practices

```python
# Always check response.success
response = await client.get_product_details(123)
if response.success:
    product = response.data
    # Process product
else:
    logger.error(f"Failed to get product: {response.error}")
    # Fallback logic
```

---

## Type Hints Reference

```python
from typing import List, Dict, Optional, Any

# Function signatures
async def search(query: str) -> List[Dict[str, Any]]: ...
async def get_product(product_id: int) -> APIResponse: ...
def format_price(price: float) -> str: ...
def filter_products(products: List[Dict], category: Optional[str] = None) -> List[Dict]: ...
```

---

## Version History

**v1.0.0** (November 13, 2025)
- Initial production release
- 12 modules with full functionality
- Complete test coverage
- Full documentation

---

**Last Updated**: November 13, 2025  
**API Version**: 1.0.0  
**Status**: ✅ Production Ready
