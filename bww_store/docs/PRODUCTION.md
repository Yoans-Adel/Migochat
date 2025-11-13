# BWW Store Package - Production Guide

> **Complete Production Deployment and Usage Guide for BWW Store API Client**

## 📋 Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Production Usage](#production-usage)
5. [Integration with Migochat](#integration-with-migochat)
6. [Performance Optimization](#performance-optimization)
7. [Monitoring & Logging](#monitoring--logging)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

BWW Store Package is a production-ready API client for the BWW Store e-commerce platform (`api-v1.bww-store.com`). It provides:

- ✅ **Smart Search**: Egyptian dialect support + fuzzy matching
- ✅ **Intelligent Caching**: LRU cache with TTL (200 items, 5-60 min)
- ✅ **Rate Limiting**: 60 requests/minute max
- ✅ **Circuit Breaker**: Auto-recovery from API failures
- ✅ **Retry Logic**: Exponential backoff (3 retries max)
- ✅ **Multi-language**: Arabic (`ar`) and English (`en`)

### Architecture

```
BWWStoreAPIService (Main Interface)
├── BWWStoreClient (HTTP + Cache + Circuit Breaker)
├── SearchEngine (Smart Search + Egyptian Dialect)
├── ProductOperations (Filtering + Price Range)
├── ProductFormatter (Messenger Cards)
├── CardGenerator (Card Templates)
└── ComparisonTool (Product Comparison)
```

---

## Installation

### 1. Dependencies

```bash
pip install aiohttp>=3.8.0 pytz>=2023.0 rapidfuzz>=3.0.0
```

### 2. Package Location

The package is already integrated at:
```
f:\working - yoans\Migochat\bww_store\
```

### 3. Verify Installation

```python
from bww_store import BWWStoreAPIService
print(BWWStoreAPIService.__module__)  # Should print: bww_store.api_client
```

---

## Configuration

### Basic Configuration

```python
from bww_store import BWWStoreAPIService

# Arabic (default)
client_ar = BWWStoreAPIService(language="ar")

# English
client_en = BWWStoreAPIService(language="en")
```

### Advanced Configuration

```python
client = BWWStoreAPIService(language="ar")

# Adjust cache size (default: 200)
client.client._max_cache_size = 300

# Adjust rate limit (default: 60/min)
client.client._max_requests_per_minute = 100

# Adjust circuit breaker threshold (default: 5 failures)
client.client._circuit_breaker_threshold = 10

# Adjust retry attempts (default: 3)
client.client._max_retries = 5
```

### Cache TTL Settings

```python
from bww_store.models import CacheStrategy

# Cache strategies with TTL:
# - NO_CACHE: 0 seconds (no cache)
# - SHORT_TERM: 5 minutes (real-time data)
# - MEDIUM_TERM: 15 minutes (semi-static data)
# - LONG_TERM: 60 minutes (static data)

# Search results use SHORT_TERM (5 min)
# Product details use MEDIUM_TERM (15 min)
# Categories use LONG_TERM (60 min)
```

---

## Production Usage

### 1. Smart Search

```python
import asyncio
from bww_store import BWWStoreAPIService

async def search_products():
    client = BWWStoreAPIService(language="ar")
    
    # Smart search (understands Egyptian dialect)
    results = await client.search_and_format_products(
        query="عايز طقم صيفي رجالي",  # "I want summer outfit men's"
        limit=5
    )
    
    for product in results:
        print(f"📦 {product['name']}")
        print(f"💰 {product['price']}")
        print(f"⭐ {product['rating']}")
        print(f"🔗 {product['link']}")
        print("---")

asyncio.run(search_products())
```

### 2. Get Product Details

```python
async def get_product():
    client = BWWStoreAPIService(language="ar")
    
    # Get single product by ID
    response = await client.get_product_details(product_id=53)
    
    if response.success:
        product = response.data
        print(f"Product: {product['name']}")
        print(f"Price: {product['final_price']} EGP")
        print(f"Stock: {product['stock_quantity']} units")
        print(f"Rating: {product['rating']} ({product['count_rating']} reviews)")
    else:
        print(f"Error: {response.error}")
```

### 3. Generate Messenger Card

```python
async def create_product_card():
    client = BWWStoreAPIService(language="ar")
    
    # Get product
    response = await client.get_product_details(53)
    
    if response.success:
        # Generate card for Messenger
        card = await client.generate_product_card(
            product=response.data,
            language="ar"
        )
        
        # Card structure:
        print(card["card_content"])
        # {
        #     "title": "Product Name",
        #     "subtitle": "Price • Rating • Stock",
        #     "image_url": "https://...",
        #     "buttons": [
        #         {"type": "web_url", "url": "...", "title": "🛒 عرض المنتج"}
        #     ]
        # }
```

### 4. Product Comparison

```python
async def compare_products():
    client = BWWStoreAPIService(language="ar")
    
    # Compare 2-4 products
    comparison = await client.compare_products(
        product_ids=[53, 50, 48],
        language="ar"
    )
    
    print(comparison["title"])  # "مقارنة المنتجات"
    print(comparison["summary"])  # "أفضل سعر: Product Name (299 EGP)"
    
    for item in comparison["items"]:
        print(f"• {item['name']}: {item['price']} EGP")
```

### 5. Filtering Products

```python
async def filter_products():
    client = BWWStoreAPIService(language="ar")
    
    # Filter by category
    men_products = await client.filter_products(category="رجالي")
    
    # Filter by price range (local filtering)
    budget_products = await client.get_products_by_price_range(
        min_price=100,
        max_price=500
    )
    
    # Filter by color (local filtering)
    black_products = await client.get_products_by_color(color="أسود")
    
    # Text search
    shirts = await client.search_products_by_text(query="قميص")
```

---

## Integration with Migochat

### 1. Message Handler Integration

The package is already integrated in:
```python
# app/services/messaging/message_handler.py

from bww_store import BWWStoreAPIService

class MessageHandler:
    def __init__(self):
        self.bww_client = BWWStoreAPIService(language="ar")
    
    async def handle_product_search(self, query: str, user_id: str):
        # Search products
        products = await self.bww_client.search_and_format_products(query, limit=5)
        
        # Track interest (Product Recommender)
        await self.product_recommender.track_product_interest(
            user_id=user_id,
            search_query=query,
            viewed_products=products
        )
        
        return products
```

### 2. Server API Integration

```python
# Server/routes/api.py

from bww_store import BWWStoreAPIService

# Initialize client
bww_client = BWWStoreAPIService(language="ar")

@app.get("/api/products/search")
async def search_products(query: str, limit: int = 10):
    results = await bww_client.search_and_format_products(query, limit)
    return {"products": results}

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    response = await bww_client.get_product_details(product_id)
    return response.data if response.success else {"error": response.error}
```

### 3. Product Recommender Integration

```python
# app/services/ai/product_recommender.py

async def suggest_products(self, user_id: str):
    # Get user preferences
    prefs = self.customer_preferences.get(user_id)
    
    if prefs and prefs["searches"]:
        recent_query = prefs["searches"][-1]["query"]
        
        # Search BWW Store
        products = await self.bww_client.search_and_format_products(
            query=recent_query,
            limit=3
        )
        
        return products
```

---

## Performance Optimization

### 1. Caching Strategy

```python
# Cache is automatically managed:
# - LRU eviction when cache is full (200 items)
# - TTL-based expiration (5-60 min)
# - No manual cache management needed

# Check cache status
status = client.get_service_status()
print(f"Cache size: {status['cache']['size']}/{status['cache']['max_size']}")
print(f"Cache hit rate: {status['cache']['hits']}/{status['cache']['total_requests']}")
```

### 2. Rate Limiting

```python
# Automatic rate limiting (60 req/min)
# - Requests are queued if limit exceeded
# - No errors thrown
# - Transparent to caller

# Monitor rate limit
status = client.get_service_status()
print(f"Requests this minute: {status['rate_limit']['current_requests']}/60")
```

### 3. Batch Operations

```python
# Avoid sequential calls - use batch operations
# ❌ BAD: Sequential calls
for product_id in [1, 2, 3]:
    await client.get_product_details(product_id)

# ✅ GOOD: Parallel calls (respects rate limit)
import asyncio
tasks = [client.get_product_details(id) for id in [1, 2, 3]]
results = await asyncio.gather(*tasks)
```

---

## Monitoring & Logging

### 1. Service Status

```python
status = client.get_service_status()

print(status)
# {
#     "service_name": "BWW Store API Client",
#     "version": "1.0.0",
#     "language": "ar",
#     "base_url": "https://api-v1.bww-store.com",
#     "cache": {
#         "size": 45,
#         "max_size": 200,
#         "hits": 120,
#         "misses": 30
#     },
#     "rate_limit": {
#         "max_requests_per_minute": 60,
#         "current_requests": 12
#     },
#     "circuit_breaker": {
#         "state": "closed",  # closed/open/half_open
#         "failure_count": 0
#     }
# }
```

### 2. Logging

```python
import logging

# BWW Store uses Python logging
logger = logging.getLogger("bww_store")
logger.setLevel(logging.INFO)

# Logs include:
# - API requests/responses
# - Cache hits/misses
# - Rate limit events
# - Circuit breaker state changes
# - Error details
```

---

## Error Handling

### 1. Response Structure

```python
from bww_store.models import APIResponse

response: APIResponse = await client.get_product_details(123)

if response.success:
    # Success path
    product = response.data
    print(f"Product: {product['name']}")
else:
    # Error path
    print(f"Error: {response.error}")
    print(f"Status: {response.status_code}")
```

### 2. Common Errors

```python
# Network timeout
response.error = "Request timeout"
response.status_code = 408

# API error
response.error = "Product not found"
response.status_code = 404

# Rate limit exceeded
response.error = "Rate limit exceeded"
response.status_code = 429

# Circuit breaker open
response.error = "Service temporarily unavailable"
response.status_code = 503
```

### 3. Retry Logic

```python
# Automatic retry with exponential backoff:
# - Attempt 1: Immediate
# - Attempt 2: 1 second delay
# - Attempt 3: 2 seconds delay
# - Attempt 4: 4 seconds delay (max 3 retries)

# Retries happen automatically on:
# - Network timeouts
# - 5xx server errors
# - Connection errors
```

---

## Best Practices

### ✅ DO:

1. **Reuse client instances** - Don't create new clients for each request
   ```python
   # ✅ GOOD: Singleton client
   client = BWWStoreAPIService(language="ar")
   
   # Reuse for all requests
   products1 = await client.search_and_format_products("query1")
   products2 = await client.search_and_format_products("query2")
   ```

2. **Handle errors gracefully**
   ```python
   response = await client.get_product_details(123)
   if response.success:
       # Success logic
   else:
       # Fallback logic
       logger.error(f"Product fetch failed: {response.error}")
   ```

3. **Use appropriate cache strategies**
   ```python
   # Real-time data: SHORT_TERM (5 min)
   # Semi-static: MEDIUM_TERM (15 min)
   # Static: LONG_TERM (60 min)
   ```

4. **Monitor service status**
   ```python
   status = client.get_service_status()
   if status['circuit_breaker']['state'] == 'open':
       logger.warning("BWW Store circuit breaker is open!")
   ```

### ❌ DON'T:

1. **Don't create clients in loops**
   ```python
   # ❌ BAD
   for query in queries:
       client = BWWStoreAPIService()  # DON'T!
       await client.search_and_format_products(query)
   ```

2. **Don't ignore errors**
   ```python
   # ❌ BAD
   response = await client.get_product_details(123)
   product = response.data  # Could be None!
   ```

3. **Don't bypass rate limits**
   ```python
   # ❌ BAD
   client._max_requests_per_minute = 1000  # Too high!
   ```

---

## Troubleshooting

### Issue 1: No Results from Search

**Symptom**: `search_and_format_products()` returns empty list

**Solutions**:
1. Check API connectivity
   ```python
   status = client.get_service_status()
   print(status['base_url'])  # Should be: https://api-v1.bww-store.com
   ```

2. Try simpler query
   ```python
   # Instead of complex query
   results = await client.search_and_format_products("عايز طقم صيفي رجالي كامل")
   
   # Try simple
   results = await client.search_and_format_products("طقم رجالي")
   ```

3. Check circuit breaker state
   ```python
   status = client.get_service_status()
   if status['circuit_breaker']['state'] == 'open':
       # Wait 60 seconds for auto-recovery
       await asyncio.sleep(60)
   ```

### Issue 2: Rate Limit Errors

**Symptom**: Requests are slow or failing

**Solutions**:
1. Check rate limit status
   ```python
   status = client.get_service_status()
   print(f"Requests: {status['rate_limit']['current_requests']}/60")
   ```

2. Reduce request frequency
   ```python
   # Add delays between requests
   await asyncio.sleep(1)
   ```

3. Increase cache size
   ```python
   client.client._max_cache_size = 500  # More cache = fewer API calls
   ```

### Issue 3: Cache Not Working

**Symptom**: Every request hits the API

**Solutions**:
1. Check cache status
   ```python
   status = client.get_service_status()
   print(f"Cache size: {status['cache']['size']}")
   print(f"Cache hits: {status['cache']['hits']}")
   ```

2. Verify cache strategy
   ```python
   # Cache is automatic - no manual configuration needed
   # Products are cached for 5-60 minutes based on data type
   ```

---

## Production Checklist

✅ **Before Deployment:**
- [ ] Dependencies installed (`aiohttp`, `pytz`, `rapidfuzz`)
- [ ] Package imported successfully
- [ ] Client instance created
- [ ] Test search returns results
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Monitoring setup

✅ **After Deployment:**
- [ ] Monitor cache hit rate (target: >70%)
- [ ] Monitor rate limit usage (target: <60/min)
- [ ] Check circuit breaker state (should be "closed")
- [ ] Verify response times (<500ms avg)
- [ ] Review error logs
- [ ] Test fallback scenarios

---

## Support & Resources

- **Package Location**: `f:\working - yoans\Migochat\bww_store\`
- **Tests**: `f:\working - yoans\Migochat\tests\test_bww_store.py`
- **Documentation**: `f:\working - yoans\Migochat\bww_store\docs\`
- **Main API**: https://api-v1.bww-store.com
- **Store Website**: https://bww-store.com

---

**Version**: 1.0.0  
**Last Updated**: November 13, 2025  
**Status**: ✅ Production Ready
