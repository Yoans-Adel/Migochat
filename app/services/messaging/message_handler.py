"""
New Professional Message Handler
Completely independent implementation using the new architecture
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session

from app.services.core.base_service import MessageService
from app.services.ai.ai_service import AIService
from app.services.messaging.messenger_service import MessengerService
from app.services.messaging.whatsapp_service import WhatsAppService
from database import get_db_session, User, Message, Conversation, MessageDirection, MessageStatus, Governorate
from Server.config import settings

logger = logging.getLogger(__name__)

class MessageHandler(MessageService):
    """Message handler using the new architecture"""
    
    def __init__(self):
        super().__init__()
        self.platform = "multi"
        self.ai_service = AIService()
        self.messenger_service = MessengerService()
        self.whatsapp_service = WhatsAppService()
        self._initialized = False
    
    def _do_initialize(self):
        """Initialize all services"""
        try:
            # Database accessed directly via app.database module
            self.ai_service.initialize()
            self.messenger_service.initialize()
            self.whatsapp_service.initialize()
            self._initialized = True
            logger.info("Professional Message Handler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Professional Message Handler: {e}")
            raise
    
    async def _process_message_impl(self, message_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Process incoming message"""
        try:
            # Extract message details
            user_id = message_data.get("user_id")
            message_text = message_data.get("text", "")
            message_id = message_data.get("message_id")
            
            logger.info(f"Processing {platform} message from user {user_id}: {message_text}")
            
            # Get or create user
            user = await self._get_or_create_user(user_id, platform)
            if not user:
                return {"success": False, "error": "Failed to get or create user"}
            
            # Generate AI response (sync method)
            ai_response = self.ai_service.generate_response(message_text, context={"user": user})
            
            # Send response back
            response_sent = await self._send_message_impl(user_id, ai_response, platform)
            
            return {
                "success": True,
                "user_id": user_id,
                "response": ai_response,
                "response_sent": response_sent,
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
                return response is not None
            elif platform == "whatsapp":
                response = self.whatsapp_service.send_message(user_id, message)
                return response is not None
            else:
                logger.warning(f"Unknown platform: {platform}")
                return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def _get_or_create_user(self, user_id: str, platform: str) -> Optional[User]:
        """Get existing user or create new one"""
        try:
            # Use the proper context manager for database session
            with get_db_session() as session:
                # Try to find existing user
                user = session.query(User).filter(User.psid == user_id).first()
                
                if not user:
                    # Create new user
                    user_data = {
                        "psid": user_id,
                        "platform": platform,
                        "created_at": datetime.now(timezone.utc),
                        "last_message_at": datetime.now(timezone.utc)
                    }
                    user = User(**user_data)
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                    logger.info(f"Created new user: {user_id}")
                else:
                    # Update last message time
                    user.last_message_at = datetime.now(timezone.utc)
                    session.commit()
                    logger.info(f"Found existing user: {user_id}")
                
                return user
                    
        except Exception as e:
            logger.error(f"Error getting or creating user {user_id}: {e}")
            return None
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        base_status = super().get_service_status()
        
        return {
            **base_status,
            "platform": self.platform,
            "database": "connected",  # Database is always available via get_session()
            "ai_service_status": self.ai_service.get_service_status(),
            "messenger_service_status": self.messenger_service.get_service_status(),
            "whatsapp_service_status": self.whatsapp_service.get_service_status(),
            "initialized": self._initialized
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            # Database health - check if we can get a session
            db_healthy = True
            try:
                with get_db_session() as session:
                    # If we can get a session, database is healthy
                    pass
            except Exception:
                db_healthy = False
                
            ai_health = await self.ai_service.health_check()
            
            healthy = (
                db_healthy and
                ai_health.get("healthy", False) and
                self._initialized
            )
            
            return {
                "healthy": healthy,
                "db_healthy": db_healthy,
                "ai_healthy": ai_health.get("healthy", False),
                "initialized": self._initialized,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def process_message(self, message_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Process incoming message (sync wrapper)"""
        import asyncio
        try:
            return asyncio.run(self._process_message_impl(message_data, platform))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {"success": False, "error": str(e)}
    
    def send_message(self, user_id: str, message: str, platform: str = "facebook") -> bool:
        """Send message to user (sync wrapper)"""
        import asyncio
        try:
            return asyncio.run(self._send_message_impl(user_id, message, platform))
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def _do_shutdown(self):
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
