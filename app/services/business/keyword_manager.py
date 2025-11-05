"""
Keyword Manager for BWW Assistant Chatbot
Centralized keyword management and NLP processing
"""

import logging
import unicodedata
from typing import Dict, List, Optional, Tuple, Any
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class KeywordManager:
    """Centralized keyword management"""

    def __init__(self) -> None:
        self.keywords: Dict[str, Dict[str, List[str]]] = {}
        self._initialized = False
        self.logger = logging.getLogger(__name__)

    def initialize(self) -> bool:
        """Initialize keyword manager"""
        try:
            if self._initialized:
                return True

            # Load all keyword categories
            self._load_keyword_categories()

            self._initialized = True
            self.logger.info("Keyword manager initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize keyword manager: {e}")
            return False

    def _load_keyword_categories(self) -> None:
        """Load all keyword categories"""
        # Basic greeting keywords
        self.keywords["greeting"] = {
            "مرحبا": ["مرحبا", "مرحباً", "مرحبا بك", "مرحبا بيك", "أهلا وسهلا", "أهلاً وسهلاً", "مرحبا يا"],
            "هلا": ["هلا", "هلا بك", "هلا بيك", "هلا وسهلا", "هلاً وسهلاً", "هلا يا", "هلا ومرحبا"],
            "السلام": ["السلام", "السلام عليكم", "سلام", "سلام عليكم", "السلام عليك", "وعليكم السلام", "سلام ورحمة"],
            "أهلا": ["أهلا", "أهلاً", "أهلا بك", "أهلا بيك", "أهلا وسهلا", "أهلاً وسهلاً", "أهلا يا"],
            "صباح الخير": ["صباح الخير", "صباح النور", "صباح الفل", "صباح الورد", "صباحك سعيد", "صباح الخير عليك", "صباح الخير بيك"],
            "مساء الخير": ["مساء الخير", "مساء النور", "مساء الفل", "مساء الورد", "مساءك سعيد", "مساء الخير عليك", "مساء الخير بيك"]
        }

        # Help keywords
        self.keywords["help"] = {
            "مساعدة": ["مساعدة", "المساعدة", "ساعدني", "ساعدوني", "أحتاج مساعدة", "أريد مساعدة", "مساعدة من فضلك"],
            "ساعد": ["ساعد", "ساعدني", "ساعدوني", "ساعدني من فضلك", "ساعدني لو سمحت", "ساعدني يا", "ساعدني في"],
            "help": ["help", "support", "assistance", "aid", "guidance", "help me", "can you help"]
        }

        # Product keywords
        self.keywords["products"] = {
            "فستان": ["فستان", "فستان طويل", "فستان قصير", "فستان سهرة", "فستان عمل", "فستان صيفي", "فستان شتوي"],
            "قميص": ["قميص", "قميص نسائي", "قميص قطني", "قميص حرير", "قميص عمل", "قميص رسمي", "قميص كاجوال"],
            "بلوزة": ["بلوزة", "بلوزة نسائية", "بلوزة قطنية", "بلوزة حريرية", "بلوزة عمل", "بلوزة رسمية", "بلوزة كاجوال"],
            "تيشيرت": ["تيشيرت", "تيشيرت نسائي", "تيشيرت قطني", "تيشيرت كاجوال", "تيشيرت صيفي", "تيشيرت مطبوع", "تيشيرت رياضي"],
            "جينز": ["جينز", "بنطلون جينز", "جينز نسائي", "جينز ضيق", "جينز واسع", "جينز قصير", "جينز طويل"],
            "بنطلون": ["بنطلون", "بنطلون نسائي", "بنطلون رسمي", "بنطلون كاجوال", "بنطلون عمل", "بنطلون صيفي", "بنطلون شتوي"],
            "حذاء": ["حذاء", "حذاء نسائي", "حذاء رجالي", "حذاء رياضي", "حذاء رسمي", "حذاء كاجوال", "حذاء صيفي", "حذاء شتوي"],
            "حقيبة": ["حقيبة", "حقيبة يد", "حقيبة كتف", "حقيبة ظهر", "حقيبة نسائية", "حقيبة رجالية", "حقيبة عمل", "حقيبة رسمية"]
        }

        # Price keywords
        self.keywords["price"] = {
            "سعر": ["سعر", "السعر", "بكام", "كم يكلف", "تكلفة", "ثمن", "قيمة", "فلوس", "سعره", "السعر كام"],
            "كم": ["كم", "كام", "إيه السعر", "إزاي السعر", "السعر إيه", "بكام ده", "كم السعر", "السعر كام", "إيه الثمن"],
            "بكام": ["بكام", "بكام", "كم السعر", "السعر كام", "بكام ده", "كم تكلف", "السعر إيه", "إيه السعر", "كم يكلف"],
            "غالي": ["غالي", "غالي أوي", "مكلف", "سعره عالي", "مش رخيص", "سعره كتير", "غالي جداً", "مكلف أوي", "سعره عالي"],
            "رخيص": ["رخيص", "رخيص أوي", "سعره حلو", "مش غالي", "سعره معقول", "زين السعر", "رخيص جداً", "سعره حلو", "مش مكلف"],
            "عرض": ["عرض", "عروض", "خصم", "تخفيض", "سعر خاص", "عرض خاص", "خصم كبير", "عروض خاصة", "تخفيضات", "عروض رائعة"],
            "price": ["price", "cost", "money", "how much", "expensive", "cheap", "discount", "offer", "sale", "budget", "affordable", "reasonable", "value"]
        }

        # Size keywords
        self.keywords["size"] = {
            "مقاس": ["مقاس", "المقاس", "مقاسات", "المقاسات", "إيه المقاس", "مقاس إيه", "مقاس كام", "المقاس إيه", "إيه المقاسات"],
            "حجم": ["حجم", "الحجم", "أحجام", "الأحجام", "إيه الحجم", "حجم إيه", "حجم كام", "الحجم إيه", "إيه الأحجام"],
            "صغير": ["صغير", "صغيرة", "مقاس صغير", "حجم صغير", "صغير أوي", "مش كبير", "صغير جداً", "مقاس صغير", "حجم صغير"],
            "كبير": ["كبير", "كبيرة", "مقاس كبير", "حجم كبير", "كبير أوي", "مش صغير", "كبير جداً", "مقاس كبير", "حجم كبير"],
            "متوسط": ["متوسط", "متوسطة", "مقاس متوسط", "حجم متوسط", "وسط", "وسطاني", "متوسط الحجم", "مقاس متوسط"],
            "XS": ["XS", "اكس صغير", "اكس اس", "صغير جداً", "صغير أوي", "اكس صغير", "اكس اس", "صغير جداً"],
            "S": ["S", "اس", "صغير", "صغيرة", "مقاس صغير", "حجم صغير", "اس", "صغير", "صغيرة"],
            "M": ["M", "ام", "متوسط", "متوسطة", "مقاس متوسط", "حجم متوسط", "ام", "متوسط", "متوسطة"],
            "L": ["L", "ال", "كبير", "كبيرة", "مقاس كبير", "حجم كبير", "ال", "كبير", "كبيرة"],
            "XL": ["XL", "اكس ال", "اكس ال", "كبير جداً", "كبير أوي", "اكس ال", "اكس ال", "كبير جداً"]
        }

        # Location keywords
        self.keywords["location"] = {
            "موقع": ["موقع", "الموقع", "مكان", "المكان", "أين موقعكم", "أين متجركم", "عنوان المتجر"],
            "أين": ["أين", "أين أنتم", "أين متجركم", "أين موقعكم", "أين العنوان", "أين المكان", "أين الفرع"],
            "عنوان": ["عنوان", "العنوان", "عنوان المتجر", "عنوان الفرع", "العنوان كام", "العنوان إيه", "عنوانكم إيه"],
            "محافظة": ["محافظة", "المحافظة", "أي محافظة", "إيه المحافظة", "محافظة إيه", "أي محافظة أنتم", "محافظتكم إيه"],
            "location": ["location", "where", "address", "governorate", "city", "area", "place"]
        }

        # Thank you keywords
        self.keywords["thank"] = {
            "شكرا": ["شكرا", "شكراً", "شكرا لك", "شكراً لك", "شكرا ليك", "شكراً ليك", "شكرا جزيلا"],
            "شكراً": ["شكراً", "شكراً لك", "شكراً ليك", "شكراً جزيلاً", "شكراً كثيراً", "شكراً أوي", "شكراً جداً"],
            "متشكر": ["متشكر", "متشكر أوي", "متشكر جداً", "متشكر ليك", "متشكر لك", "متشكر أوي أوي", "متشكر من القلب"],
            "thank": ["thank", "thanks", "appreciate", "grateful", "thank you", "thanks a lot", "much appreciated"]
        }

        # Goodbye keywords
        self.keywords["goodbye"] = {
            "وداع": ["وداع", "وداعاً", "وداع يا", "وداع بيك", "وداع لك", "وداعاً يا", "وداعاً بيك"],
            "مع السلامة": ["مع السلامة", "مع السلامة يا", "مع السلامة بيك", "مع السلامة لك", "مع السلامة يا", "مع السلامة بيك", "مع السلامة"],
            "باي": ["باي", "باي باي", "باي يا", "باي بيك", "باي لك", "باي باي يا", "باي باي بيك"],
            "bye": ["bye", "goodbye", "see you", "farewell", "take care", "see you later", "good night"]
        }

    def normalize_arabic_text(self, text: str) -> str:
        """Normalize Arabic text by removing diacritics and standardizing characters"""
        try:
            # Remove diacritics
            text = unicodedata.normalize('NFKD', text)
            text = ''.join([c for c in text if not unicodedata.combining(c)])

            # Standardize Arabic characters
            replacements = {
                'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ة': 'ه',
                'ى': 'ي', 'ؤ': 'و', 'ئ': 'ي'
            }

            for old, new in replacements.items():
                text = text.replace(old, new)

            return text.lower().strip()

        except Exception as e:
            self.logger.error(f"Error normalizing Arabic text: {e}")
            return text.lower().strip()

    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        try:
            if len(s1) < len(s2):
                return self.levenshtein_distance(s2, s1)

            if len(s2) == 0:
                return len(s1)

            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row

            return previous_row[-1]

        except Exception as e:
            self.logger.error(f"Error calculating Levenshtein distance: {e}")
            return len(s1) + len(s2)

    def fuzzy_match(self, text: str, keywords: List[str], threshold: float = 0.8) -> Optional[str]:
        """Find fuzzy match for text in keywords list"""
        try:
            normalized_text = self.normalize_arabic_text(text)

            best_match = None
            best_score = 0

            for keyword in keywords:
                normalized_keyword = self.normalize_arabic_text(keyword)

                # Exact match
                if normalized_text == normalized_keyword:
                    return keyword

                # SequenceMatcher ratio
                ratio = SequenceMatcher(None, normalized_text, normalized_keyword).ratio()

                # Levenshtein distance
                distance = self.levenshtein_distance(normalized_text, normalized_keyword)
                max_len = max(len(normalized_text), len(normalized_keyword))
                levenshtein_score = 1 - (distance / max_len) if max_len > 0 else 0

                # Combined score
                combined_score = (ratio + levenshtein_score) / 2

                if combined_score > best_score and combined_score >= threshold:
                    best_score = combined_score
                    best_match = keyword

            return best_match

        except Exception as e:
            self.logger.error(f"Error in fuzzy match: {e}")
            return None

    def detect_category(self, text: str) -> Optional[str]:
        """Detect the category of the input text"""
        try:
            if not self._initialized:
                self.initialize()

            normalized_text = self.normalize_arabic_text(text)

            # Check each category
            for category, keywords_dict in self.keywords.items():
                for _, variations in keywords_dict.items():
                    if self.fuzzy_match(normalized_text, variations, threshold=0.7):
                        return category

            return None

        except Exception as e:
            self.logger.error(f"Error detecting category: {e}")
            return None

    def get_keywords_for_category(self, category: str) -> Dict[str, List[str]]:
        """Get keywords for a specific category"""
        return self.keywords.get(category, {})

    def add_keywords(self, category: str, keywords: Dict[str, List[str]]) -> None:
        """Add keywords to a category"""
        if category not in self.keywords:
            self.keywords[category] = {}

        self.keywords[category].update(keywords)

    def get_all_categories(self) -> List[str]:
        """Get all available categories"""
        return list(self.keywords.keys())

    def search_keywords(self, query: str, category: Optional[str] = None) -> List[Tuple[str, str, float]]:
        """Search for keywords matching a query"""
        try:
            results: List[Tuple[str, str, float]] = []
            categories_to_search = [category] if category else self.keywords.keys()

            for cat in categories_to_search:
                if cat not in self.keywords:
                    continue

                for keyword, variations in self.keywords[cat].items():
                    match = self.fuzzy_match(query, variations, threshold=0.6)
                    if match:
                        score = SequenceMatcher(None, query.lower(), match.lower()).ratio()
                        results.append((cat, keyword, score))

            # Sort by score
            results.sort(key=lambda x: x[2], reverse=True)
            return results

        except Exception as e:
            self.logger.error(f"Error searching keywords: {e}")
            return []

    def get_keyword_stats(self) -> Dict[str, Any]:
        """Get keyword statistics"""
        try:
            stats: Dict[str, Any] = {
                "total_categories": len(self.keywords),
                "categories": {},
                "total_keywords": 0
            }

            for category, keywords_dict in self.keywords.items():
                category_stats: Dict[str, Any] = {
                    "total_keywords": len(keywords_dict),
                    "total_variations": sum(len(variations) for variations in keywords_dict.values())
                }
                stats["categories"][category] = category_stats
                stats["total_keywords"] += category_stats["total_keywords"]

            return stats

        except Exception as e:
            self.logger.error(f"Error getting keyword stats: {e}")
            return {"error": str(e)}


# Global keyword manager instance
keyword_manager = KeywordManager()


def get_keyword_manager() -> KeywordManager:
    """Get the global keyword manager instance"""
    return keyword_manager


def initialize_keywords() -> bool:
    """Initialize keyword manager"""
    return keyword_manager.initialize()


def detect_text_category(text: str) -> Optional[str]:
    """Detect text category"""
    return keyword_manager.detect_category(text)


def fuzzy_match_keywords(text: str, keywords: List[str], threshold: float = 0.8) -> Optional[str]:
    """Fuzzy match keywords"""
    return keyword_manager.fuzzy_match(text, keywords, threshold)
