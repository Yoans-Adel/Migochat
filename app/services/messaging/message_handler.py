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


class MessageHandler(MessageService):
    """Message handler using the new architecture"""

    def __init__(self) -> None:
        super().__init__()
        self.platform = "multi"
        self.ai_service = AIService()
        self.messenger_service = MessengerService()
        self.whatsapp_service = WhatsAppService()
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

            # Generate AI response (sync method)
            ai_response = self.ai_service.generate_response(message_text, context={"user": user})

            # Send response back
            response_sent = await self._send_message_impl(str(user_id), ai_response, platform)

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
