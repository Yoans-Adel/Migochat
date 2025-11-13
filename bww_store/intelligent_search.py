"""
BWW Store Intelligent Search Engine
===================================

Advanced search with context understanding, fuzzy matching, and intelligent filtering.
This module makes BWW Store search truly intelligent like a smart assistant.

Features:
    - Fuzzy matching with Levenshtein distance
    - Context-aware search (outfit combinations, occasions)
    - Price range detection and filtering
    - Occasion detection (wedding, work, party, etc.)
    - Season detection (summer, winter)
    - Smart response generation

Author: BWW Store AI Team
Date: November 2025
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import re


# ============================================================================
# Enums for Search Intelligence
# ============================================================================

class PriceRange(Enum):
    """Price range categories"""
    VERY_LOW = "very_low"      # Very cheap
    LOW = "low"                # Cheap
    MEDIUM = "medium"          # Affordable/Normal
    HIGH = "high"              # Expensive
    VERY_HIGH = "very_high"    # Very expensive


class Occasion(Enum):
    """Occasion/Event types"""
    WEDDING = "wedding"        # فرح، زفاف، عرس
    WORK = "work"              # شغل، عمل، مكتب
    PARTY = "party"            # حفلة، سهرة
    CASUAL = "casual"          # يومي، كاجوال
    SPORTS = "sports"          # رياضة، جيم
    FORMAL = "formal"          # رسمي، فورمال
    BEACH = "beach"            # بحر، شاطئ
    HOME = "home"              # بيت، منزل
    SCHOOL = "school"          # مدرسة، جامعة


class Season(Enum):
    """Season types"""
    SUMMER = "summer"          # صيف، صيفي
    WINTER = "winter"          # شتاء، شتوي
    SPRING = "spring"          # ربيع، ربيعي
    AUTUMN = "autumn"          # خريف، خريفي
    ALL_SEASON = "all_season"  # كل الفصول


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class SearchIntent:
    """Detected search intent from query"""
    # Basic
    query: str
    cleaned_query: str
    
    # Detected attributes
    price_range: Optional[PriceRange] = None
    occasion: Optional[Occasion] = None
    season: Optional[Season] = None
    
    # Item details
    item_types: List[str] = None
    colors: List[str] = None
    gender: Optional[str] = None
    
    # Preferences
    wants_complete_outfit: bool = False
    quality_preference: Optional[str] = None  # حلو، جميل، etc.
    
    # Extracted keywords
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.item_types is None:
            self.item_types = []
        if self.colors is None:
            self.colors = []
        if self.keywords is None:
            self.keywords = []


# ============================================================================
# Fuzzy Matching Engine
# ============================================================================

class FuzzyMatcher:
    """
    Fuzzy string matching using Levenshtein distance.
    Handles typos and spelling variations.
    """
    
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Edit distance (number of operations needed)
        """
        if len(s1) < len(s2):
            return FuzzyMatcher.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def similarity_score(s1: str, s2: str) -> float:
        """
        Calculate similarity score (0-1) between two strings.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Similarity score (1.0 = identical, 0.0 = completely different)
        """
        distance = FuzzyMatcher.levenshtein_distance(s1.lower(), s2.lower())
        max_len = max(len(s1), len(s2))
        
        if max_len == 0:
            return 1.0
        
        return 1.0 - (distance / max_len)
    
    @staticmethod
    def find_best_match(query: str, candidates: List[str], threshold: float = 0.7) -> Optional[str]:
        """
        Find best matching string from candidates.
        
        Args:
            query: Query string
            candidates: List of candidate strings
            threshold: Minimum similarity threshold (0-1)
            
        Returns:
            Best matching candidate or None
        """
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            score = FuzzyMatcher.similarity_score(query, candidate)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate
        
        return best_match
    
    @staticmethod
    def fuzzy_search(query: str, text: str, threshold: float = 0.7) -> bool:
        """
        Check if query fuzzy matches anywhere in text.
        
        Args:
            query: Query string
            text: Text to search in
            threshold: Minimum similarity threshold
            
        Returns:
            True if fuzzy match found
        """
        query = query.lower()
        text = text.lower()
        
        # Exact match first
        if query in text:
            return True
        
        # Split text into words and check each
        words = text.split()
        for word in words:
            if FuzzyMatcher.similarity_score(query, word) >= threshold:
                return True
        
        return False


