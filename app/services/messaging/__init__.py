"""
Messaging Services Module
=========================
Message handling and multi-platform communication services.

This module provides:
- Facebook Messenger integration
- WhatsApp Business API integration
- Professional message handler (orchestration and routing)

Enables seamless communication across multiple messaging platforms.
"""

from typing import TYPE_CHECKING

# Lazy imports for better performance
if TYPE_CHECKING:
    from .messenger_service import MessengerService
    from .whatsapp_service import WhatsAppService
    from .message_handler import MessageHandler

__all__ = [
    "MessengerService",
    "WhatsAppService",
    "MessageHandler",
]


def __getattr__(name: str):
    """Lazy import mechanism for better performance."""
    if name == "MessengerService":
        from .messenger_service import MessengerService
        return MessengerService
    
    if name == "WhatsAppService":
        from .whatsapp_service import WhatsAppService
        return WhatsAppService
    
    if name == "MessageHandler":
        from .message_handler import MessageHandler
        return MessageHandler
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
