# Changelog

All notable changes to BWW Store API Client will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-26

### Added
- **Modular Architecture**: 12 specialized modules
  - `api_client.py`: Main interface
  - `client.py`: HTTP client with caching
  - `search.py`: Search engine
  - `product_ops.py`: Product operations
  - `card_generator.py`: Card generation with proper BWW links
  - `comparison_tool.py`: Product comparison
  - `product_formatter.py`: Messenger formatting
  - `constants.py`: Egyptian dialect corrections and keywords
  - `models.py`: Data models
  - `base.py`: Base classes and decorators
  - `utils.py`: Helper utilities
  - `__init__.py`: Package exports

- **Core Features**:
  - LRU caching with TTL (3min, 15min, 60min)
  - Rate limiting (60 requests/min)
  - Circuit breaker (5 failures threshold)
  - Automatic retry (3 attempts)
  - Async/await for better performance

- **Smart Search**:
  - Egyptian dialect support (94 corrections)
  - Fuzzy matching with rapidfuzz
  - Keyword extraction (25 categories)
  - Search suggestions
  - Multiple search strategies

- **Product Features**:
  - Generate Messenger cards with BWW Store links
  - Compare products side-by-side
  - Multi-language (Arabic/English)
  - Local filtering for color and price

- **Testing**:
  - Comprehensive test suite
  - Real API integration tests
  - Card generator validation
  - Comparison testing

### Technical Details
- Python 3.8+ async/await
- Type hints throughout
- Comprehensive docstrings
- Error handling and logging

### Current Limitations (BWW Store API)
- **Read-Only**: No write operations (API doesn't allow)
- **Color Filtering**: API accepts parameter but doesn't filter (we do it locally)
- **Price Filtering**: API accepts parameter but doesn't filter (we do it locally)
- **Exact Match Only**: API search is exact (we add fuzzy matching)

### Future Improvements
- Better caching strategies
- Enhanced search relevance scoring
- Optimized memory usage
- More comprehensive error messages