# ============================================================================
# Price Range Detector
# ============================================================================

class PriceDetector:
    """Detects price preferences from query"""
    
    # Price keywords mapping
    PRICE_KEYWORDS: Dict[PriceRange, List[str]] = {
        PriceRange.VERY_LOW: [
            'ببلاش', 'رخيص جدا', 'رخيص قوي', 'سعر قليل جدا'
        ],
        PriceRange.LOW: [
            'رخيص', 'رخيصة', 'سعر قليل', 'مش غالي', 'مش غالية',
            'مش غالى', 'سعر حلو', 'سعر كويس', 'مناسب', 'في الميزانية'
        ],
        PriceRange.MEDIUM: [
            'عادي', 'متوسط', 'متوسطة', 'سعر عادي', 'سعر متوسط'
        ],
        PriceRange.HIGH: [
            'غالي', 'غالية', 'غالى', 'مكلف', 'مكلفة', 'سعر عالي'
        ],
        PriceRange.VERY_HIGH: [
            'غالي جدا', 'غالي قوي', 'مكلف جدا', 'راقي', 'فخم', 'لوكس'
        ]
    }
    
    @staticmethod
    def detect(query: str) -> Optional[PriceRange]:
        """
        Detect price range from query.
        
        Args:
            query: Search query
            
        Returns:
            Detected price range or None
        """
        query_lower = query.lower()
        
        # Check each price range
        for price_range, keywords in PriceDetector.PRICE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return price_range
        
        return None


# ============================================================================
# Occasion Detector
# ============================================================================

class OccasionDetector:
    """Detects occasion/event from query"""
    
    # Occasion keywords mapping
    OCCASION_KEYWORDS: Dict[Occasion, List[str]] = {
        Occasion.WEDDING: [
            'فرح', 'فرحة', 'زفاف', 'عرس', 'جواز', 'للفرح', 'للزفاف'
        ],
        Occasion.WORK: [
            'شغل', 'عمل', 'مكتب', 'أوفيس', 'office', 'للشغل', 'للعمل',
            'للمكتب', 'وظيفة', 'انترفيو', 'مقابلة'
        ],
        Occasion.PARTY: [
            'حفلة', 'حفل', 'سهرة', 'بارتي', 'party', 'للحفلة', 'للسهرة',
            'مناسبة', 'احتفال'
        ],
        Occasion.CASUAL: [
            'يومي', 'يومية', 'كاجوال', 'كاجول', 'casual', 'عادي',
            'للخروج', 'للنزول', 'للتمشية'
        ],
        Occasion.SPORTS: [
            'رياضة', 'رياضي', 'رياضية', 'جيم', 'gym', 'تمرين', 'فيتنس',
            'fitness', 'ران', 'run', 'للجيم', 'للرياضة', 'للتمرين'
        ],
        Occasion.FORMAL: [
            'رسمي', 'رسمية', 'فورمال', 'formal', 'أنيق', 'أنيقة',
            'بيزنس', 'business', 'كلاسيك', 'classic'
        ],
        Occasion.BEACH: [
            'بحر', 'شاطئ', 'بيتش', 'beach', 'للبحر', 'للشاطئ',
            'مصيف', 'الساحل'
        ],
        Occasion.HOME: [
            'بيت', 'منزل', 'للبيت', 'للمنزل', 'للنوم', 'نوم',
            'بيجاما', 'بيجامة', 'جلابية', 'جلابيه'
        ],
        Occasion.SCHOOL: [
            'مدرسة', 'جامعة', 'كلية', 'للمدرسة', 'للجامعة', 'للكلية',
            'دراسة', 'محاضرة'
        ]
    }
    
    @staticmethod
    def detect(query: str) -> Optional[Occasion]:
        """
        Detect occasion from query.
        
        Args:
            query: Search query
            
        Returns:
            Detected occasion or None
        """
        query_lower = query.lower()
        
        # Check each occasion
        for occasion, keywords in OccasionDetector.OCCASION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return occasion
        
        return None


# ============================================================================
# Season Detector
# ============================================================================

