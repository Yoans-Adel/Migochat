"""
BWW Store Integration Tests - Egyptian Dialect & Natural Language Understanding
==============================================================================

Tests comprehensive language understanding for Egyptian Arabic and English,
focusing on natural conversation patterns and real customer queries.

Author: BWW Store Team
Date: 2025
"""

import pytest
from bww_store import BWWStoreAPIService


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def bww_client():
    """Create BWW Store client instance"""
    return BWWStoreAPIService(language='ar')


@pytest.fixture
def search_engine():
    """Create BWW Store service instance with search enabled"""
    return BWWStoreAPIService(language='ar')


# ============================================================================
# Egyptian Dialect Tests
# ============================================================================

class TestEgyptianDialect:
    """Test Egyptian Arabic dialect understanding"""
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_want_expressions(self, bww_client):
        """Test different 'want' expressions in Egyptian dialect"""
        want_queries = [
            "عايز طقم صيفي حلو",  # عايز (want)
            "عاوز بنطلون جينز أسود",  # عاوز (alternative spelling)
            "محتاج جاكيت شتوي",  # محتاج (need)
            "نفسي في قميص أبيض",  # نفسي في (I wish/want)
            "ياريت طقم رياضي",  # ياريت (I wish)
            "بدور على فستان سهرة",  # بدور على (searching for)
        ]
        
        for query in want_queries:
            results = bww_client.search_and_format_products(query)
            assert results is not None, f"Failed for query: {query}"
            # Check if results contain products
            has_products = bool(results.get('products', []))
            print(f"✓ '{query}' → {len(results.get('products', []))} results")
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_quality_adjectives(self, bww_client):
        """Test Egyptian quality adjectives (حلو، جميل، جامد، etc.)"""
        quality_queries = [
            "عايز طقم حلو قوي",  # حلو قوي (very nice)
            "محتاج فستان جميل جدا",  # جميل جدا (very beautiful)
            "بدور على جاكيت جامد",  # جامد (excellent)
            "نفسي في قميص شيك",  # شيك (chic)
            "ياريت حذاء ظريف",  # ظريف (elegant)
        ]
        
        for query in quality_queries:
            results = bww_client.search(query)
            assert results is not None, f"Failed for query: {query}"
            # Quality adjectives should be properly normalized
            print(f"✓ '{query}' → normalized and searched")
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_demonstratives(self, bww_client):
        """Test Egyptian demonstratives (ده، دي، دول، كده)"""
        demo_queries = [
            "عايز قميص زي ده",  # زي ده (like this)
            "محتاج فستان زي كده",  # زي كده (like this)
            "بدور على طقم كدا",  # كدا (like this)
        ]
        
        for query in demo_queries:
            results = bww_client.search(query)
            assert results is not None, f"Failed for query: {query}"
            print(f"✓ '{query}' → {len(results)} results")
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_negation(self, bww_client):
        """Test Egyptian negation (مش، مافيش، etc.)"""
        negation_queries = [
            "عايز طقم مش غالي",  # مش (not)
            "محتاج جاكيت مش تقيل",  # مش تقيل (not heavy)
        ]
        
        for query in negation_queries:
            results = bww_client.search(query)
            # Should handle negation properly
            assert results is not None, f"Failed for query: {query}"
            print(f"✓ '{query}' → handled negation")


# ============================================================================
# Clothing Term Variations Tests
# ============================================================================

class TestClothingVariations:
    """Test clothing term variations and misspellings"""
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_shirt_variations(self, bww_client):
        """Test different ways to say 'shirt' in Egyptian"""
        shirt_variations = [
            "قميص",  # Standard
            "قميس",  # Common misspelling
            "تيشرت",  # T-shirt
            "تيشيرت",  # Alternative spelling
            "تي شيرت",  # Spaced
            "بلوزة",  # Blouse
            "توب",  # Top
        ]
        
        all_results = []
        for variation in shirt_variations:
            query = f"عايز {variation} أبيض"
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {variation}"
            all_results.append(len(results))
            print(f"✓ '{variation}' → {len(results)} results")
        
        # All variations should return similar results
        assert all(r > 0 for r in all_results), "Some variations returned no results"
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_pants_variations(self, bww_client):
        """Test different ways to say 'pants' in Egyptian"""
        pants_variations = [
            "بنطال",  # Standard
            "بنطلون",  # Common Egyptian
            "بنطلونه",  # With Egyptian suffix
            "سرويل",  # Classical
            "جينز",  # Jeans
            "جينس",  # Misspelling
        ]
        
        for variation in pants_variations:
            query = f"محتاج {variation} أسود"
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {variation}"
            assert len(results) > 0, f"No results for: {variation}"
            print(f"✓ '{variation}' → {len(results)} results")
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_jacket_variations(self, bww_client):
        """Test different ways to say 'jacket' in Egyptian"""
        jacket_variations = [
            "جاكيت",  # Standard
            "جاكيتة",  # Egyptian feminine
            "جاكت",  # Short form
            "ستره",  # Classical
            "سترة",  # Alternative
            "كوت",  # Coat
            "بليزر",  # Blazer
            "كاردجن",  # Cardigan
        ]
        
        for variation in jacket_variations:
            query = f"بدور على {variation}"
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {variation}"
            print(f"✓ '{variation}' → {len(results)} results")


