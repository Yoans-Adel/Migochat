"""
BWW Store Language Enhancement Tests
====================================

Simple tests to validate Egyptian dialect improvements.
"""

import pytest
from bww_store.constants import EGYPTIAN_CORRECTIONS, CLOTHING_KEYWORDS_AR


class TestEgyptianCorrections:
    """Test Egyptian corrections dictionary"""
    
    def test_corrections_count(self):
        """Test that we have comprehensive corrections"""
        assert len(EGYPTIAN_CORRECTIONS) > 200, "Should have 200+ Egyptian corrections"
        print(f"✓ {len(EGYPTIAN_CORRECTIONS)} Egyptian corrections loaded")
    
    def test_want_expressions(self):
        """Test 'want' expression variations"""
        want_words = ['عايز', 'عاوز', 'عايزة', 'عاوزة', 'محتاج', 'نفسي', 'ياريت', 'بدور على']
        
        for word in want_words:
            assert word in EGYPTIAN_CORRECTIONS, f"Missing want expression: {word}"
        
        print(f"✓ All {len(want_words)} want expressions found")
    
    def test_quality_adjectives(self):
        """Test quality adjectives"""
        quality_words = ['حلو', 'جميل', 'جامد', 'شيك', 'ظريف', 'تمام']
        
        for word in quality_words:
            assert word in EGYPTIAN_CORRECTIONS, f"Missing quality word: {word}"
        
        print(f"✓ All {len(quality_words)} quality adjectives found")
    
    def test_clothing_terms(self):
        """Test clothing term corrections"""
        clothing_words = ['تيشرت', 'بنطلون', 'جاكيتة', 'قميس', 'كوتشي', 'شنطة']
        
        for word in clothing_words:
            assert word in EGYPTIAN_CORRECTIONS, f"Missing clothing term: {word}"
        
        print(f"✓ All {len(clothing_words)} clothing terms found")
    
    def test_color_variations(self):
        """Test color variations"""
        colors = ['أحمر', 'حمراء', 'أسود', 'سوداء', 'أبيض', 'بيضاء', 'أزرق', 'زرقاء']
        
        for color in colors:
            assert color in EGYPTIAN_CORRECTIONS, f"Missing color: {color}"
        
        print(f"✓ All {len(colors)} color variations found")
    
    def test_demonstratives(self):
        """Test demonstratives"""
        demos = ['ده', 'دي', 'دول', 'كده', 'كدا', 'زي كده']
        
        for demo in demos:
            assert demo in EGYPTIAN_CORRECTIONS, f"Missing demonstrative: {demo}"
        
        print(f"✓ All {len(demos)} demonstratives found")
    
    def test_negation(self):
        """Test negation words"""
        negations = ['مش', 'ماش', 'مافيش', 'مفيش', 'فيش']
        
        for neg in negations:
            assert neg in EGYPTIAN_CORRECTIONS, f"Missing negation: {neg}"
        
        print(f"✓ All {len(negations)} negation words found")


class TestClothingKeywords:
    """Test clothing keywords dictionary"""
    
    def test_keywords_count(self):
        """Test that we have comprehensive keywords"""
        assert len(CLOTHING_KEYWORDS_AR) >= 10, "Should have 10+ clothing categories"
        print(f"✓ {len(CLOTHING_KEYWORDS_AR)} clothing categories loaded")
    
    def test_shirt_variations(self):
        """Test shirt variations"""
        assert 'قميص' in CLOTHING_KEYWORDS_AR, "Should have shirt category"
        
        shirt_variations = CLOTHING_KEYWORDS_AR['قميص']
        expected_terms = ['قميص', 'قميس', 'تيشرت', 'تيشيرت', 'بلوزة', 'توب']
        
        for term in expected_terms:
            assert term in shirt_variations, f"Missing shirt variation: {term}"
        
        print(f"✓ Shirt has {len(shirt_variations)} variations")
    
    def test_pants_variations(self):
        """Test pants variations"""
        assert 'بنطال' in CLOTHING_KEYWORDS_AR, "Should have pants category"
        
        pants_variations = CLOTHING_KEYWORDS_AR['بنطال']
        expected_terms = ['بنطال', 'بنطلون', 'جينز', 'جينس', 'شورت']
        
        for term in expected_terms:
            assert term in pants_variations, f"Missing pants variation: {term}"
        
        print(f"✓ Pants has {len(pants_variations)} variations")
    
    def test_jacket_variations(self):
        """Test jacket variations"""
        assert 'جاكيت' in CLOTHING_KEYWORDS_AR, "Should have jacket category"
        
        jacket_variations = CLOTHING_KEYWORDS_AR['جاكيت']
        expected_terms = ['جاكيت', 'جاكيتة', 'ستره', 'كوت', 'بليزر']
        
        for term in expected_terms:
            assert term in jacket_variations, f"Missing jacket variation: {term}"
        
        print(f"✓ Jacket has {len(jacket_variations)} variations")


class TestLanguageCoverage:
    """Test overall language coverage"""
    
    def test_egyptian_dialect_coverage(self):
        """Test Egyptian dialect coverage"""
        # Count different categories
        want_count = sum(1 for k in EGYPTIAN_CORRECTIONS if k in [
            'عايز', 'عاوز', 'محتاج', 'نفسي', 'ياريت', 'بدور', 'عاوزة', 'عايزة'
        ])
        
        quality_count = sum(1 for k in EGYPTIAN_CORRECTIONS if k in [
            'حلو', 'حلوة', 'جميل', 'جميلة', 'جامد', 'جامدة', 'شيك', 'ظريف', 'تمام'
        ])
        
        clothing_count = sum(1 for k in EGYPTIAN_CORRECTIONS if k in [
            'تيشرت', 'تيشيرت', 'بنطلون', 'جاكيتة', 'جاكت', 'قميس', 'كوتشي'
        ])
        
        color_count = sum(1 for k in EGYPTIAN_CORRECTIONS if k in [
            'أحمر', 'حمراء', 'حمر', 'أسود', 'سوداء', 'سود', 'أبيض', 'بيضاء'
        ])
        
        print(f"✓ Want expressions: {want_count}/8")
        print(f"✓ Quality adjectives: {quality_count}/9")
        print(f"✓ Clothing terms: {clothing_count}/7")
        print(f"✓ Color variations: {color_count}/8")
        
        assert want_count >= 6, "Should have most want expressions"
        assert quality_count >= 6, "Should have most quality adjectives"
        assert clothing_count >= 5, "Should have most clothing terms"
        assert color_count >= 6, "Should have most color variations"
    
    def test_no_duplicate_keys(self):
        """Test that there are no duplicate keys in corrections"""
        corrections_list = list(EGYPTIAN_CORRECTIONS.keys())
        unique_corrections = set(corrections_list)
        
        assert len(corrections_list) == len(unique_corrections), \
            "Found duplicate keys in EGYPTIAN_CORRECTIONS"
        
        print(f"✓ No duplicates in {len(corrections_list)} corrections")
    
    def test_corrections_are_strings(self):
        """Test that all corrections are proper strings"""
        for key, value in EGYPTIAN_CORRECTIONS.items():
            assert isinstance(key, str), f"Key {key} is not a string"
            assert isinstance(value, str), f"Value {value} is not a string"
            assert len(key) > 0, f"Empty key found"
        
        print(f"✓ All {len(EGYPTIAN_CORRECTIONS)} corrections are valid strings")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-q'])