class SeasonDetector:
    """Detects season/weather preference from query"""
    
    # Season keywords mapping
    SEASON_KEYWORDS: Dict[Season, List[str]] = {
        Season.SUMMER: [
            'صيف', 'صيفي', 'صيفية', 'حر', 'خفيف', 'خفيفة', 'قطن', 'قطني',
            'summer', 'للصيف', 'للحر', 'بارد', 'cool'
        ],
        Season.WINTER: [
            'شتاء', 'شتوي', 'شتوية', 'برد', 'دافي', 'دافئ', 'دافئة', 'ثقيل',
            'صوف', 'صوفي', 'winter', 'للشتاء', 'للبرد', 'warm', 'فرو'
        ],
        Season.SPRING: [
            'ربيع', 'ربيعي', 'ربيعية', 'spring', 'للربيع'
        ],
        Season.AUTUMN: [
            'خريف', 'خريفي', 'خريفية', 'autumn', 'fall', 'للخريف'
        ]
    }
    
    @staticmethod
    def detect(query: str) -> Optional[Season]:
        """
        Detect season from query.
        
        Args:
            query: Search query
            
        Returns:
            Detected season or None
        """
        query_lower = query.lower()
        
        # Check each season
        for season, keywords in SeasonDetector.SEASON_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return season
        
        return Season.ALL_SEASON


# ============================================================================
# Context Analyzer
# ============================================================================

