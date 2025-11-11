"""
Service dependency injection helpers for API routes
Provides clean access to services without circular imports
"""
import logging
from typing import Optional, TypeVar, Type
from functools import lru_cache

logger = logging.getLogger(__name__)

# Type variable for generic service access
T = TypeVar('T')


@lru_cache(maxsize=1)
def get_service_bootstrap():
    """
    Get service bootstrap instance (cached)
    Uses lazy import to avoid circular dependencies
    """
    try:
        from app.services.bootstrap import get_service_bootstrap as _get_bootstrap
        return _get_bootstrap()
    except ImportError as e:
        logger.error(f"Failed to import service bootstrap: {e}")
        return None


def get_service(service_class: Type[T]) -> Optional[T]:
    """
    Get a service instance from the DI container

    Args:
        service_class: The service class type to retrieve

    Returns:
        Service instance or None if not available

    Example:
        messenger = get_service(MessengerService)
        if messenger:
            messenger.send_message(user_id, "Hello")
    """
    bootstrap = get_service_bootstrap()
    if not bootstrap:
        logger.warning(f"Bootstrap not available, cannot get service: {service_class.__name__}")
        return None

    try:
        # Try to get from DI container
        container = bootstrap.di_container
        if container:
            # Type ignore: DI container returns ServiceInterface, but we trust the type at runtime
            service = container.get_service_by_type(service_class)  # type: ignore[arg-type]
            if service:
                return service  # type: ignore[return-value]
    except Exception as e:
        logger.debug(f"Could not resolve service from DI container: {e}")

    # Fallback: try direct instantiation (for services not in DI container yet)
    try:
        logger.debug(f"Falling back to direct instantiation for: {service_class.__name__}")
        return service_class()  # type: ignore[return-value]
    except Exception as e:
        logger.error(f"Failed to instantiate service {service_class.__name__}: {e}")
        return None


def get_messenger_service():
    """Get MessengerService instance"""
    from app.services.messaging.messenger_service import MessengerService
    return get_service(MessengerService)


def get_whatsapp_service():
    """Get WhatsAppService instance"""
    from app.services.messaging.whatsapp_service import WhatsAppService
    return get_service(WhatsAppService)


def get_message_handler():
    """Get MessageHandler instance"""
    from app.services.messaging.message_handler import MessageHandler
    return get_service(MessageHandler)


def get_facebook_lead_center_service():
    """Get FacebookLeadCenterService instance"""
    from app.services.business.facebook_lead_center_service import FacebookLeadCenterService
    return get_service(FacebookLeadCenterService)


def get_message_source_tracker():
    """Get MessageSourceTracker instance"""
    from app.services.business.message_source_tracker import MessageSourceTracker
    return get_service(MessageSourceTracker)


def get_ai_service():
    """Get AIService instance"""
    from app.services.ai.ai_service import AIService
    return get_service(AIService)


def get_gemini_service():
    """Get GeminiService instance"""
    from app.services.ai.gemini_service import GeminiService
    return get_service(GeminiService)


def get_settings_manager():
    """Get SettingsManager instance"""
    try:
        from app.services.infrastructure.settings_manager import get_settings_manager as _get_settings_manager
        return _get_settings_manager()
    except ImportError as e:
        logger.error(f"Failed to import settings manager: {e}")
        return None
