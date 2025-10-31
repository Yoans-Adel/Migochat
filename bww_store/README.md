# BWW Store API Client

Python client for BWW Store API with smart caching and Egyptian dialect search.

## What Is This?

A **read-only API client** that connects to BWW Store's API at `api-v1.bww-store.com` and adds:
- 🧠 Smart search with Egyptian dialect support
- 💾 Intelligent caching (LRU, TTL)
- 🔍 Fuzzy matching for typos
- 📊 Product comparison
- 🎴 Messenger card generation
- 🔧 Enterprise reliability (retries, circuit breaker, rate limiting)

## Installation

```bash
pip install aiohttp pytz rapidfuzz
```

Then copy the `bww_store/` folder to your project.

## Quick Start

```python
import asyncio
from bww_store import BWWStoreAPIService

async def main():
    # Initialize client
    client = BWWStoreAPIService(language="ar")
    
    # Smart search (understands Egyptian dialect)
    results = await client.search_and_format_products("عايز طقم صيفي رجالي", limit=3)
    for result in results:
        print(result)
        print("---")

asyncio.run(main())
```

## Features

### 1. Smart Search
```python
# Understands Egyptian dialect
results = await client.search_and_format_products("عايز طقم صيفي", limit=3)

# Handles typos
results = await client.search_and_format_products("طقم صيفى", limit=3)

# Extracts keywords
results = await client.search_and_format_products("محتاج بنطال رجالي أسود", limit=3)
```

### 2. Product Cards
```python
# Get product
product = await client.get_product_details(53)

# Generate Messenger card
if product.success:
    card = await client.generate_product_card(product.data, language="ar")
    print(card["card_content"])
    # Includes: name, price, rating, stock, link
    # Link format: https://bww-store.com/ar/product-details/slug/id
```

### 3. Product Comparison
```python
# Compare 2-4 products
comparison = await client.compare_products([53, 50, 48], language="ar")
print(comparison)
# Shows: side-by-side prices, ratings, best deal
```

### 4. Filtering
```python
# By category
products = await client.filter_products(category="أطفال")

# By price (local filtering)
products = await client.get_products_by_price_range(100, 500)

# By text
products = await client.search_products_by_text("طقم")
```

## Configuration

```python
client = BWWStoreAPIService(language="ar")

# Cache settings
client.client._max_cache_size = 300  # Default: 200
client.client._max_requests_per_minute = 100  # Default: 60

# Language
client_ar = BWWStoreAPIService(language="ar")  # Arabic
client_en = BWWStoreAPIService(language="en")  # English
```

## Service Status

```python
status = client.get_service_status()
print(f"Cache: {status['cache']['size']}/{status['cache']['max_size']}")
print(f"Rate: {status['rate_limit']['current_requests']}/60")
```

## Important Notes

### This is a Read-Only Client
- ✅ Can: Search, get products, format data
- ❌ Cannot: Update inventory, modify prices, create products

### API Limitations
- Color filtering doesn't work at API level (we filter locally)
- Price filtering doesn't work at API level (we filter locally)
- Search is exact-match only (we add fuzzy matching)

### What We Add Client-Side
- Egyptian dialect understanding
- Fuzzy search for typos
- Smart caching (LRU)
- Local filtering (color, price)
- Messenger card formatting
- Product comparison

## Project Structure

```
bww_store/
├── api_client.py          # Main interface
├── client.py              # HTTP client + cache
├── search.py              # Smart search engine
├── product_ops.py         # Product operations
├── card_generator.py      # Card generation
├── comparison_tool.py     # Product comparison
├── product_formatter.py   # Messenger formatting
├── constants.py           # Static data
├── models.py              # Data models
├── base.py                # Base classes
├── utils.py               # Utilities
└── __init__.py           # Package exports
```

## Dependencies

```
aiohttp>=3.8.0          # Async HTTP
pytz>=2023.0            # Timezone (for API auth)
rapidfuzz>=3.0.0        # Fuzzy matching
```

## Documentation

- 📖 [Production Guide](docs/PRODUCTION.md) - Deployment and usage
- 🛠️ [Development Guide](docs/DEVELOPMENT.md) - Architecture and development

## License

MIT License - see [LICENSE](LICENSE)

## Version

**v1.0.0** (October 26, 2025)

- Modular architecture (12 modules)
- Smart search with Egyptian dialect
- Enterprise reliability features
- Multi-language support
- Comprehensive testing