"""
BWW Store Product Recommendation Engine
Smart recommendations based on customer behavior and preferences
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from collections import Counter

logger = logging.getLogger(__name__)


class ProductRecommender:
    """
    Intelligent product recommendation engine for BWW Store
    
    Features:
    - Customer preference tracking
    - Similar product suggestions
    - Complementary items (outfit matching)
    - Trending products
    - Personalized recommendations based on history
    """
    
    def __init__(self):
        """Initialize the recommendation engine"""
        self.customer_preferences: Dict[str, Dict[str, Any]] = {}
        self._initialized = True
        logger.info("Product Recommender initialized")
    
    async def track_product_interest(
        self, 
        user_id: str, 
        search_query: str, 
        viewed_products: List[Dict[str, Any]]
    ) -> None:
        """
        Track customer product interests
        
        Args:
            user_id: Customer ID
            search_query: Search query used
            viewed_products: List of products shown to customer
        """
        try:
            if user_id not in self.customer_preferences:
                self.customer_preferences[user_id] = {
                    "searches": [],
                    "viewed_categories": [],
                    "viewed_colors": [],
                    "price_range": [],
                    "last_interaction": None
                }
            
            prefs = self.customer_preferences[user_id]
            
            # Track search query
            prefs["searches"].append({
                "query": search_query,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Extract categories and colors from viewed products
            for product in viewed_products:
                if "category" in product:
                    prefs["viewed_categories"].append(product["category"])
                
                if "color" in product:
                    prefs["viewed_colors"].append(product["color"])
                
                if "price" in product:
                    prefs["price_range"].append(float(product["price"]))
            
            prefs["last_interaction"] = datetime.now(timezone.utc).isoformat()
            
            # Keep only last 20 searches
            if len(prefs["searches"]) > 20:
                prefs["searches"] = prefs["searches"][-20:]
            
            # Keep only last 50 category/color views
            if len(prefs["viewed_categories"]) > 50:
                prefs["viewed_categories"] = prefs["viewed_categories"][-50:]
            
            if len(prefs["viewed_colors"]) > 50:
                prefs["viewed_colors"] = prefs["viewed_colors"][-50:]
            
            logger.info(f"Tracked product interest for user {user_id}: {search_query}")
            
        except Exception as e:
            logger.error(f"Error tracking product interest: {e}")
    
    async def get_recommendations(
        self, 
        user_id: str, 
        current_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get personalized product recommendations
        
        Args:
            user_id: Customer ID
            current_context: Current conversation context
        
        Returns:
            Dictionary with recommendations and reasoning
        """
        try:
            if user_id not in self.customer_preferences:
                return {
                    "has_recommendations": False,
                    "message": "لا توجد توصيات حالياً - جرب البحث عن منتجات أولاً! 🛍️"
                }
            
            prefs = self.customer_preferences[user_id]
            recommendations: List[Dict[str, str]] = []
            
            # Initialize Counter variables outside if blocks to avoid "possibly unbound" errors
            category_counts: Optional[Counter[str]] = None
            favorite_category: Optional[str] = None
            color_counts: Optional[Counter[str]] = None
            favorite_color: Optional[str] = None
            
            # Analyze favorite categories
            if prefs["viewed_categories"]:
                category_counts = Counter(prefs["viewed_categories"])
                favorite_category = category_counts.most_common(1)[0][0]
                recommendations.append({
                    "type": "favorite_category",
                    "suggestion": f"منتجات {favorite_category} جديدة وصلت! 🎉",
                    "search_query": favorite_category,
                    "reason": "based_on_browsing_history"
                })
            
            # Analyze favorite colors
            if prefs["viewed_colors"]:
                color_counts = Counter(prefs["viewed_colors"])
                favorite_color = color_counts.most_common(1)[0][0]
                recommendations.append({
                    "type": "favorite_color",
                    "suggestion": f"منتجات {favorite_color} مميزة! 🌈",
                    "search_query": favorite_color,
                    "reason": "based_on_color_preference"
                })
            
            # Price range recommendations
            if prefs["price_range"]:
                avg_price = sum(prefs["price_range"]) / len(prefs["price_range"])
                if avg_price < 500:
                    recommendations.append({
                        "type": "price_match",
                        "suggestion": "عروض وأسعار مناسبة تحت 500 جنيه! 💰",
                        "search_query": "budget friendly",
                        "reason": "based_on_price_preference"
                    })
                elif avg_price > 800:
                    recommendations.append({
                        "type": "price_match",
                        "suggestion": "منتجات مميزة وفاخرة! ✨",
                        "search_query": "premium quality",
                        "reason": "based_on_price_preference"
                    })
            
            # Recent searches
            if prefs["searches"]:
                recent_search = prefs["searches"][-1]["query"]
                recommendations.append({
                    "type": "recent_search",
                    "suggestion": f"منتجات مشابهة لـ '{recent_search}' 🔍",
                    "search_query": recent_search,
                    "reason": "based_on_recent_search"
                })
            
            return {
                "has_recommendations": len(recommendations) > 0,
                "recommendations": recommendations[:3],  # Top 3 recommendations
                "customer_profile": {
                    "total_searches": len(prefs["searches"]),
                    "favorite_category": category_counts.most_common(1)[0][0] if category_counts and prefs["viewed_categories"] else None,
                    "favorite_color": color_counts.most_common(1)[0][0] if color_counts and prefs["viewed_colors"] else None,
                    "avg_price_range": sum(prefs["price_range"]) / len(prefs["price_range"]) if prefs["price_range"] else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return {
                "has_recommendations": False,
                "error": str(e)
            }
    
    async def get_complementary_items(
        self, 
        product_category: str
    ) -> List[str]:
        """
        Get complementary item suggestions (outfit matching)
        
        Args:
            product_category: Category of current product
        
        Returns:
            List of complementary categories
        """
        # Egyptian market outfit matching rules
        complementary_rules = {
            "فستان": ["حذاء", "شنطة", "إكسسوارات", "حجاب"],
            "بنطلون": ["بلوزة", "تيشرت", "جاكيت", "حذاء"],
            "بلوزة": ["بنطلون", "تنورة", "جاكيت"],
            "تنورة": ["بلوزة", "تيشرت", "حذاء"],
            "جاكيت": ["بنطلون", "تنورة", "بلوزة"],
            "حذاء": ["شنطة", "إكسسوارات"],
            "عباية": ["حجاب", "شنطة", "حذاء"],
            "حجاب": ["بلوزة", "فستان", "عباية"]
        }
        
        return complementary_rules.get(product_category, [])
    
    async def suggest_outfit_combinations(
        self, 
        viewed_product: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest complete outfit combinations
        
        Args:
            viewed_product: Product customer is viewing
        
        Returns:
            Dictionary with outfit suggestions
        """
        try:
            category = viewed_product.get("category", "")
            color = viewed_product.get("color", "")
            
            complementary = await self.get_complementary_items(category)
            
            if not complementary:
                return {
                    "has_suggestions": False
                }
            
            suggestions: List[Dict[str, str]] = []
            
            # Suggest matching items
            for item in complementary[:2]:  # Top 2 matches
                suggestions.append({
                    "item": item,
                    "search_query": f"{item} {color}" if color else item,
                    "message": f"يمكنك تنسيقها مع {item}! 👗✨"
                })
            
            return {
                "has_suggestions": True,
                "suggestions": suggestions,
                "message": f"نصيحة تنسيق: {category} يليق معاها:",
                "complementary_items": complementary
            }
            
        except Exception as e:
            logger.error(f"Error suggesting outfit combinations: {e}")
            return {"has_suggestions": False, "error": str(e)}
    
    async def generate_smart_response(
        self, 
        user_id: str, 
        search_query: str,
        products_found: List[Dict[str, Any]]
    ) -> str:
        """
        Generate smart response with recommendations
        
        Args:
            user_id: Customer ID
            search_query: Customer search query
            products_found: Products found in search
        
        Returns:
            Smart response message in Arabic
        """
        try:
            # Track interest first
            await self.track_product_interest(user_id, search_query, products_found)
            
            # Get recommendations
            recommendations = await self.get_recommendations(user_id)
            
            response_parts: List[str] = []
            
            # Main results message
            if products_found:
                response_parts.append(f"تم العثور على {len(products_found)} منتج مناسب! 🎉")
            
            # Add recommendations if available
            if recommendations.get("has_recommendations"):
                recs = recommendations["recommendations"]
                if recs:
                    response_parts.append("\n\n💡 توصيات لك:")
                    for rec in recs[:2]:  # Top 2
                        response_parts.append(f"• {rec['suggestion']}")
            
            # Suggest outfit combinations for first product
            if products_found and len(products_found) > 0:
                outfit_suggestions = await self.suggest_outfit_combinations(products_found[0])
                if outfit_suggestions.get("has_suggestions"):
                    response_parts.append(f"\n\n{outfit_suggestions['message']}")
                    for suggestion in outfit_suggestions["suggestions"][:2]:
                        response_parts.append(f"• {suggestion['message']}")
            
            return "\n".join(response_parts) if response_parts else "تم إرسال المنتجات!"
            
        except Exception as e:
            logger.error(f"Error generating smart response: {e}")
            return f"تم العثور على {len(products_found)} منتج!"
    
    def get_customer_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get customer preferences for analytics"""
        return self.customer_preferences.get(user_id)
    
    def clear_customer_data(self, user_id: str) -> bool:
        """Clear customer preference data (GDPR compliance)"""
        try:
            if user_id in self.customer_preferences:
                del self.customer_preferences[user_id]
                logger.info(f"Cleared preferences for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing customer data: {e}")
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status for health monitoring"""
        return {
            "service": "ProductRecommender",
            "status": "operational",
            "initialized": self._initialized,
            "tracked_customers": len(self.customer_preferences),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
