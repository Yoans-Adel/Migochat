"""
New Professional Message Handler
Completely independent implementation using the new architecture
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Any

from app.services.core.base_service import MessageService, ServiceHealth
from app.services.core.interfaces import ServiceStatus
from app.services.ai.ai_service import AIService
from app.services.messaging.messenger_service import MessengerService
from app.services.messaging.whatsapp_service import WhatsAppService
from database import get_db_session, User

logger = logging.getLogger(__name__)

# Import BWW Store Integration
bww_store_available = False
BWWStoreAPIService = None

try:
    from bww_store import BWWStoreAPIService
    bww_store_available = True
    logger.info("BWW Store integration loaded in Message Handler")
except ImportError:
    logger.warning("BWW Store integration not available in Message Handler")

# Import Product Recommender
try:
    from app.services.ai.product_recommender import ProductRecommender
    recommender_available = True
    logger.info("Product Recommender loaded in Message Handler")
except ImportError:
    recommender_available = False
    logger.warning("Product Recommender not available in Message Handler")


class MessageHandler(MessageService):
    """Message handler using the new architecture"""

    def __init__(self) -> None:
        super().__init__()
        self.platform = "multi"
        self.ai_service = AIService()
        self.messenger_service = MessengerService()
        self.whatsapp_service = WhatsAppService()
        
        # Initialize BWW Store if available
        self.bww_store = None
        if bww_store_available and BWWStoreAPIService:
            try:
                self.bww_store = BWWStoreAPIService(language="ar")
                logger.info("BWW Store service initialized in Message Handler")
            except Exception as e:
                logger.warning(f"Failed to initialize BWW Store: {e}")
        
        # Initialize Product Recommender if available
        self.product_recommender = None
        if recommender_available:
            try:
                from app.services.ai.product_recommender import ProductRecommender
                self.product_recommender = ProductRecommender()
                logger.info("Product Recommender initialized in Message Handler")
            except Exception as e:
                logger.warning(f"Failed to initialize Product Recommender: {e}")
        
        self._initialized = False

    def _do_initialize(self) -> bool:
        """Initialize all services"""
        try:
            # Database accessed directly via app.database module
            self.ai_service.initialize()
            self.messenger_service.initialize()
            self.whatsapp_service.initialize()
            self._initialized = True
            logger.info("Professional Message Handler initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Professional Message Handler: {e}")
            return False

    async def _process_message_impl(self, message_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Process incoming message"""
        try:
            # Extract message details
            user_id = message_data.get("user_id")
            message_text = message_data.get("text", "")

            # Validate user_id
            if not user_id:
                logger.error("Missing user_id in message_data")
                return {"success": False, "error": "Missing user_id"}

            logger.info(f"Processing {platform} message from user {user_id}: {message_text}")

            # Get or create user
            user = await self._get_or_create_user(str(user_id), platform)
            if not user:
                return {"success": False, "error": "Failed to get or create user"}

            # Check for recommendations request
            if self.product_recommender and any(keyword in message_text.lower() for keyword in ["توصيات", "اقتراحات", "recommendations", "suggest"]):
                try:
                    recommendations = await self.product_recommender.get_recommendations(str(user_id), message_text)
                    
                    if recommendations.get("has_recommendations"):
                        response_parts = ["💡 توصيات مخصصة لك:\n"]
                        for rec in recommendations["recommendations"][:3]:
                            response_parts.append(f"• {rec['suggestion']}")
                        
                        ai_response = "\n".join(response_parts)
                        
                        # Optionally search for recommended products
                        if recommendations["recommendations"]:
                            first_rec = recommendations["recommendations"][0]
                            search_query = first_rec.get("search_query", "")
                            if search_query and self.bww_store:
                                product_results = await self.bww_store.search_and_format_products(
                                    search_text=search_query,
                                    limit=3,
                                    language="ar"
                                )
                                if product_results and platform == "facebook":
                                    await self._send_product_cards(str(user_id), product_results, platform)
                    else:
                        ai_response = recommendations.get("message", "ابحث عن منتجات أولاً لنقدم لك توصيات مخصصة! 🛍️")
                    
                    response_sent = await self._send_message_impl(str(user_id), ai_response, platform)
                    return {
                        "success": True,
                        "user_id": user_id,
                        "response": ai_response,
                        "response_sent": response_sent,
                        "platform": platform,
                        "type": "recommendations"
                    }
                except Exception as rec_error:
                    logger.error(f"Error handling recommendations request: {rec_error}")

            # Check if message is product-related query
            product_query_detected = await self._detect_product_query(message_text)
            
            ai_response = None
            product_results = None
            
            if product_query_detected and self.bww_store:
                # Handle product query with BWW Store
                try:
                    logger.info(f"Product query detected: {message_text}")
                    product_results = await self.bww_store.search_and_format_products(
                        search_text=message_text,
                        limit=3,
                        language="ar"
                    )
                    
                    if product_results:
                        # Generate smart response with recommendations
                        if self.product_recommender:
                            try:
                                # Convert product results to dict format for tracking
                                products_dict = []
                                for product_str in product_results:
                                    # Extract basic info from formatted product string
                                    products_dict.append({
                                        "category": message_text,
                                        "search_query": message_text
                                    })
                                
                                # Get smart response with recommendations
                                ai_response = await self.product_recommender.generate_smart_response(
                                    user_id=str(user_id),
                                    search_query=message_text,
                                    products_found=products_dict
                                )
                            except Exception as rec_error:
                                logger.error(f"Error getting recommendations: {rec_error}")
                                ai_response = f"تم العثور على {len(product_results)} منتج"
                        else:
                            ai_response = f"تم العثور على {len(product_results)} منتج"
                        
                        # Send product cards via Messenger
                        if platform == "facebook" and product_results:
                            await self._send_product_cards(str(user_id), product_results, platform)
                        else:
                            # For WhatsApp or if no cards, send text
                            ai_response = "\n\n".join(product_results)
                    else:
                        ai_response = "عذراً، لم أتمكن من العثور على منتجات مطابقة"
                        
                except Exception as e:
                    logger.error(f"Error searching BWW Store: {e}")
                    # Fallback to AI response
                    ai_response = self.ai_service.generate_response(message_text, context={"user": user})
            else:
                # Generate AI response (sync method)
                ai_response = self.ai_service.generate_response(message_text, context={"user": user})

            # Send response back if not already sent
            response_sent = False
            if ai_response and not product_results:
                response_sent = await self._send_message_impl(str(user_id), ai_response, platform)

            return {
                "success": True,
                "user_id": user_id,
                "response": ai_response,
                "product_results": len(product_results) if product_results else 0,
                "response_sent": response_sent or bool(product_results),
                "platform": platform
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {"success": False, "error": str(e)}

    async def _send_message_impl(self, user_id: str, message: str, platform: str) -> bool:
        """Send message to user"""
        try:
            if platform == "facebook":
                response = self.messenger_service.send_message(user_id, message)
                return bool(response)
            elif platform == "whatsapp":
                response = self.whatsapp_service.send_message(user_id, message)
                return bool(response)
            else:
                logger.warning(f"Unknown platform: {platform}")
                return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    async def _get_or_create_user(self, user_id: str, platform: str) -> Optional[User]:
        """Get existing user or create new one - Thread-safe implementation"""
        try:
            from database.context import get_db_session_with_commit
            from sqlalchemy.exc import IntegrityError

            user_id_pk: Optional[int] = None

            # First, try to get existing user (read-only)
            with get_db_session() as session:
                user = session.query(User).filter(User.psid == user_id).first()

                if user:
                    # User exists, update last message time
                    user_id_pk = user.id

            # If user doesn't exist, create it with proper transaction
            if not user:
                try:
                    with get_db_session_with_commit() as session:
                        # Double-check user doesn't exist (race condition protection)
                        user = session.query(User).filter(User.psid == user_id).first()

                        if not user:
                            user_data: Dict[str, Any] = {
                                "psid": user_id,
                                "platform": platform,
                                "created_at": datetime.now(timezone.utc),
                                "last_message_at": datetime.now(timezone.utc)
                            }
                            user = User(**user_data)
                            session.add(user)
                            session.flush()  # Get ID before commit
                            user_id_pk = user.id
                            logger.info(f"Created new user: {user_id}")
                        else:
                            user_id_pk = user.id
                            logger.info(f"User already exists (race condition avoided): {user_id}")

                except IntegrityError as ie:
                    # Handle race condition: another thread created the user
                    logger.warning(f"Race condition detected for user {user_id}: {ie}")
                    with get_db_session() as session:
                        user = session.query(User).filter(User.psid == user_id).first()
                        user_id_pk = user.id if user else None

            # Update last message time in separate transaction
            if user_id_pk:
                with get_db_session_with_commit() as session:
                    user = session.query(User).filter(User.id == user_id_pk).first()
                    if user:
                        user.last_message_at = datetime.now(timezone.utc)
                        return user

            return None

        except Exception as e:
            logger.error(f"Error getting or creating user {user_id}: {e}")
            return None

    async def _detect_product_query(self, message_text: str) -> bool:
        """Detect if message is a product-related query"""
        try:
            if not self.bww_store:
                return False
            
            # Import constants from bww_store
            from bww_store.constants import CLOTHING_KEYWORDS_AR, CLOTHING_KEYWORDS_EN
            
            message_lower = message_text.lower()
            
            # Check for product-related keywords
            product_keywords = [
                "منتج", "منتجات", "عايز", "عايزة", "محتاج", "محتاجة",
                "فستان", "بنطلون", "بلوزة", "تيشرت", "جاكيت",
                "سعر", "كام", "متاح", "موجود", "عندك",
                "product", "products", "looking for", "want", "need"
            ]
            
            # Check Arabic clothing keywords
            for keyword in CLOTHING_KEYWORDS_AR:
                if keyword in message_lower:
                    return True
            
            # Check English clothing keywords
            for keyword in CLOTHING_KEYWORDS_EN:
                if keyword.lower() in message_lower:
                    return True
            
            # Check general product keywords
            for keyword in product_keywords:
                if keyword in message_lower:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting product query: {e}")
            return False

    async def _send_product_cards(self, user_id: str, product_cards: list[str], platform: str) -> bool:
        """Send product cards to user"""
        try:
            if platform == "facebook" and self.messenger_service:
                # Send as generic template (cards)
                for card in product_cards[:3]:  # Max 3 cards
                    self.messenger_service.send_message(user_id, str(card))
                return True
            elif platform == "whatsapp" and self.whatsapp_service:
                # Send as text messages
                for card in product_cards[:3]:
                    self.whatsapp_service.send_message(user_id, str(card))
                return True
            return False
        except Exception as e:
            logger.error(f"Error sending product cards: {e}")
            return False

    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        base_status = super().get_service_status()

        status = {
            **base_status,
            "platform": self.platform,
            "database": "connected",  # Database is always available via get_session()
            "ai_service_status": self.ai_service.get_service_status(),
            "messenger_service_status": self.messenger_service.get_service_status(),
            "whatsapp_service_status": self.whatsapp_service.get_service_status(),
            "initialized": self._initialized
        }
        
        # Add BWW Store status if available
        if self.bww_store:
            status["bww_store_status"] = self.bww_store.get_service_status()
            status["bww_store_enabled"] = True
        else:
            status["bww_store_enabled"] = False
        
        # Add Product Recommender status if available
        if self.product_recommender:
            status["product_recommender_status"] = self.product_recommender.get_service_status()
            status["product_recommender_enabled"] = True
        else:
            status["product_recommender_enabled"] = False
        
        return status

    def health_check(self) -> ServiceHealth:
        """Comprehensive health check"""
        try:
            # Database health - check if we can get a session
            db_healthy = True
            try:
                with get_db_session() as _:
                    # If we can get a session, database is healthy
                    pass
            except Exception as e:
                logger.error(f"Database health check failed: {e}")
                db_healthy = False

            ai_health = self.ai_service.health_check()

            # Determine overall health status
            if db_healthy and ai_health.status == ServiceStatus.HEALTHY and self._initialized:
                status = ServiceStatus.HEALTHY
                message = "All services healthy"
            elif db_healthy or ai_health.status != ServiceStatus.UNHEALTHY:
                status = ServiceStatus.DEGRADED
                message = "Some services degraded"
            else:
                status = ServiceStatus.UNHEALTHY
                message = "Services unhealthy"

            return ServiceHealth(
                status=status,
                message=message,
                timestamp=datetime.now(timezone.utc),
                metrics={
                    "db_healthy": db_healthy,
                    "ai_status": ai_health.status,
                    "initialized": self._initialized
                },
                dependencies=["database", "ai_service", "messenger_service", "whatsapp_service"]
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ServiceHealth(
                status=ServiceStatus.UNKNOWN,
                message=f"Health check error: {str(e)}",
                timestamp=datetime.now(timezone.utc),
                metrics={},
                dependencies=[]
            )

    def process_message(self, message_data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Process incoming message (sync wrapper)"""
        try:
            # Extract platform from kwargs or message_data
            platform = kwargs.get('platform') or message_data.get('platform', 'facebook')
            return asyncio.run(self._process_message_impl(message_data, platform))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {"success": False, "error": str(e)}

    def send_message(self, recipient_id: str, message: str, **kwargs: Any) -> Dict[str, Any]:
        """Send message to user (sync wrapper)"""
        try:
            # Extract platform from kwargs, default to facebook
            platform = kwargs.get('platform', 'facebook')
            success = asyncio.run(self._send_message_impl(recipient_id, message, platform))
            return {
                "success": success,
                "recipient_id": recipient_id,
                "platform": platform
            }
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _do_shutdown(self) -> None:
        """Shutdown all services"""
        try:
            # No db_service to shutdown - database connections managed by get_session()
            self.ai_service.shutdown()
            self.messenger_service.shutdown()
            self.whatsapp_service.shutdown()
            logger.info("Professional Message Handler shutdown successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Create global instance
message_handler = MessageHandler()
