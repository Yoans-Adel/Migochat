"""
Product Filtering Utilities - Refactored from search.py for better maintainability

This module contains helper functions to reduce complexity of product filtering logic.
"""
from typing import Dict, Any, Tuple, Protocol

from .intelligent_search import SearchIntent, PriceRange, Occasion, Season


class FuzzyMatcherProtocol(Protocol):
    """Protocol for fuzzy matcher to avoid circular import."""
    def similarity_score(self, text1: str, text2: str) -> float:
        ...


# Price range mapping (based on Egyptian market analysis + BWW Store data)
PRICE_RANGES = {
    PriceRange.VERY_LOW: (0, 150),      # ببلاش، رخيص جدا
    PriceRange.LOW: (150, 350),          # رخيص، مش غالي
    PriceRange.MEDIUM: (350, 650),       # عادي، متوسط
    PriceRange.HIGH: (650, 1200),        # غالي، مكلف
    PriceRange.VERY_HIGH: (1200, 999999)  # فخم، راقي، لوكس
}

# Occasion keywords for smart matching
OCCASION_KEYWORDS = {
    Occasion.WEDDING: ['عريس', 'عروس', 'فرح', 'زفاف', 'بدلة', 'سواريه'],
    Occasion.WORK: ['رسمي', 'أوفيس', 'شغل', 'formal', 'office'],
    Occasion.PARTY: ['سهرة', 'حفلة', 'party', 'evening'],
    Occasion.SPORTS: ['رياضة', 'sport', 'athletic', 'جيم', 'ران'],
    Occasion.FORMAL: ['رسمي', 'كلاسيك', 'أنيق', 'formal'],
    Occasion.CASUAL: ['كاجوال', 'عادي', 'casual', 'يومي'],
    Occasion.BEACH: ['بحر', 'شاطئ', 'beach', 'سباحة'],
    Occasion.HOME: ['بيت', 'نوم', 'home', 'sleep'],
    Occasion.SCHOOL: ['مدرسة', 'جامعة', 'school']
}

# Season keywords for smart matching
SEASON_KEYWORDS = {
    Season.SUMMER: ['صيف', 'خفيف', 'قطن', 'summer', 'light'],
    Season.WINTER: ['شتاء', 'دافي', 'صوف', 'winter', 'warm', 'ثقيل'],
    Season.SPRING: ['ربيع', 'spring'],
    Season.AUTUMN: ['خريف', 'autumn', 'fall']
}


def score_price_match(product: Dict[str, Any], intent: SearchIntent) -> Tuple[float, bool]:
    """Score product based on price range matching.

    Returns:
        Tuple of (score_delta, has_critical_mismatch)
    """
    if not intent.price_range:
        return 0.0, False

    price = product.get("price", 0)
    min_price, max_price = PRICE_RANGES[intent.price_range]

    if min_price <= price <= max_price:
        # Perfect price match
        return 2.0, False
    elif price < min_price * 0.8:
        # Much cheaper - still acceptable
        return 1.0, False
    elif price <= min_price:
        # Slightly cheaper - good
        return 1.5, False
    elif price <= max_price * 1.2:
        # Slightly more expensive - acceptable
        return 0.5, False
    else:
        # Too expensive - critical mismatch
        return -2.0, True


def score_occasion_match(product: Dict[str, Any], intent: SearchIntent, fuzzy_matcher: FuzzyMatcherProtocol) -> Tuple[float, bool]:
    """Score product based on occasion matching.

    Returns:
        Tuple of (score_delta, has_critical_mismatch)
    """
    if not intent.occasion:
        return 0.0, False

    name = product.get("name", "").lower()
    description = product.get("description", "").lower()
    combined_text = f"{name} {description}"

    occasion_terms = OCCASION_KEYWORDS.get(intent.occasion, [])
    occasion_matches = 0

    for term in occasion_terms:
        if term in combined_text:
            occasion_matches += 1
        else:
            # Fuzzy match with intelligent engine
            similarity = fuzzy_matcher.similarity_score(term, name)
            if similarity > 0.6:
                occasion_matches += similarity

    if occasion_matches > 0:
        # Strong occasion match
        return occasion_matches * 1.5, False
    else:
        # No occasion match - this is critical
        return -1.5, True


