"""
Core Services Module
====================
Foundation layer containing service interfaces and base class implementations.

This module provides:
- Service contracts (Protocol interfaces)
- Base service implementations with health monitoring
- Common service patterns (BaseService, APIService, MessageService, etc.)

All other service modules depend on this core foundation.
"""

from typing import TYPE_CHECKING, Any

# Lazy imports for better performance
if TYPE_CHECKING:
    from .interfaces import (
        ServiceInterface,
        AIServiceInterface,
        MessageServiceInterface,
        APIServiceInterface,
        LeadServiceInterface,
        ProductServiceInterface,
        NotificationServiceInterface,
        AnalyticsServiceInterface,
        CacheServiceInterface,
        SecurityServiceInterface,
        ConfigurationServiceInterface,
        LoggingServiceInterface,
        ServiceRegistryInterface,
        ServiceFactoryInterface,
        ServiceLifecycleInterface,
        ServiceHealth,
        ServiceStatus,
        ServiceConfig,
    )
    from .base_service import (
        BaseService,
        DatabaseService,
        APIService,
        MessageService,
        AIService as BaseAIService,
        LeadService,
        ProductService,
        ServiceState,
    )

__all__ = [
    # Interfaces
    "ServiceInterface",
    "AIServiceInterface",
    "MessageServiceInterface",
    "APIServiceInterface",
    "LeadServiceInterface",
    "ProductServiceInterface",
    "NotificationServiceInterface",
    "AnalyticsServiceInterface",
    "CacheServiceInterface",
    "SecurityServiceInterface",
    "ConfigurationServiceInterface",
    "LoggingServiceInterface",
    "ServiceRegistryInterface",
    "ServiceFactoryInterface",
    "ServiceLifecycleInterface",
    "ServiceHealth",
    "ServiceStatus",
    "ServiceConfig",
    # Base Classes
    "BaseService",
    "DatabaseService",
    "APIService",
    "MessageService",
    "BaseAIService",
    "LeadService",
    "ProductService",
    "ServiceState",
]


def __getattr__(name: str) -> Any:
    """Lazy import mechanism for better performance."""
    if name in __all__:
        # Import from interfaces
        if name in [
            "ServiceInterface", "AIServiceInterface", "MessageServiceInterface",
            "APIServiceInterface", "LeadServiceInterface", "ProductServiceInterface",
            "NotificationServiceInterface", "AnalyticsServiceInterface",
            "CacheServiceInterface", "SecurityServiceInterface",
            "ConfigurationServiceInterface", "LoggingServiceInterface",
            "ServiceRegistryInterface", "ServiceFactoryInterface",
            "ServiceLifecycleInterface", "ServiceHealth", "ServiceStatus", "ServiceConfig"
        ]:
            from .interfaces import (
                ServiceInterface,
                AIServiceInterface,
                MessageServiceInterface,
                APIServiceInterface,
                LeadServiceInterface,
                ProductServiceInterface,
                NotificationServiceInterface,
                AnalyticsServiceInterface,
                CacheServiceInterface,
                SecurityServiceInterface,
                ConfigurationServiceInterface,
                LoggingServiceInterface,
                ServiceRegistryInterface,
                ServiceFactoryInterface,
                ServiceLifecycleInterface,
                ServiceHealth,
                ServiceStatus,
                ServiceConfig,
            )
            return {
                "ServiceInterface": ServiceInterface,
                "AIServiceInterface": AIServiceInterface,
                "MessageServiceInterface": MessageServiceInterface,
                "APIServiceInterface": APIServiceInterface,
                "LeadServiceInterface": LeadServiceInterface,
                "ProductServiceInterface": ProductServiceInterface,
                "NotificationServiceInterface": NotificationServiceInterface,
                "AnalyticsServiceInterface": AnalyticsServiceInterface,
                "CacheServiceInterface": CacheServiceInterface,
                "SecurityServiceInterface": SecurityServiceInterface,
                "ConfigurationServiceInterface": ConfigurationServiceInterface,
                "LoggingServiceInterface": LoggingServiceInterface,
                "ServiceRegistryInterface": ServiceRegistryInterface,
                "ServiceFactoryInterface": ServiceFactoryInterface,
                "ServiceLifecycleInterface": ServiceLifecycleInterface,
                "ServiceHealth": ServiceHealth,
                "ServiceStatus": ServiceStatus,
                "ServiceConfig": ServiceConfig,
            }[name]

        # Import from base_service
        if name in [
            "BaseService", "DatabaseService", "APIService", "MessageService",
            "BaseAIService", "LeadService", "ProductService", "ServiceState"
        ]:
            from .base_service import (
                BaseService,
                DatabaseService,
                APIService,
                MessageService,
                AIService as BaseAIService,
                LeadService,
                ProductService,
                ServiceState,
            )
            return {
                "BaseService": BaseService,
                "DatabaseService": DatabaseService,
                "APIService": APIService,
                "MessageService": MessageService,
                "BaseAIService": BaseAIService,
                "LeadService": LeadService,
                "ProductService": ProductService,
                "ServiceState": ServiceState,
            }[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
