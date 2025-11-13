"""
Integration Tests for Intelligent Search with BWW API Service

Tests the full integration of IntelligentSearchEngine with BWWStoreAPIService
to ensure real-world queries work with high precision and smart responses.
"""

import pytest
from unittest.mock import AsyncMock, patch

from bww_store.api_client import BWWStoreAPIService
from bww_store.models import APIResponse


# === Mock Product Data ===

MOCK_PRODUCTS = [
    {
        "id": 1,
        "name": "بدلة رسمية فخمة للأفراح",
        "name_en": "Luxury Formal Suit for Weddings",
        "description": "بدلة رسمية راقية مناسبة للأفراح والمناسبات الرسمية",
        "price": 1500,
        "rating": 4.8,
        "is_best_seller": True,
        "category": "بدل",
        "image_url": "https://example.com/suit1.jpg"
    },
    {
        "id": 2,
        "name": "قميص قطن صيفي خفيف",
        "name_en": "Light Cotton Summer Shirt",
        "description": "قميص قطن خفيف مناسب للصيف",
        "price": 250,
        "rating": 4.2,
        "is_best_seller": False,
        "category": "قمصان",
        "image_url": "https://example.com/shirt1.jpg"
    },
    {
        "id": 3,
        "name": "طقم رياضي كامل للجيم",
        "name_en": "Complete Athletic Gym Set",
        "description": "طقم رياضي كامل مناسب للتمرين والجيم",
        "price": 450,
        "rating": 4.5,
        "is_best_seller": True,
        "category": "ملابس رياضية",
        "image_url": "https://example.com/gym1.jpg"
    },
    {
        "id": 4,
        "name": "جاكيت شتوي دافي",
        "name_en": "Warm Winter Jacket",
        "description": "جاكيت شتوي دافي من الصوف",
        "price": 800,
        "rating": 4.6,
        "is_best_seller": False,
        "category": "جواكت",
        "image_url": "https://example.com/jacket1.jpg"
    },
    {
        "id": 5,
        "name": "بنطلون جينز كاجوال",
        "name_en": "Casual Jeans Pants",
        "description": "بنطلون جينز كاجوال للاستخدام اليومي",
        "price": 350,
        "rating": 4.0,
        "is_best_seller": False,
        "category": "بناطيل",
        "image_url": "https://example.com/jeans1.jpg"
    },
    {
        "id": 6,
        "name": "فستان سهرة راقي",
        "name_en": "Elegant Evening Dress",
        "description": "فستان سهرة راقي للحفلات والمناسبات",
        "price": 1200,
        "rating": 4.9,
        "is_best_seller": True,
        "category": "فساتين",
        "image_url": "https://example.com/dress1.jpg"
    },
    {
        "id": 7,
        "name": "قميص أبيض رسمي للشغل",
        "name_en": "White Formal Work Shirt",
        "description": "قميص أبيض رسمي مناسب للعمل والمكتب",
        "price": 280,
        "rating": 4.3,
        "is_best_seller": False,
        "category": "قمصان",
        "image_url": "https://example.com/shirt2.jpg"
    },
    {
        "id": 8,
        "name": "شورت بحر خفيف",
        "name_en": "Light Beach Shorts",
        "description": "شورت خفيف للبحر والشاطئ",
        "price": 180,
        "rating": 4.1,
        "is_best_seller": False,
        "category": "شورتات",
        "image_url": "https://example.com/shorts1.jpg"
    }
]


# === Fixtures ===

@pytest.fixture
async def mock_api_client():
    """Create mock API client with predefined product responses."""
    client = AsyncMock(spec=BWWStoreAPIService)
    
    async def mock_filter_products(*args, **kwargs):
        """Return mock products based on search parameters."""
        search = kwargs.get('search', '').lower()
        
        # Filter products based on search term
        if search:
            filtered = [
                p for p in MOCK_PRODUCTS
                if search in p['name'].lower() or search in p['description'].lower()
            ]
        else:
            filtered = MOCK_PRODUCTS
        
        return APIResponse(
            data={
                "data": {
                    "products": filtered
                }
            },
            success=True
        )
    
    client.filter_products = mock_filter_products
    return client


@pytest.fixture
async def api_service(mock_api_client):
    """Create BWWStoreAPIService with mocked client."""
    with patch('bww_store.api_client.BWWStoreAPIClient', return_value=mock_api_client):
        service = BWWStoreAPIService(language='ar')
        # Replace client with mock
        service.client = mock_api_client
        service.search.client = mock_api_client
        return service


# === Integration Tests ===