class ContextAnalyzer:
    """
    Analyzes query context to understand user intent.
    Detects complete outfit requests, combinations, etc.
    """
    
    # Complete outfit keywords
    COMPLETE_OUTFIT_KEYWORDS = [
        'طقم كامل', 'طقم متكامل', 'كومبليت', 'complete', 'انسامبل',
        'ensemble', 'لبس كامل', 'outfit', 'طقم', 'سيت', 'set',
        'حاجة كاملة', 'كامل من', 'لبس كومبليت'  # Added for better detection
    ]
    
    # Quality preference keywords
    QUALITY_KEYWORDS = {
        'excellent': ['جامد', 'ممتاز', 'رائع', 'خرافي', 'top', 'best', 
                     'جميلة قوي', 'جميل قوي', 'حلوة جدا', 'حلو جدا'],  # Added "قوي" variations
        'very_good': ['حلو قوي', 'جميل جدا', 'تمام التمام', 'شيك جدا', 'كويس جدا'],
        'good': ['حلو', 'جميل', 'كويس', 'شيك', 'ظريف', 'تمام', 'nice', 'good', 'جميلة', 'حلوة'],
        'acceptable': ['عادي', 'ok', 'ماشي', 'مقبول']
    }
    
    @staticmethod
    def wants_complete_outfit(query: str) -> bool:
        """Check if user wants a complete outfit"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in ContextAnalyzer.COMPLETE_OUTFIT_KEYWORDS)
    
    @staticmethod
    def detect_quality_preference(query: str) -> Optional[str]:
        """Detect quality preference from query"""
        query_lower = query.lower()
        
        for quality, keywords in ContextAnalyzer.QUALITY_KEYWORDS.items():
            if any(keyword in query_lower for keyword in keywords):
                return quality
        
        return None
    
    @staticmethod
    def extract_item_types(query: str, clothing_keywords: Dict[str, List[str]]) -> List[str]:
        """
        Extract clothing item types from query.
        
        Args:
            query: Search query
            clothing_keywords: Dictionary of clothing keywords
            
        Returns:
            List of detected item types
        """
        query_lower = query.lower()
        detected_items = []
        
        for item_type, variations in clothing_keywords.items():
            for variation in variations:
                if variation in query_lower:
                    if item_type not in detected_items:
                        detected_items.append(item_type)
                    break
        
        return detected_items


# ============================================================================
# Intelligent Search Engine
# ============================================================================

class IntelligentSearchEngine:
    """
    Main intelligent search engine combining all detectors.
    Provides context-aware, fuzzy-matched, intelligent search.
    """
    
    def __init__(self, clothing_keywords: Dict[str, List[str]] = None):
        """
        Initialize intelligent search engine.
        
        Args:
            clothing_keywords: Dictionary of clothing keywords
        """
        self.clothing_keywords = clothing_keywords or {}
        self.fuzzy_matcher = FuzzyMatcher()
        self.price_detector = PriceDetector()
        self.occasion_detector = OccasionDetector()
        self.season_detector = SeasonDetector()
        self.context_analyzer = ContextAnalyzer()
    
    def analyze_query(self, query: str) -> SearchIntent:
        """
        Analyze query and extract all intent information.
        
        Args:
            query: User search query
            
        Returns:
            SearchIntent object with all detected information
        """
        # Clean query (will be done by Egyptian corrections in actual search)
        cleaned_query = query.strip()
        
        # Detect all attributes
        intent = SearchIntent(
            query=query,
            cleaned_query=cleaned_query,
            price_range=self.price_detector.detect(query),
            occasion=self.occasion_detector.detect(query),
            season=self.season_detector.detect(query),
            item_types=self.context_analyzer.extract_item_types(query, self.clothing_keywords),
            wants_complete_outfit=self.context_analyzer.wants_complete_outfit(query),
            quality_preference=self.context_analyzer.detect_quality_preference(query),
        )
        
        return intent
    
    def generate_search_filters(self, intent: SearchIntent) -> Dict[str, Any]:
        """
        Generate search filters based on detected intent.
        
        Args:
            intent: Detected search intent
            
        Returns:
            Dictionary of search filters
        """
        filters = {}
        
        if intent.price_range:
            filters['price_range'] = intent.price_range.value
        
        if intent.occasion:
            filters['occasion'] = intent.occasion.value
        
        if intent.season:
            filters['season'] = intent.season.value
        
        if intent.item_types:
            filters['item_types'] = intent.item_types
        
        if intent.wants_complete_outfit:
            filters['complete_outfit'] = True
        
        return filters
    
    def generate_smart_response(self, intent: SearchIntent, results_count: int) -> str:
        """
        Generate intelligent response based on intent and results.
        
        Args:
            intent: Detected search intent
            results_count: Number of results found
            
        Returns:
            Smart response message in Arabic
        """
        if results_count == 0:
            return self._generate_no_results_response(intent)
        
        response_parts = []
        
        # Greeting based on quality preference
        if intent.quality_preference == 'excellent':
            response_parts.append("لقيتلك حاجات جامدة جدًا")
        elif intent.quality_preference in ['very_good', 'good']:
            response_parts.append("لقيتلك حاجات حلوة")
        else:
            response_parts.append(f"لقيتلك {results_count} منتج")
        
        # Add context info
        if intent.occasion:
            occasion_text = self._get_occasion_text(intent.occasion)
            response_parts.append(f"مناسبة {occasion_text}")
        
        if intent.season:
            season_text = self._get_season_text(intent.season)
            response_parts.append(f"{season_text}")
        
        if intent.wants_complete_outfit:
            response_parts.append("- طقم كامل")
        
        return " ".join(response_parts) + " 👔✨"
    
    def _generate_no_results_response(self, intent: SearchIntent) -> str:
        """Generate response when no results found"""
        suggestions = []
        
        if intent.price_range == PriceRange.VERY_LOW:
            suggestions.append("جرب تدور على حاجات 'مناسبة' بدل 'رخيص جدا'")
        
        if intent.item_types:
            suggestions.append(f"جرب تدور بدون تحديد نوع ({', '.join(intent.item_types)})")
        
        if suggestions:
            return "معلش، مافيش نتائج. " + " أو ".join(suggestions)
        
        return "معلش، مافيش نتائج دلوقتي. جرب تدور بكلمات تانية 🔍"
    
    def _get_occasion_text(self, occasion: Occasion) -> str:
        """Get Arabic text for occasion"""
        occasion_map = {
            Occasion.WEDDING: "للفرح",
            Occasion.WORK: "للشغل",
            Occasion.PARTY: "للحفلات",
            Occasion.CASUAL: "يومي",
            Occasion.SPORTS: "رياضي",
            Occasion.FORMAL: "رسمي",
            Occasion.BEACH: "للبحر",
            Occasion.HOME: "للبيت",
            Occasion.SCHOOL: "للمدرسة"
        }
        return occasion_map.get(occasion, "")
    
    def _get_season_text(self, season: Season) -> str:
        """Get Arabic text for season"""
        season_map = {
            Season.SUMMER: "صيفي",
            Season.WINTER: "شتوي",
            Season.SPRING: "ربيعي",
            Season.AUTUMN: "خريفي",
            Season.ALL_SEASON: "لكل الفصول"
        }
        return season_map.get(season, "")


# ============================================================================
# Export
# ============================================================================

__all__ = [
    'IntelligentSearchEngine',
    'FuzzyMatcher',
    'PriceDetector',
    'OccasionDetector',
    'SeasonDetector',
    'ContextAnalyzer',
    'SearchIntent',
    'PriceRange',
    'Occasion',
    'Season',
]