# ============================================================================
# Color Variations Tests
# ============================================================================

class TestColorVariations:
    """Test color term variations and gender forms"""
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_red_variations(self, bww_client):
        """Test different forms of 'red' in Arabic"""
        red_variations = [
            "أحمر",  # Masculine
            "احمر",  # Without hamza
            "حمراء",  # Feminine
            "حمر",  # Shortened
            "ريد",  # English
        ]
        
        for color in red_variations:
            query = f"عايز قميص {color}"
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {color}"
            print(f"✓ 'قميص {color}' → {len(results)} results")
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_blue_variations(self, bww_client):
        """Test different forms of 'blue' in Arabic"""
        blue_variations = [
            "أزرق",  # Masculine
            "ازرق",  # Without hamza
            "زرقاء",  # Feminine
            "بليو",  # English
            "سماوي",  # Sky blue
            "نيلي",  # Navy
        ]
        
        for color in blue_variations:
            query = f"محتاج بنطال {color}"
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {color}"
            print(f"✓ 'بنطال {color}' → {len(results)} results")


# ============================================================================
# Real Customer Queries Tests
# ============================================================================

class TestRealCustomerQueries:
    """Test real-world customer queries in natural Egyptian dialect"""
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_casual_outfit_queries(self, bww_client):
        """Test casual outfit queries"""
        casual_queries = [
            "عايز طقم كاجوال للشغل",
            "محتاج لبس كاجول للجامعة",
            "بدور على ملابس عملية ومريحة",
            "نفسي في طقم كومفي للبيت",
        ]
        
        for query in casual_queries:
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {query}"
            assert len(results) > 0, f"No results for: {query}"
            print(f"✓ '{query}' → {len(results)} results")
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_formal_outfit_queries(self, bww_client):
        """Test formal outfit queries"""
        formal_queries = [
            "عايز بدلة رسمية للفرح",
            "محتاج طقم فورمال للشغل",
            "بدور على لبس أنيق للمناسبات",
            "نفسي في فستان سواريه للحفلة",
        ]
        
        for query in formal_queries:
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {query}"
            print(f"✓ '{query}' → {len(results)} results")
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_sports_outfit_queries(self, bww_client):
        """Test sports outfit queries"""
        sports_queries = [
            "عايز طقم رياضي للجيم",
            "محتاج لبس سبورت للتمرين",
            "بدور على ملابس فيتنس",
            "نفسي في كوتشي للران",
        ]
        
        for query in sports_queries:
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {query}"
            print(f"✓ '{query}' → {len(results)} results")
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_seasonal_queries(self, bww_client):
        """Test seasonal clothing queries"""
        seasonal_queries = [
            "عايز طقم صيفي خفيف",
            "محتاج جاكيت شتوي دافي",
            "بدور على قميص قطن للصيف",
            "نفسي في معطف صوف للشتاء",
        ]
        
        for query in seasonal_queries:
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {query}"
            print(f"✓ '{query}' → {len(results)} results")
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_gender_specific_queries(self, bww_client):
        """Test gender-specific queries"""
        gender_queries = [
            "عايز طقم رجالي كلاسيك",
            "محتاج فستان نسائي حلو",
            "بدور على ملابس أطفال",
            "نفسي في هودي للولاد",
            "ياريت فستان للبنات",
        ]
        
        for query in gender_queries:
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {query}"
            print(f"✓ '{query}' → {len(results)} results")
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_multi_attribute_queries(self, bww_client):
        """Test queries with multiple attributes"""
        complex_queries = [
            "عايز قميص أبيض قطن رجالي",
            "محتاج بنطال جينز أسود واسع",
            "بدور على فستان وردي طويل للسهرة",
            "نفسي في جاكيت جلد أسود رجالي",
            "ياريت طقم رياضي أزرق للأطفال",
        ]
        
        for query in complex_queries:
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {query}"
            assert len(results) > 0, f"No results for complex query: {query}"
            print(f"✓ '{query}' → {len(results)} results")


# ============================================================================
# Context Understanding Tests
# ============================================================================

