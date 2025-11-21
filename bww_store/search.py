"""
BWW Store Search Engine

This module contains intelligent search functionality including keyword extraction,
fuzzy matching, and smart product ranking for the BWW Store API.
"""

import logging
from typing import Any, Dict, List, Set, Tuple, cast

from rapidfuzz import fuzz, process

from .client import BWWStoreAPIClient
from .constants import (
    EGYPTIAN_CORRECTIONS,
    CLOTHING_KEYWORDS_AR,
    CLOTHING_KEYWORDS_EN,
    BWW_SEARCH_SUGGESTIONS_AR,
    BWW_SEARCH_SUGGESTIONS_EN,
    BWW_PRIORITY_ITEMS_AR,
    BWW_PRIORITY_ITEMS_EN
)
from .intelligent_search import (
    IntelligentSearchEngine,
    SearchIntent,
    Season
)
from .models import APIResponse, CacheStrategy
from .product_formatter import format_product_for_messenger
from .product_filters import (
    score_price_match, score_occasion_match, score_season_match,
    score_quality_match, score_outfit_match, should_include_product
)
from .search_strategies import extract_products_from_results, format_no_results_message

logger = logging.getLogger(__name__)


def fuzzy_similarity(text1: str, text2: str) -> float:
    """Calculate fuzzy similarity between two text strings.

    Uses Levenshtein distance algorithm to compute similarity ratio,
    normalized to a 0.0-1.0 scale where 1.0 means identical strings.

    Args:
        text1: First text string to compare
        text2: Second text string to compare

    Returns:
        Similarity score between 0.0 (no similarity) and 1.0 (identical)
    """
    return fuzz.ratio(text1.lower(), text2.lower()) / 100.0


def spelling_suggestions(search_term: str, dictionary: List[str], limit: int = 3) -> List[str]:
    """Generate spelling correction suggestions for a search term.

    Args:
        search_term: The potentially misspelled search term
        dictionary: List of valid terms to match against
        limit: Maximum number of suggestions to return (default: 3)

    Returns:
        List of suggested corrections, ordered by similarity score
    """
    results = process.extract(search_term, dictionary, limit=limit, score_cutoff=50)
    return [word for word, _score, _index in results]


def calculate_product_score(product: Dict[str, Any], search_term: str) -> float:
    """Calculate relevance score for a product based on search term matching.

    Args:
        product: Product data dictionary with name and metadata
        search_term: User's search query

    Returns:
        Relevance score between 0.0 (no match) and 1.0+ (perfect match + bonuses)
    """
    name = product.get("name", "").lower()
    search = search_term.lower()

    # Exact substring match gets perfect score
    if search in name:
        base_score = 1.0
    else:
        # Fuzzy similarity for approximate matches
        base_score = fuzzy_similarity(name, search)

    # Position-based bonuses
    if name.startswith(search):
        base_score += 0.3  # Prefix matches are very relevant

    # Business rule: boost best sellers slightly
    if product.get("is_best_seller"):
        base_score += 0.1

    return min(base_score, 1.0)  # Cap at 1.0 for consistency