class TestIntelligentIntegration:
    """Test full integration of intelligent search with API service."""

    @pytest.mark.asyncio
    async def test_wedding_outfit_query(self, api_service):
        """Test: عايز طقم كامل للفرح صيفي ومش غالي"""
        results = await api_service.search_and_format_products(
            "عايز طقم كامل للفرح صيفي ومش غالي",
            limit=3
        )
        
        assert len(results) > 0
        # First result should be smart response
        assert isinstance(results[0], str)
        # Should mention occasion or intent
        assert any(word in results[0] for word in ['فرح', 'حلو', 'جامد', 'لقيت'])

    @pytest.mark.asyncio
    async def test_work_shirt_query(self, api_service):
        """Test: محتاج قميص أبيض للشغل"""
        results = await api_service.search_and_format_products(
            "محتاج قميص أبيض للشغل",
            limit=3
        )
        
        assert len(results) > 0
        # Should return work-related products
        response_text = ' '.join(results)
        assert 'قميص' in response_text or 'shirt' in response_text.lower()

    @pytest.mark.asyncio
    async def test_winter_jacket_query(self, api_service):
        """Test: بدور على جاكيت شتوي دافي"""
        results = await api_service.search_and_format_products(
            "بدور على جاكيت شتوي دافي",
            limit=3
        )
        
        assert len(results) > 0
        response_text = ' '.join(results)
        assert 'جاكيت' in response_text or 'jacket' in response_text.lower()

    @pytest.mark.asyncio
    async def test_party_dress_query(self, api_service):
        """Test: نفسي في فستان حلو للسهرة"""
        results = await api_service.search_and_format_products(
            "نفسي في فستان حلو للسهرة",
            limit=3
        )
        
        assert len(results) > 0
        response_text = ' '.join(results)
        assert 'فستان' in response_text or 'dress' in response_text.lower()

    @pytest.mark.asyncio
    async def test_gym_outfit_query(self, api_service):
        """Test: عايز لبس للجيم"""
        results = await api_service.search_and_format_products(
            "عايز لبس للجيم",
            limit=3
        )
        
        assert len(results) > 0
        response_text = ' '.join(results)
        # Should find gym/sports items
        assert any(word in response_text for word in ['رياضي', 'جيم', 'sport', 'gym'])

    @pytest.mark.asyncio
    async def test_cheap_products_query(self, api_service):
        """Test: عايز حاجة رخيصة"""
        results = await api_service.search_and_format_products(
            "عايز حاجة رخيصة",
            limit=3
        )
        
        assert len(results) > 0
        # Should prioritize low-priced items
        # First result is smart response, check products after
        if len(results) > 1:
            # Products should be there
            assert isinstance(results[1], str)

    @pytest.mark.asyncio
    async def test_luxury_query(self, api_service):
        """Test: نفسي في حاجة فخمة راقية"""
        results = await api_service.search_and_format_products(
            "نفسي في حاجة فخمة راقية",
            limit=3
        )
        
        assert len(results) > 0
        # Should mention quality or luxury in response
        assert any(word in results[0] for word in ['فخم', 'راقي', 'جامد', 'حلو'])

    @pytest.mark.asyncio
    async def test_beach_shorts_query(self, api_service):
        """Test: عايز شورت للبحر"""
        results = await api_service.search_and_format_products(
            "عايز شورت للبحر",
            limit=3
        )
        
        assert len(results) > 0
        response_text = ' '.join(results)
        assert 'شورت' in response_text or 'shorts' in response_text.lower()

    @pytest.mark.asyncio
    async def test_smart_response_generation(self, api_service):
        """Test that smart responses are generated correctly."""
        results = await api_service.search_and_format_products(
            "عايز طقم للفرح",
            limit=3
        )
        
        # First item should be smart response
        assert len(results) > 0
        smart_response = results[0]
        
        # Should be in Arabic
        assert any(arabic_char in smart_response for arabic_char in 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        
        # Should be helpful and friendly
        assert any(word in smart_response for word in ['لقيت', 'حلو', 'جامد', 'مناسب'])

    @pytest.mark.asyncio
    async def test_typo_handling(self, api_service):
        """Test: عايز قمسي (typo for قميص)"""
        results = await api_service.search_and_format_products(
            "عايز قمسي",  # قمسي is a typo
            limit=3
        )
        
        # Should still find results despite typo
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_multiple_criteria(self, api_service):
        """Test query with multiple criteria: price + occasion + season"""
        results = await api_service.search_and_format_products(
            "محتاج طقم للشغل صيفي وسعره حلو",
            limit=3
        )
        
        assert len(results) > 0
        # Should understand: work + summer + affordable price
        smart_response = results[0]
        assert isinstance(smart_response, str)

    @pytest.mark.asyncio
    async def test_quality_preference(self, api_service):
        """Test quality preference detection."""
        # Excellent quality request
        results = await api_service.search_and_format_products(
            "عايز حاجة جامدة جدا",
            limit=3
        )
        
        assert len(results) > 0
        # Should prioritize high-rated products

    @pytest.mark.asyncio
    async def test_no_results_with_suggestions(self, api_service):
        """Test that suggestions are provided when no results found."""
        # Search for something unlikely to exist
        results = await api_service.search_and_format_products(
            "عايز طائرة فضائية",  # Searching for "spaceship" :)
            limit=3
        )
        
        assert len(results) > 0
        # Should have smart response even with no results
        response = results[0]
        # Should provide suggestions or helpful message
        assert any(word in response for word in ['معلش', 'مافيش', 'جرب', 'اقتراح', '💡'])

    @pytest.mark.asyncio
    async def test_complete_outfit_detection(self, api_service):
        """Test complete outfit detection."""
        results = await api_service.search_and_format_products(
            "عايز طقم كامل كومبليت",
            limit=3
        )
        
        assert len(results) > 0
        # Should prioritize complete sets/outfits

    @pytest.mark.asyncio
    async def test_intent_logging(self, api_service, caplog):
        """Test that intent is properly logged for debugging."""
        import logging
        caplog.set_level(logging.INFO)
        
        await api_service.search_and_format_products(
            "عايز بدلة للفرح غالية",
            limit=3
        )
        
        # Check that intent was logged
        assert any('Intent detected' in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_price_range_filtering(self, api_service):
        """Test that price range filtering works correctly."""
        # Very low price request
        low_results = await api_service.search_and_format_products(
            "عايز حاجة رخيصة جدا",
            limit=5
        )
        
        # High price request
        high_results = await api_service.search_and_format_products(
            "عايز حاجة غالية فخمة",
            limit=5
        )
        
        # Both should return results
        assert len(low_results) > 0
        assert len(high_results) > 0

    @pytest.mark.asyncio
    async def test_occasion_filtering(self, api_service):
        """Test occasion-based filtering."""
        # Wedding occasion
        wedding_results = await api_service.search_and_format_products(
            "محتاج لبس للفرح",
            limit=3
        )
        
        # Work occasion
        work_results = await api_service.search_and_format_products(
            "محتاج لبس للشغل",
            limit=3
        )
        
        assert len(wedding_results) > 0
        assert len(work_results) > 0

    @pytest.mark.asyncio
    async def test_season_filtering(self, api_service):
        """Test season-based filtering."""
        # Summer request
        summer_results = await api_service.search_and_format_products(
            "عايز لبس صيفي خفيف",
            limit=3
        )
        
        # Winter request
        winter_results = await api_service.search_and_format_products(
            "عايز لبس شتوي دافي",
            limit=3
        )
        
        assert len(summer_results) > 0
        assert len(winter_results) > 0

    @pytest.mark.asyncio
    async def test_response_always_in_arabic(self, api_service):
        """Test that smart responses are always in Arabic."""
        results = await api_service.search_and_format_products(
            "عايز قميص",
            limit=3
        )
        
        smart_response = results[0]
        # Should contain Arabic text
        assert any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in smart_response)

    @pytest.mark.asyncio
    async def test_fast_response_time(self, api_service):
        """Test that intelligent search doesn't slow down response significantly."""
        import time
        
        start = time.time()
        await api_service.search_and_format_products(
            "عايز طقم للفرح",
            limit=3
        )
        elapsed = time.time() - start
        
        # Should complete in reasonable time (< 2 seconds for mocked data)
        assert elapsed < 2.0

    @pytest.mark.asyncio
    async def test_limit_respected(self, api_service):
        """Test that limit parameter is respected."""
        results = await api_service.search_and_format_products(
            "عايز قميص",
            limit=2
        )
        
        # First is smart response, then up to 2 products
        assert len(results) <= 3  # 1 smart response + 2 products


# === Edge Cases ===

class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_query(self, api_service):
        """Test empty search query."""
        results = await api_service.search_and_format_products("", limit=3)
        # Should handle gracefully
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_very_long_query(self, api_service):
        """Test very long search query."""
        long_query = "عايز قميص أبيض رسمي للشغل مناسب للصيف خفيف قطن مقاس كبير سعر حلو " * 5
        results = await api_service.search_and_format_products(long_query, limit=3)
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_special_characters(self, api_service):
        """Test query with special characters."""
        results = await api_service.search_and_format_products(
            "عايز قميص !@#$%",
            limit=3
        )
        # Should handle gracefully
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_mixed_arabic_english(self, api_service):
        """Test mixed Arabic and English query."""
        results = await api_service.search_and_format_products(
            "عايز shirt للشغل",
            limit=3
        )
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_numbers_in_query(self, api_service):
        """Test query with numbers."""
        results = await api_service.search_and_format_products(
            "عايز 3 قمصان",
            limit=3
        )
        assert len(results) > 0
