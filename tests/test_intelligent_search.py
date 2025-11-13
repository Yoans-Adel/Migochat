"""
Intelligent Search Engine Tests
===============================

Tests for advanced search features including fuzzy matching,
context understanding, and intelligent filtering.
"""

import pytest
from bww_store.intelligent_search import (
    IntelligentSearchEngine,
    FuzzyMatcher,
    PriceDetector,
    OccasionDetector,
    SeasonDetector,
    ContextAnalyzer,
    SearchIntent,
    PriceRange,
    Occasion,
    Season
)
from bww_store.constants import CLOTHING_KEYWORDS_AR


# ============================================================================
# Fuzzy Matching Tests
# ============================================================================

class TestFuzzyMatcher:
    """Test fuzzy string matching"""
    
    def test_levenshtein_distance_identical(self):
        """Test distance for identical strings"""
        assert FuzzyMatcher.levenshtein_distance("hello", "hello") == 0
    
    def test_levenshtein_distance_one_char(self):
        """Test distance for one character difference"""
        assert FuzzyMatcher.levenshtein_distance("hello", "hallo") == 1
    
    def test_levenshtein_distance_arabic(self):
        """Test distance for Arabic words"""
        # قميص vs قمسي (typo)
        distance = FuzzyMatcher.levenshtein_distance("قميص", "قمسي")
        assert distance <= 2
    
    def test_similarity_score_identical(self):
        """Test similarity for identical strings"""
        score = FuzzyMatcher.similarity_score("test", "test")
        assert score == 1.0
    
    def test_similarity_score_similar(self):
        """Test similarity for similar strings"""
        score = FuzzyMatcher.similarity_score("قميص", "قمسي")
        assert score > 0.4  # Should be similar (adjusted for Arabic)
    
    def test_similarity_score_different(self):
        """Test similarity for different strings"""
        score = FuzzyMatcher.similarity_score("قميص", "بنطلون")
        assert score < 0.5  # Should be different
    
    def test_find_best_match(self):
        """Test finding best match from candidates"""
        candidates = ["قميص", "بنطال", "جاكيت"]
        match = FuzzyMatcher.find_best_match("قمسي", candidates, threshold=0.5)
        assert match == "قميص"
    
    def test_fuzzy_search(self):
        """Test fuzzy search in text"""
        text = "عايز قميص أبيض حلو"
        assert FuzzyMatcher.fuzzy_search("قميص", text) is True
        assert FuzzyMatcher.fuzzy_search("قمسي", text, threshold=0.5) is True


# ============================================================================
# Price Detector Tests
# ============================================================================

class TestPriceDetector:
    """Test price range detection"""
    
    def test_detect_very_low(self):
        """Test detection of very low price"""
        assert PriceDetector.detect("عايز حاجة ببلاش") == PriceRange.VERY_LOW
    
    def test_detect_low(self):
        """Test detection of low price"""
        assert PriceDetector.detect("محتاج حاجة رخيصة") == PriceRange.LOW
        assert PriceDetector.detect("عايز حاجة مش غالية") == PriceRange.LOW
    
    def test_detect_medium(self):
        """Test detection of medium price"""
        assert PriceDetector.detect("سعر متوسط") == PriceRange.MEDIUM
    
    def test_detect_high(self):
        """Test detection of high price"""
        assert PriceDetector.detect("عايز حاجة غالية") == PriceRange.HIGH
    
    def test_detect_very_high(self):
        """Test detection of very high price"""
        assert PriceDetector.detect("نفسي في حاجة فخمة") == PriceRange.VERY_HIGH
    
    def test_detect_none(self):
        """Test no price detection"""
        assert PriceDetector.detect("عايز قميص أبيض") is None


# ============================================================================
# Occasion Detector Tests
# ============================================================================