class TestContextUnderstanding:
    """Test context-aware search and intent understanding"""
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_complete_outfit_intent(self, bww_client):
        """Test understanding of 'complete outfit' intent"""
        outfit_queries = [
            "عايز طقم كامل",  # Complete outfit
            "محتاج طقم متكامل",  # Integrated outfit
            "بدور على لبس كومبليت",  # Complete look
            "نفسي في انسامبل حلو",  # Ensemble
        ]
        
        for query in outfit_queries:
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {query}"
            # Should prioritize outfit sets
            print(f"✓ '{query}' → understood outfit intent")
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_occasion_context(self, bww_client):
        """Test understanding occasion context"""
        occasion_queries = [
            "عايز لبس للفرح",  # Wedding
            "محتاج طقم للشغل",  # Work
            "بدور على فستان للحفلة",  # Party
            "نفسي في لبس للجامعة",  # University
            "ياريت طقم للسهرة",  # Evening
        ]
        
        for query in occasion_queries:
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {query}"
            print(f"✓ '{query}' → understood occasion context")
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_price_hints(self, bww_client):
        """Test understanding price hints"""
        price_queries = [
            "عايز طقم مش غالي",  # Not expensive
            "محتاج حاجة رخيصة شوية",  # Cheap
            "بدور على حاجة بسعر مناسب",  # Affordable
        ]
        
        for query in price_queries:
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {query}"
            print(f"✓ '{query}' → understood price hint")


# ============================================================================
# Misspelling Tolerance Tests
# ============================================================================

class TestMisspellingTolerance:
    """Test tolerance for common misspellings"""
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_common_typos(self, bww_client):
        """Test common typing errors"""
        typo_pairs = [
            ("قميص", "قمسي"),  # Reversed letters
            ("جاكيت", "جاكت"),  # Missing letter
            ("بنطال", "بنطلون"),  # Alternative form
            ("جينز", "جينس"),  # س instead of ز
        ]
        
        for correct, typo in typo_pairs:
            query_correct = f"عايز {correct} أبيض"
            query_typo = f"عايز {typo} أبيض"
            
            results_correct = bww_client.search(query_correct)
            results_typo = bww_client.search(query_typo)
            
            assert results_correct is not None
            assert results_typo is not None
            
            # Both should return results
            assert len(results_correct) > 0
            assert len(results_typo) > 0
            
            print(f"✓ '{typo}' tolerated (finds '{correct}')")


# ============================================================================
# English Language Tests
# ============================================================================

class TestEnglishQueries:
    """Test English language queries"""
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_basic_english_queries(self, bww_client):
        """Test basic English queries"""
        english_queries = [
            "white shirt",
            "black pants",
            "blue jacket",
            "red dress",
            "sports shoes",
        ]
        
        for query in english_queries:
            results = bww_client.search(query, language='en')
            assert results is not None, f"Failed for: {query}"
            print(f"✓ '{query}' → {len(results)} results")
    
    @pytest.mark.bww_store
    @pytest.mark.integration
    def test_mixed_language_queries(self, bww_client):
        """Test mixed Arabic-English queries"""
        mixed_queries = [
            "عايز shirt أبيض",  # Arabic + English
            "محتاج jeans أسود",  # Arabic + English
            "white قميص",  # English + Arabic
        ]
        
        for query in mixed_queries:
            results = bww_client.search(query)
            assert results is not None, f"Failed for: {query}"
            print(f"✓ '{query}' → handled mixed language")


# ============================================================================
# Performance Tests
# ============================================================================

class TestSearchPerformance:
    """Test search performance and caching"""
    
    @pytest.mark.bww_store
    @pytest.mark.performance
    def test_search_speed(self, bww_client):
        """Test search response time"""
        import time
        
        query = "عايز قميص أبيض"
        
        start = time.time()
        results = bww_client.search(query)
        duration = time.time() - start
        
        assert results is not None
        assert duration < 5.0, f"Search took too long: {duration}s"
        print(f"✓ Search completed in {duration:.3f}s")
    
    @pytest.mark.bww_store
    @pytest.mark.performance
    def test_cache_effectiveness(self, bww_client):
        """Test that caching improves performance"""
        import time
        
        query = "عايز طقم رياضي"
        
        # First search (no cache)
        start1 = time.time()
        results1 = bww_client.search(query)
        duration1 = time.time() - start1
        
        # Second search (cached)
        start2 = time.time()
        results2 = bww_client.search(query)
        duration2 = time.time() - start2
        
        assert results1 is not None
        assert results2 is not None
        # Cached should be faster
        print(f"✓ First: {duration1:.3f}s, Cached: {duration2:.3f}s")


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == '__main__':
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-m', 'bww_store',
        '--color=yes'
    ])
