# Create empty
"""
Services Package
================
Professional modular architecture for service-oriented application.

Module Structure:
-----------------
- core/          : Service interfaces and base classes (foundation)
- infrastructure/: Cross-cutting concerns (DI, registry, errors, config)
- messaging/     : Multi-platform message handling
- ai/            : AI and NLP services
- business/      : Business logic and domain services
- bootstrap.py   : Application initialization and service registration

Usage:
------
# Import from submodules directly
from app.services.core import ServiceInterface, BaseService
from app.services.infrastructure import DependencyInjectionContainer
from app.services.messaging import MessengerService
from app.services.ai import GeminiService
from app.services.business import FacebookLeadCenterService

# Or use the bootstrap for initialization
from app.services.bootstrap import ServiceBootstrap

# Initialize all services
bootstrap = ServiceBootstrap()
await bootstrap.initialize_services()
"""

from typing import TYPE_CHECKING

# Re-export commonly used items for convenience
if TYPE_CHECKING:
    # Core
    from .core import (
        ServiceInterface,
        AIServiceInterface,
        MessageServiceInterface,
        BaseService,
        APIService,
        MessageService,
    )
    # Infrastructure
    from .infrastructure import (
        DependencyInjectionContainer,
        ServiceRegistry,
        get_container,
    )
    # Messaging
    from .messaging import (
        MessengerService,
        WhatsAppService,
        MessageHandler,
    )
    # AI
    from .ai import (
        GeminiService,
        AIService,
    )
    # Business
    from .business import (
        FacebookLeadCenterService,
        KeywordManager,
        MessageSourceTracker,
    )

__all__ = [
    # Core exports
    "ServiceInterface",
    "AIServiceInterface",
    "MessageServiceInterface",
    "BaseService",
    "APIService",
    "MessageService",
    # Infrastructure exports
    "DependencyInjectionContainer",
    "ServiceRegistry",
    "get_container",
    # Messaging exports
    "MessengerService",
    "WhatsAppService",
    "MessageHandler",
    # AI exports
    "GeminiService",
    "AIService",
    # Business exports
    "FacebookLeadCenterService",
    "KeywordManager",
    "MessageSourceTracker",
]

def __getattr__(name: str):
    """Lazy import mechanism for optimal performance."""
    if name in __all__:
        # Core imports
        if name in ["ServiceInterface", "AIServiceInterface", "MessageServiceInterface", "BaseService", "APIService", "MessageService"]:
            from .core import ServiceInterface, AIServiceInterface, MessageServiceInterface, BaseService, APIService, MessageService
            return locals()[name]

        # Infrastructure imports
        if name in ["DependencyInjectionContainer", "ServiceRegistry", "get_container"]:
            from .infrastructure import DependencyInjectionContainer, ServiceRegistry, get_container
            return locals()[name]

        # Messaging imports
        if name in ["MessengerService", "WhatsAppService", "MessageHandler"]:
            from .messaging import MessengerService, WhatsAppService, MessageHandler
            return locals()[name]

        # AI imports
        if name in ["GeminiService", "AIService"]:
            from .ai import GeminiService, AIService
            return locals()[name]

        # Business imports
        if name in ["FacebookLeadCenterService", "KeywordManager", "MessageSourceTracker"]:
            from .business import FacebookLeadCenterService, KeywordManager, MessageSourceTracker
            return locals()[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    # files for proper Python package structure