class TestOccasionDetector:
    """Test occasion detection"""
    
    def test_detect_wedding(self):
        """Test wedding detection"""
        assert OccasionDetector.detect("عايز طقم للفرح") == Occasion.WEDDING
        assert OccasionDetector.detect("محتاج لبس للزفاف") == Occasion.WEDDING
    
    def test_detect_work(self):
        """Test work detection"""
        assert OccasionDetector.detect("عايز لبس للشغل") == Occasion.WORK
        assert OccasionDetector.detect("محتاج طقم للمكتب") == Occasion.WORK
    
    def test_detect_party(self):
        """Test party detection"""
        assert OccasionDetector.detect("فستان للحفلة") == Occasion.PARTY
        assert OccasionDetector.detect("لبس للسهرة") == Occasion.PARTY
    
    def test_detect_sports(self):
        """Test sports detection"""
        assert OccasionDetector.detect("طقم للجيم") == Occasion.SPORTS
        assert OccasionDetector.detect("ملابس رياضية") == Occasion.SPORTS
    
    def test_detect_formal(self):
        """Test formal detection"""
        assert OccasionDetector.detect("لبس رسمي") == Occasion.FORMAL
        assert OccasionDetector.detect("طقم فورمال") == Occasion.FORMAL
    
    def test_detect_casual(self):
        """Test casual detection"""
        assert OccasionDetector.detect("لبس كاجوال") == Occasion.CASUAL
        assert OccasionDetector.detect("ملابس يومية") == Occasion.CASUAL
    
    def test_detect_none(self):
        """Test no occasion detection"""
        assert OccasionDetector.detect("عايز قميص") is None


# ============================================================================
# Season Detector Tests
# ============================================================================

class TestSeasonDetector:
    """Test season detection"""
    
    def test_detect_summer(self):
        """Test summer detection"""
        assert SeasonDetector.detect("عايز طقم صيفي") == Season.SUMMER
        assert SeasonDetector.detect("قميص قطن خفيف") == Season.SUMMER
    
    def test_detect_winter(self):
        """Test winter detection"""
        assert SeasonDetector.detect("جاكيت شتوي") == Season.WINTER
        assert SeasonDetector.detect("معطف دافئ") == Season.WINTER
    
    def test_detect_spring(self):
        """Test spring detection"""
        assert SeasonDetector.detect("ملابس ربيعية") == Season.SPRING
    
    def test_detect_autumn(self):
        """Test autumn detection"""
        assert SeasonDetector.detect("لبس خريفي") == Season.AUTUMN
    
    def test_detect_default(self):
        """Test default all-season detection"""
        result = SeasonDetector.detect("عايز قميص")
        assert result == Season.ALL_SEASON


# ============================================================================
# Context Analyzer Tests
# ============================================================================

class TestContextAnalyzer:
    """Test context analysis"""
    
    def test_wants_complete_outfit_true(self):
        """Test complete outfit detection - positive"""
        assert ContextAnalyzer.wants_complete_outfit("عايز طقم كامل") is True
        assert ContextAnalyzer.wants_complete_outfit("محتاج لبس كومبليت") is True
    
    def test_wants_complete_outfit_false(self):
        """Test complete outfit detection - negative"""
        assert ContextAnalyzer.wants_complete_outfit("عايز قميص") is False
    
    def test_detect_quality_excellent(self):
        """Test excellent quality detection"""
        assert ContextAnalyzer.detect_quality_preference("حاجة جامدة") == 'excellent'
    
    def test_detect_quality_good(self):
        """Test good quality detection"""
        assert ContextAnalyzer.detect_quality_preference("حاجة حلوة") == 'good'
        assert ContextAnalyzer.detect_quality_preference("حاجة جميلة") == 'good'
    
    def test_detect_quality_none(self):
        """Test no quality detection"""
        assert ContextAnalyzer.detect_quality_preference("عايز قميص") is None
    
    def test_extract_item_types(self):
        """Test item type extraction"""
        query = "عايز قميص وبنطلون"
        items = ContextAnalyzer.extract_item_types(query, CLOTHING_KEYWORDS_AR)
        assert 'قميص' in items
        assert 'بنطال' in items


# ============================================================================
# Intelligent Search Engine Tests
# ============================================================================