def score_season_match(product: Dict[str, Any], intent: SearchIntent, fuzzy_matcher: FuzzyMatcherProtocol) -> float:
    """Score product based on season matching."""
    if not intent.season or intent.season == Season.ALL_SEASON:
        return 0.0

    name = product.get("name", "").lower()
    description = product.get("description", "").lower()
    combined_text = f"{name} {description}"

    season_terms = SEASON_KEYWORDS.get(intent.season, [])
    season_matches = 0

    for term in season_terms:
        if term in combined_text:
            season_matches += 1
        else:
            # Fuzzy match
            similarity = fuzzy_matcher.similarity_score(term, combined_text)
            if similarity > 0.5:
                season_matches += similarity * 0.7

    if season_matches > 0:
        return season_matches * 1.0
    else:
        # Wrong season - penalty
        return -0.8


def score_quality_match(product: Dict[str, Any], intent: SearchIntent) -> Tuple[float, bool]:
    """Score product based on quality preference.

    Returns:
        Tuple of (score_delta, has_critical_mismatch)
    """
    if not intent.quality_preference:
        return 0.0, False

    rating = product.get("rating", 0)
    is_best_seller = product.get("is_best_seller", False)

    if intent.quality_preference == 'excellent':
        # Wants premium quality - STRICT
        if rating >= 4.5 and is_best_seller:
            return 2.0, False
        elif rating >= 4.2:
            return 1.0, False
        elif rating >= 3.8:
            return 0.3, False
        else:
            # Not good enough quality
            return -1.5, True

    elif intent.quality_preference == 'very_good':
        if rating >= 4.0:
            return 1.5, False
        elif rating >= 3.5:
            return 0.7, False
        else:
            return -0.5, False

    elif intent.quality_preference == 'good':
        if rating >= 3.5:
            return 1.0, False
        elif rating >= 3.0:
            return 0.5, False
        return 0.0, False

    elif intent.quality_preference == 'acceptable':
        if rating >= 3.0:
            return 0.8, False
        elif rating >= 2.5:
            return 0.3, False
        return 0.0, False

    return 0.0, False


def score_outfit_match(product: Dict[str, Any], intent: SearchIntent) -> float:
    """Score product based on complete outfit detection."""
    if not intent.wants_complete_outfit:
        return 0.0

    name = product.get("name", "").lower()
    description = product.get("description", "").lower()
    combined_text = f"{name} {description}"

    # Boost sets, combos, complete outfits
    outfit_keywords = ['طقم', 'كومبليت', 'set', 'combo', 'outfit', 'كامل']
    outfit_match = sum(1 for keyword in outfit_keywords if keyword in combined_text)

    if outfit_match > 0:
        return outfit_match * 1.5
    else:
        # User wants outfit but this isn't - significant penalty
        return -1.2


def calculate_match_ratio(intent: SearchIntent, match_count: float) -> float:
    """Calculate the ratio of matched criteria."""
    total_criteria = sum([
        1 if intent.price_range else 0,
        1 if intent.occasion else 0,
        1 if intent.season and intent.season != Season.ALL_SEASON else 0,
        1 if intent.quality_preference else 0,
        1 if intent.wants_complete_outfit else 0
    ])

    if total_criteria == 0:
        return 1.0

    return match_count / total_criteria


def should_include_product(
    intent: SearchIntent,
    score: float,
    match_count: float,
    has_critical_mismatch: bool
) -> bool:
    """Determine if product should be included in results.

    Args:
        intent: Search intent with user preferences
        score: Product score
        match_count: Number of matched criteria
        has_critical_mismatch: Whether there's a critical mismatch

    Returns:
        True if product should be included
    """
    if has_critical_mismatch:
        return False

    quality_threshold = 1.0

    if intent.price_range or intent.occasion or intent.quality_preference:
        quality_threshold = 1.5
        match_ratio = calculate_match_ratio(intent, match_count)
        if match_ratio < 0.5:
            return False

    return score >= quality_threshold
