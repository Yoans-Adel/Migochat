# BWW Store Package - Quick Start Guide

> **Get started with BWW Store API Client in 5 minutes**

## 🚀 Installation

### 1. Install Dependencies

```bash
pip install aiohttp>=3.8.0 pytz>=2023.0 rapidfuzz>=3.0.0
```

### 2. Verify Package

```python
from bww_store import BWWStoreAPIService
print("✅ BWW Store package is ready!")
```

---

## 📦 Basic Usage

### Example 1: Simple Search

```python
import asyncio
from bww_store import BWWStoreAPIService

async def search_example():
    # Initialize client (Arabic by default)
    client = BWWStoreAPIService(language="ar")
    
    # Search for products
    results = await client.search_and_format_products(
        query="طقم رجالي",  # Men's suit
        limit=3
    )
    
    # Display results
    for product in results:
        print(f"📦 {product['name']}")
        print(f"💰 {product['price']}")
        print(f"⭐ {product['rating']}")
        print(f"🔗 {product['link']}")
        print("---")

# Run
asyncio.run(search_example())
```

**Output**:
```
📦 طقم رجالي صيفي - أسود
💰 299.99 EGP
⭐ ⭐⭐⭐⭐⭐ (4.5)
🔗 https://bww-store.com/ar/product-details/summer-suit/123
---
```

---

### Example 2: Egyptian Dialect Search

```python
async def egyptian_search():
    client = BWWStoreAPIService(language="ar")
    
    # Egyptian dialect query - automatically normalized!
    results = await client.search_and_format_products(
        query="عايز طقم صيفي حلو",  # "I want a nice summer outfit"
        limit=3
    )
    
    print(f"Found {len(results)} products")
    for product in results:
        print(f"• {product['name']} - {product['price']}")

asyncio.run(egyptian_search())
```

**How it works**:
- `"عايز"` → `"أريد"` (I want)
- `"حلو"` → `"جميل"` (nice/beautiful)
- Search uses normalized Standard Arabic

---

### Example 3: Get Product Details

```python
async def product_details():
    client = BWWStoreAPIService(language="ar")
    
    # Get specific product by ID
    response = await client.get_product_details(product_id=53)
    
    if response.success:
        product = response.data
        print(f"Product: {product['name']}")
        print(f"Price: {product['final_price']} EGP")
        print(f"Original: {product['original_price']} EGP")
        print(f"Discount: {product['discount']}%")
        print(f"Rating: {product['rating']} ({product['count_rating']} reviews)")
        print(f"Stock: {product['stock_quantity']} units")
        
        # Check cache status
        if response.cached:
            print("✅ Served from cache!")
        else:
            print(f"⏱️ API response time: {response.response_time_ms}ms")
    else:
        print(f"❌ Error: {response.error}")

asyncio.run(product_details())
```

---

### Example 4: Filter Products

```python
async def filter_example():
    client = BWWStoreAPIService(language="ar")
    
    # Multiple filters
    filtered = await client.filter_products(
        category="رجالي",      # Men's category
        min_price=200,         # Minimum 200 EGP
        max_price=600,         # Maximum 600 EGP
        color="أسود"           # Black color
    )
    
    print(f"Found {len(filtered)} matching products:")
    for product in filtered[:5]:  # Show first 5
        print(f"• {product['name']} - {product['final_price']} EGP")

asyncio.run(filter_example())
```

---

### Example 5: Generate Messenger Card

```python
async def messenger_card():
    client = BWWStoreAPIService(language="ar")
    
    # Get product
    response = await client.get_product_details(53)
    
    if response.success:
        # Generate Messenger card
        card = await client.generate_product_card(
            product=response.data,
            language="ar"
        )
        
        # Card structure
        content = card["card_content"]
        print(f"Title: {content['title']}")
        print(f"Subtitle: {content['subtitle']}")
        print(f"Image: {content['image_url']}")
        print(f"Button: {content['buttons'][0]['title']}")
        print(f"URL: {content['buttons'][0]['url']}")

asyncio.run(messenger_card())
```

**Output**:
```
Title: طقم رجالي صيفي - أسود
Subtitle: 299 EGP • ⭐ 4.5 • متوفر
Image: https://api-v1.bww-store.com/storage/products/image.jpg
Button: 🛒 عرض المنتج
URL: https://bww-store.com/ar/product-details/summer-suit/53
```

---

### Example 6: Compare Products

```python
async def compare_example():
    client = BWWStoreAPIService(language="ar")
    
    # Compare 3 products
    comparison = await client.compare_products(
        product_ids=[53, 50, 48],
        language="ar"
    )
    
    print(f"📊 {comparison['title']}")
    print(f"✨ {comparison['summary']}")
    print("\nProducts:")
    for item in comparison['items']:
        print(f"• {item['name']}")
        print(f"  💰 {item['price']} EGP | ⭐ {item['rating']}")

asyncio.run(compare_example())
```

**Output**:
```
📊 مقارنة المنتجات
✨ أفضل سعر: طقم صيفي رجالي (299 EGP)

Products:
• طقم صيفي رجالي
  💰 299 EGP | ⭐ 4.5
• طقم شتوي رجالي
  💰 399 EGP | ⭐ 4.2
• طقم كلاسيك رجالي
  💰 499 EGP | ⭐ 4.8
```

---

## 🎯 Common Use Cases

### Use Case 1: Search + Send to User