class TestIntelligentSearchEngine:
    """Test main intelligent search engine"""
    
    @pytest.fixture
    def engine(self):
        """Create search engine instance"""
        return IntelligentSearchEngine(CLOTHING_KEYWORDS_AR)
    
    def test_analyze_simple_query(self, engine):
        """Test simple query analysis"""
        intent = engine.analyze_query("عايز قميص")
        
        assert intent.query == "عايز قميص"
        assert intent.price_range is None
        assert intent.occasion is None
    
    def test_analyze_complex_query(self, engine):
        """Test complex query with multiple attributes"""
        intent = engine.analyze_query("عايز طقم كامل للفرح صيفي ومش غالي")
        
        assert intent.wants_complete_outfit is True
        assert intent.occasion == Occasion.WEDDING
        assert intent.season == Season.SUMMER
        assert intent.price_range == PriceRange.LOW
    
    def test_analyze_price_query(self, engine):
        """Test query with price preference"""
        intent = engine.analyze_query("محتاج قميص رخيص")
        
        assert intent.price_range == PriceRange.LOW
    
    def test_analyze_occasion_query(self, engine):
        """Test query with occasion"""
        intent = engine.analyze_query("فستان للحفلة")
        
        assert intent.occasion == Occasion.PARTY
    
    def test_analyze_season_query(self, engine):
        """Test query with season"""
        intent = engine.analyze_query("جاكيت شتوي")
        
        assert intent.season == Season.WINTER
    
    def test_generate_search_filters(self, engine):
        """Test search filter generation"""
        intent = engine.analyze_query("عايز طقم للشغل صيفي")
        filters = engine.generate_search_filters(intent)
        
        assert filters['occasion'] == Occasion.WORK.value
        assert filters['season'] == Season.SUMMER.value
    
    def test_generate_smart_response_with_results(self, engine):
        """Test smart response generation with results"""
        intent = engine.analyze_query("عايز طقم للفرح")
        response = engine.generate_smart_response(intent, 10)
        
        assert "لقيتلك" in response
        assert "للفرح" in response or "فرح" in response.lower()
    
    def test_generate_smart_response_no_results(self, engine):
        """Test smart response generation without results"""
        intent = engine.analyze_query("عايز حاجة")
        response = engine.generate_smart_response(intent, 0)
        
        assert "مافيش نتائج" in response or "معلش" in response
    
    def test_generate_smart_response_quality(self, engine):
        """Test smart response with quality preference"""
        intent = engine.analyze_query("عايز حاجة جامدة")
        response = engine.generate_smart_response(intent, 5)
        
        assert "جامدة" in response or "جامد" in response


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntelligentSearchIntegration:
    """Integration tests for intelligent search"""
    
    @pytest.fixture
    def engine(self):
        """Create search engine instance"""
        return IntelligentSearchEngine(CLOTHING_KEYWORDS_AR)
    
    def test_real_world_query_1(self, engine):
        """Test: عايز طقم كامل للفرح صيفي ومش غالي"""
        intent = engine.analyze_query("عايز طقم كامل للفرح صيفي ومش غالي")
        
        assert intent.wants_complete_outfit is True
        assert intent.occasion == Occasion.WEDDING
        assert intent.season == Season.SUMMER
        assert intent.price_range == PriceRange.LOW
        
        filters = engine.generate_search_filters(intent)
        assert 'complete_outfit' in filters
        assert filters['occasion'] == 'wedding'
        assert filters['season'] == 'summer'
        assert filters['price_range'] == 'low'
    
    def test_real_world_query_2(self, engine):
        """Test: محتاج قميص أبيض للشغل"""
        intent = engine.analyze_query("محتاج قميص أبيض للشغل")
        
        assert intent.occasion == Occasion.WORK
        assert 'قميص' in intent.item_types
    
    def test_real_world_query_3(self, engine):
        """Test: بدور على جاكيت شتوي دافي"""
        intent = engine.analyze_query("بدور على جاكيت شتوي دافي")
        
        assert intent.season == Season.WINTER
        assert 'جاكيت' in intent.item_types
    
    def test_real_world_query_4(self, engine):
        """Test: نفسي في فستان حلو للسهرة"""
        intent = engine.analyze_query("نفسي في فستان حلو للسهرة")
        
        assert intent.occasion == Occasion.PARTY
        assert intent.quality_preference == 'good'
        assert 'فستان' in intent.item_types
    
    def test_real_world_query_5(self, engine):
        """Test: ياريت طقم رياضي للجيم"""
        intent = engine.analyze_query("ياريت طقم رياضي للجيم")
        
        assert intent.occasion == Occasion.SPORTS


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
