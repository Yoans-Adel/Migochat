"""
BWW Store API Client Package

A comprehensive Python client for the BWW Store API with enterprise-grade
reliability features, intelligent caching, and multi-language support.

Main Features:
    - Intelligent search with Egyptian dialect support
    - Product comparison and card generation
    - Enterprise-grade caching and rate limiting
    - Circuit breaker pattern for fault tolerance
    - Automatic retry with exponential backoff

Usage:
    >>> from bww_store import BWWStoreAPIService
    >>> client = BWWStoreAPIService(language="ar")
    >>> result = client.search_and_format_products("طقم صيفي")
"""

from .api_client import BWWStoreAPIService
from .constants import (
    EGYPTIAN_CORRECTIONS,
    CLOTHING_KEYWORDS_AR,
    CLOTHING_KEYWORDS_EN,
    BWW_SEARCH_SUGGESTIONS_AR,
    BWW_SEARCH_SUGGESTIONS_EN,
    BWW_PRIORITY_ITEMS_AR,
    BWW_PRIORITY_ITEMS_EN
)
from .models import APIResponse, CacheStrategy, ProductInfo

__version__ = "1.0.0"
__author__ = "BWW Store AI Assistant"
__description__ = "BWW Store API Client with advanced features"

__all__ = [
    "BWWStoreAPIService",
    "APIResponse",
    "CacheStrategy",
    "ProductInfo",
    "EGYPTIAN_CORRECTIONS",
    "CLOTHING_KEYWORDS_AR",
    "CLOTHING_KEYWORDS_EN",
    "BWW_SEARCH_SUGGESTIONS_AR",
    "BWW_SEARCH_SUGGESTIONS_EN",
    "BWW_PRIORITY_ITEMS_AR",
    "BWW_PRIORITY_ITEMS_EN",
]