```python
async def search_and_send(user_message: str, send_function):
    """Search for products and send to user"""
    client = BWWStoreAPIService(language="ar")
    
    # Search
    products = await client.search_and_format_products(user_message, limit=5)
    
    if products:
        # Send results
        for product in products[:3]:  # Top 3
            card = await client.generate_product_card(product, language="ar")
            await send_function(card)
    else:
        await send_function("عذراً، لم أجد منتجات مطابقة 😔")
```

---

### Use Case 2: Budget Shopping

```python
async def budget_shopping(max_budget: float):
    """Find products within budget"""
    client = BWWStoreAPIService(language="ar")
    
    # Get affordable products
    products = await client.get_products_by_price_range(
        min_price=0,
        max_price=max_budget
    )
    
    # Sort by rating
    products.sort(key=lambda p: p.get('rating', 0), reverse=True)
    
    print(f"🛍️ Best products under {max_budget} EGP:")
    for product in products[:5]:
        print(f"• {product['name']} - {product['final_price']} EGP (⭐ {product['rating']})")

asyncio.run(budget_shopping(500))
```

---

### Use Case 3: Category Browser

```python
async def browse_category(category: str):
    """Browse products in category"""
    client = BWWStoreAPIService(language="ar")
    
    # Get category products
    products = await client.get_products_by_category(category)
    
    print(f"📂 {category} ({len(products)} products)")
    
    # Group by price range
    budget = [p for p in products if p['final_price'] < 300]
    mid = [p for p in products if 300 <= p['final_price'] <= 600]
    premium = [p for p in products if p['final_price'] > 600]
    
    print(f"💰 Budget (<300): {len(budget)} items")
    print(f"💰 Mid-range (300-600): {len(mid)} items")
    print(f"💰 Premium (>600): {len(premium)} items")

asyncio.run(browse_category("رجالي"))
```

---

### Use Case 4: Smart Recommendations

```python
async def recommend_similar(product_id: int):
    """Recommend similar products"""
    client = BWWStoreAPIService(language="ar")
    
    # Get original product
    response = await client.get_product_details(product_id)
    
    if response.success:
        original = response.data
        category = original['category'].get('name', '')
        price = original['final_price']
        
        # Find similar in same category
        all_products = await client.get_products_by_category(category)
        
        # Filter by similar price (±30%)
        min_price = price * 0.7
        max_price = price * 1.3
        similar = [
            p for p in all_products
            if min_price <= p['final_price'] <= max_price
            and p['id'] != product_id
        ]
        
        print(f"Similar to: {original['name']}")
        print(f"Found {len(similar)} similar products:")
        for product in similar[:3]:
            print(f"• {product['name']} - {product['final_price']} EGP")

asyncio.run(recommend_similar(53))
```

---

## 🔧 Configuration

### Change Language

```python
# Arabic (default)
client_ar = BWWStoreAPIService(language="ar")

# English
client_en = BWWStoreAPIService(language="en")
```

---

### Adjust Cache Size

```python
client = BWWStoreAPIService(language="ar")

# Increase cache (more memory, fewer API calls)
client.client._max_cache_size = 500  # Default: 200
```

---

### Monitor Status

```python
client = BWWStoreAPIService(language="ar")

# Get status
status = client.get_service_status()

print(f"Cache: {status['cache']['size']}/{status['cache']['max_size']}")
print(f"Hit rate: {status['cache']['hits']}/{status['cache']['total_requests']}")
print(f"Rate limit: {status['rate_limit']['current_requests']}/60")
print(f"Circuit breaker: {status['circuit_breaker']['state']}")
```

---

## ✅ Best Practices

### DO ✅

```python
# ✅ Reuse client instance
client = BWWStoreAPIService(language="ar")
results1 = await client.search_and_format_products("query1")
results2 = await client.search_and_format_products("query2")

# ✅ Check response.success
response = await client.get_product_details(123)
if response.success:
    product = response.data

# ✅ Handle errors gracefully
try:
    results = await client.search_and_format_products(query)
except Exception as e:
    logger.error(f"Search failed: {e}")
    results = []
```

---

### DON'T ❌

```python
# ❌ Don't create new clients in loops
for query in queries:
    client = BWWStoreAPIService()  # BAD!
    await client.search_and_format_products(query)

# ❌ Don't ignore response.success
response = await client.get_product_details(123)
product = response.data  # Could be None!

# ❌ Don't bypass rate limits
client._max_requests_per_minute = 1000  # BAD!
```

---

## 📚 Next Steps

- **Full Documentation**: [docs/PRODUCTION.md](PRODUCTION.md)
- **API Reference**: [docs/API_REFERENCE.md](API_REFERENCE.md)
- **Development Guide**: [docs/DEVELOPMENT.md](DEVELOPMENT.md)
- **Test Suite**: `tests/test_bww_store.py`

---

## 🆘 Troubleshooting

### No results from search?

```python
# Try simpler query
results = await client.search_and_format_products("طقم")  # Simple

# Check service status
status = client.get_service_status()
print(status['circuit_breaker']['state'])  # Should be "closed"
```

---

### Slow responses?

```python
# Check cache hit rate
status = client.get_service_status()
hit_rate = status['cache']['hits'] / status['cache']['total_requests']
print(f"Cache hit rate: {hit_rate:.2%}")  # Target: >70%
```

---

### Rate limit errors?

```python
# Check rate limit status
status = client.get_service_status()
print(f"Requests: {status['rate_limit']['current_requests']}/60")

# Add delays if needed
await asyncio.sleep(1)
```

---

**Version**: 1.0.0  
**Last Updated**: November 13, 2025  
**Ready to use!** 🚀