class BWWStoreSearchEngine:
    """Intelligent search engine for BWW Store products."""

    def __init__(self, client: BWWStoreAPIClient):
        """Initialize search engine with API client.

        Args:
            client: BWWStoreAPIClient instance
        """
        self.client = client
        # Initialize intelligent search engine for advanced intent detection
        self.intelligent_engine = IntelligentSearchEngine(CLOTHING_KEYWORDS_AR)

    def _extract_clothing_keywords(self, sentence: str, language: str = "ar") -> List[str]:
        """Extract clothing-related keywords from Arabic/English sentences with spelling correction.

        Args:
            sentence: Input sentence to analyze
            language: Language code ("ar" or "en")

        Returns:
            List of extracted clothing keywords
        """
        # Normalize text
        text = sentence.lower().strip()

        # Apply Egyptian dialect corrections if Arabic
        if language == "ar":
            for wrong, correct in EGYPTIAN_CORRECTIONS.items():
                text = text.replace(wrong, correct)

        # Use appropriate keywords dictionary
        keywords_dict = CLOTHING_KEYWORDS_AR if language == "ar" else CLOTHING_KEYWORDS_EN

        found_keywords: List[str] = []

        # Check each keyword group
        for main_keyword, variations in keywords_dict.items():
            for variation in variations:
                if variation in text:
                    found_keywords.append(main_keyword)
                    break  # Only add the main keyword once per group

        # Remove duplicates and return
        return list(set(found_keywords))

    def _generate_search_suggestions(self, keywords: List[str], language: str = "ar") -> List[str]:
        """Generate alternative search suggestions based on BWW Store's actual product catalog.

        Args:
            keywords: List of keywords to generate suggestions for
            language: Language code ("ar" or "en")

        Returns:
            List of suggested search terms
        """
        # Use appropriate suggestion mappings
        suggestion_map = BWW_SEARCH_SUGGESTIONS_AR if language == "ar" else BWW_SEARCH_SUGGESTIONS_EN
        priority_items = BWW_PRIORITY_ITEMS_AR if language == "ar" else BWW_PRIORITY_ITEMS_EN

        suggestions: List[str] = []
        for keyword in keywords:
            if keyword in suggestion_map:
                suggestions.extend(suggestion_map[keyword])

        # Remove duplicates
        suggestions = list(set(suggestions))

        # Add fallback suggestions if none found
        if not suggestions:
            suggestions = priority_items[:5]

        # Prioritize BWW's actual products
        bww_priority: List[str] = []
        for item in priority_items:
            if item in suggestions:
                bww_priority.append(item)
                suggestions.remove(item)

        return (bww_priority + suggestions)[:6]  # Prioritize BWW products, limit to 6

    async def _search_by_keywords(self, keywords: List[str], language: str) -> APIResponse:
        """Search using extracted keywords.

        Args:
            keywords: List of keywords to search for
            language: Language code

        Returns:
            APIResponse with search results
        """
        if not keywords:
            return APIResponse(success=False, error="No keywords found")

        # Try different combinations of keywords
        search_terms = [
            ' '.join(keywords),  # All keywords
            ' '.join(keywords[:2]),  # First two keywords
            keywords[0],  # Most important keyword
        ]

        for term in search_terms:
            result = await self.client.filter_products(search=term, page_size=25, cache_strategy=CacheStrategy.SHORT_TERM)
            if result.success and result.data.get("data", {}).get("products"):
                return result

        return APIResponse(success=False, error="Keyword search failed")

    async def _search_clean_sentence(self, sentence: str, language: str) -> APIResponse:
        """Search with cleaned sentence (remove stop words and normalize).

        Args:
            sentence: Input sentence to clean and search
            language: Language code

        Returns:
            APIResponse with search results
        """
        # Remove common Arabic stop words and normalize
        if language == "ar":
            stop_words = {
                'أريد', 'أحتاج', 'أبحث عن', 'بحث عن', 'ابحث عن',
                'أنا عايز', 'عايز', 'أنا محتاج', 'محتاج',
                'من فضلك', 'لو سمحت', 'شكراً', 'في', 'على', 'من', 'إلى',
                'مع', 'عن', 'و', 'أو', 'لكن', 'أن', 'ما', 'هو', 'هي', 'هم',
                'أنا', 'نحن', 'أنت', 'أنتم', 'لل', 'في', 'ع'
            }

            # Normalize Arabic text
            clean_text = sentence
            for word in stop_words:
                clean_text = clean_text.replace(f' {word} ', ' ')
            clean_text = clean_text.strip()

        else:
            # English stop words
            stop_words = {
                'i want', 'i need', 'search for', 'find me', 'looking for',
                'please', 'thank you', 'the', 'a', 'an', 'and', 'or', 'but',
                'in', 'on', 'at', 'to', 'for', 'with', 'by', 'from'
            }

            clean_text = sentence.lower()
            for word in stop_words:
                clean_text = clean_text.replace(f' {word} ', ' ')
            clean_text = clean_text.strip()

        if len(clean_text) < 2:
            return APIResponse(success=False, error="Sentence too short after cleaning")

        return await self.client.filter_products(search=clean_text, page_size=20, cache_strategy=CacheStrategy.SHORT_TERM)

    async def _search_by_important_words(self, keywords: List[str]) -> APIResponse:
        """Search by most important keywords only.

        Args:
            keywords: List of keywords

        Returns:
            APIResponse with search results
        """
        if not keywords:
            return APIResponse(success=False, error="No keywords")

        # Priority: type > color > gender > other
        priority_keywords: List[str] = []

        # Clothing types get highest priority
        clothing_types = ['قميص', 'بنطال', 'جاكيت', 'فستان', 'حذاء', 'هودي', 'بدلة', 'shirt', 'pants', 'jacket', 'dress', 'shoes', 'hoodie', 'suit']
        for keyword in keywords:
            if keyword in clothing_types:
                priority_keywords.insert(0, keyword)  # Add to front
            else:
                priority_keywords.append(keyword)

        # Search with priority keywords
        for i in range(min(3, len(priority_keywords))):
            search_term = ' '.join(priority_keywords[:i + 1])
            result = await self.client.filter_products(search=search_term, page_size=20, cache_strategy=CacheStrategy.SHORT_TERM)
            if result.success and result.data.get("data", {}).get("products"):
                return result

        return APIResponse(success=False, error="Priority keyword search failed")

    async def _search_popular_with_keywords(self, keywords: List[str]) -> APIResponse:
        """Get popular products and filter locally with keywords.

        Args:
            keywords: List of keywords to filter by

        Returns:
            APIResponse with filtered products
        """
        # Get popular products
        result = await self.client.filter_products(page_size=60, cache_strategy=CacheStrategy.MEDIUM_TERM)

        if not result.success:
            return result

        products = result.data.get("data", {}).get("products", [])
        if not products:
            return APIResponse(success=False, error="No popular products found")

        # Filter by keywords with enhanced matching
        filtered_products: List[Tuple[Dict[str, Any], float]] = []
        keyword_text = ' '.join(keywords).lower()

        for item in products:
            # Handle both tuple (product, score) and dict formats
            base_score: float = 0
            if isinstance(item, tuple):
                product_data: Tuple[Dict[str, Any], Any] = cast(Tuple[Dict[str, Any], Any], item)
                product: Dict[str, Any] = product_data[0]
                base_score = float(product_data[1])
            else:
                product = cast(Dict[str, Any], item)
                base_score = 0.0

            name: str = str(product.get("name", "")).lower()
            score: float = base_score

            # Direct keyword matches get highest score
            for keyword in keywords:
                if keyword in name:
                    score += 1.0
                else:
                    # Check fuzzy similarity for each keyword
                    similarity = calculate_product_score(product, keyword)
                    if similarity > 0.6:  # Lower threshold for better matching
                        score += similarity * 0.8

            # Overall name similarity with combined keywords
            overall_similarity = calculate_product_score(product, keyword_text)
            score += overall_similarity * 0.5

            # Boost score based on product attributes
            if product.get("is_best_seller"):
                score += 0.2
            if product.get("rating", 0) >= 4.0:
                score += 0.1

            # Include product if score is good enough
            if score >= 0.3:  # Lower threshold to include more results
                filtered_products.append((product, score))

        if filtered_products:
            # Return in API format
            fake_response: Dict[str, Dict[str, List[Tuple[Dict[str, Any], float]]]] = {
                "data": {
                    "products": filtered_products[:20]  # Limit to 20
                }
            }
            return APIResponse(data=fake_response, success=True)

        return APIResponse(success=False, error="No keyword matches in popular products")

    def _filter_products_by_intent(self, products: List[Dict[str, Any]], intent: SearchIntent) -> List[Tuple[Dict[str, Any], float]]:
        """Filter and score products based on detected search intent.

        This is the core intelligence that understands what the user REALLY wants.
        It applies sophisticated filtering for price, occasion, season, and quality.

        ENHANCED with supreme precision and multi-factor validation.

        Args:
            products: List of product dictionaries to filter
            intent: Detected search intent with price, occasion, season, quality preferences

        Returns:
            List of (product, score) tuples, sorted by relevance (only high-quality matches)
        """
        filtered: List[Tuple[Dict[str, Any], float]] = []

        for product in products:
            score = 1.0  # Start with base score
            has_critical_mismatch = False
            match_count = 0

            # 1. Price Range Filtering
            if intent.price_range:
                price_score, price_mismatch = score_price_match(product, intent)
                score += price_score
                if price_mismatch:
                    has_critical_mismatch = True
                else:
                    match_count += 1

            # 2. Occasion Matching
            if intent.occasion:
                occasion_score, occasion_mismatch = score_occasion_match(
                    product, intent, self.intelligent_engine.fuzzy_matcher
                )
                score += occasion_score
                if occasion_mismatch:
                    has_critical_mismatch = True
                else:
                    match_count += 1

            # 3. Season Matching
            if intent.season and intent.season != Season.ALL_SEASON:
                season_score = score_season_match(
                    product, intent, self.intelligent_engine.fuzzy_matcher
                )
                score += season_score
                if season_score > 0:
                    match_count += 1

            # 4. Quality Preference
            if intent.quality_preference:
                quality_score, quality_mismatch = score_quality_match(product, intent)
                score += quality_score
                if quality_mismatch:
                    has_critical_mismatch = True
                else:
                    match_count += 1

            # 5. Complete Outfit Detection
            if intent.wants_complete_outfit:
                outfit_score = score_outfit_match(product, intent)
                score += outfit_score
                if outfit_score > 0:
                    match_count += 1

            # Validation
            if should_include_product(intent, score, match_count, has_critical_mismatch):
                filtered.append((product, score))

        filtered.sort(key=lambda x: x[1], reverse=True)
        return filtered

    async def search_and_format_products(self, search_text: str, *, limit: int = 3, language: str = "ar") -> List[str]:
        """Smart search with AI-powered intent detection and intelligent filtering.

        This method uses advanced natural language understanding to detect what the user
        REALLY wants (price, occasion, season, quality) and filters products accordingly.

        Args:
            search_text: User's search query in natural language
            limit: Maximum number of products to return
            language: Language code ("ar" for Arabic, "en" for English)

        Returns:
            List of formatted product strings with smart Arabic responses
        """
        # === STEP 1: Intelligent Intent Analysis ===
        # Understand what user REALLY wants
        intent = self.intelligent_engine.analyze_query(search_text)

        logger.info(
            f"🧠 Intent detected: price={intent.price_range}, occasion={intent.occasion}, "
            f"season={intent.season}, outfit={intent.wants_complete_outfit}, quality={intent.quality_preference}"
        )

        # Extract keywords from sentence
        keywords = self._extract_clothing_keywords(search_text, language)

        # === STEP 2: Multi-Strategy Search ===
        # Try different search strategies to get candidates
        search_strategies = [
            # Strategy 1: Get popular products (BEST for limited API data)
            lambda: self._search_popular_with_keywords(keywords),

            # Strategy 2: Search with extracted keywords
            lambda: self._search_by_keywords(keywords, language),

            # Strategy 3: Search by individual important words
            lambda: self._search_by_important_words(keywords),

            # Strategy 4: Search with original sentence (cleaned)
            lambda: self._search_clean_sentence(search_text, language),
        ]

        all_products: List[Dict[str, Any]] = []

        for strategy in search_strategies:
            try:
                result = await strategy()
                if result.success:
                    products_data = result.data.get("data", {}).get("products", [])
                    if products_data:
                        extracted = extract_products_from_results(products_data)
                        all_products.extend(extracted)
            except Exception as e:
                logger.warning(f"Search strategy failed: {e}")
                continue

        # === STEP 3: Intelligent Filtering ===
        # Apply AI-powered filtering based on detected intent
        if all_products:
            filtered_with_scores = self._filter_products_by_intent(all_products, intent)

            if filtered_with_scores:
                # Get top products
                top_products = [product for product, _score in filtered_with_scores[:limit]]

                # === STEP 4: Smart Response Generation ===
                # Generate intelligent Arabic response
                smart_response = self.intelligent_engine.generate_smart_response(
                    intent,
                    results_count=len(top_products)
                )

                # Format products with smart prefix
                formatted = [format_product_for_messenger(p, language) for p in top_products]

                # Add smart response as first message
                return [smart_response] + formatted

        # === FALLBACK: No Results After Intelligent Filtering ===
        # Try fuzzy search as last resort
        if not all_products:
            fuzzy_result = await self._search_popular_with_keywords(keywords)
            if fuzzy_result.success and fuzzy_result.data.get("data", {}).get("products"):
                products = fuzzy_result.data["data"]["products"]

                # Score with lower threshold for fuzzy matches
                scored_products: List[Tuple[Dict[str, Any], float]] = []
                for product_item in products:
                    product = cast(Dict[str, Any], product_item)
                    score = calculate_product_score(product, search_text)
                    if score > 0.1:
                        scored_products.append((product, score))

                if scored_products:
                    scored_products.sort(key=lambda x: float(x[1]), reverse=True)
                    unique_products: List[Dict[str, Any]] = []
                    seen_ids: Set[Any] = set()
                    for product_tuple in scored_products[:limit]:
                        product: Dict[str, Any] = product_tuple[0]
                        product_id = product.get('id')
                        if product_id and product_id not in seen_ids:
                            seen_ids.add(product_id)
                            unique_products.append(product)

                    if unique_products:
                        # Use smart response even for fuzzy results
                        smart_response = self.intelligent_engine.generate_smart_response(
                            intent,
                            results_count=len(unique_products)
                        )
                        formatted = [format_product_for_messenger(p, language) for p in unique_products]
                        return [smart_response] + formatted

        # === NO RESULTS: Provide Smart Suggestions ===
        suggestions = self._generate_search_suggestions(keywords, language)
        return [format_no_results_message(intent, suggestions, language, self.intelligent_engine)]
