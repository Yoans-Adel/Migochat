"""
Infrastructure Services Module
===============================
Cross-cutting concerns that support all other services.

This module provides:
- Dependency Injection Container (lifecycle management)
- Service Registry (service discovery and registration)
- Error Handling (circuit breakers, retry logic, monitoring)
- Configuration Management (hot-reload, multi-format support)

These services enable robust, maintainable, and scalable architecture.
"""

from typing import TYPE_CHECKING, Any

# Lazy imports for better performance
if TYPE_CHECKING:
    from .di_container import (
        DependencyInjectionContainer,
        ServiceScope,
        ServiceRegistration,
        get_container,
    )
    from .service_registry import (
        ServiceRegistry,
        ServiceFactory,
        ServiceLifecycleManager,
        ServiceDefinition,
        ServicePriority,
    )
    from .error_handler import (
        CircuitBreaker,
        CircuitBreakerState,
        CircuitBreakerConfig,
        ErrorMonitor,
        RetryConfig,
        ErrorHandler,
        ErrorSeverity,
        ErrorCategory,
        ErrorContext,
        ErrorRecord,
    )
    from .configuration_manager import (
        ConfigurationManager,
        ConfigurationLoader,
        ConfigurationWatcher,
        ServiceConfiguration,
        ConfigFormat,
        ConfigurationValidator,
    )

__all__ = [
    # Dependency Injection
    "DependencyInjectionContainer",
    "ServiceScope",
    "ServiceRegistration",
    "get_container",
    # Service Registry
    "ServiceRegistry",
    "ServiceFactory",
    "ServiceLifecycleManager",
    "ServiceDefinition",
    "ServicePriority",
    # Error Handling
    "CircuitBreaker",
    "CircuitBreakerState",
    "CircuitBreakerConfig",
    "ErrorMonitor",
    "RetryConfig",
    "ErrorHandler",
    "ErrorSeverity",
    "ErrorCategory",
    "ErrorContext",
    "ErrorRecord",
    # Configuration
    "ConfigurationManager",
    "ConfigurationLoader",
    "ConfigurationWatcher",
    "ServiceConfiguration",
    "ConfigFormat",
    "ConfigurationValidator",
]


def __getattr__(name: str) -> Any:
    """Lazy import mechanism for better performance."""
    if name in __all__:
        # DI Container imports
        if name in ["DependencyInjectionContainer", "ServiceScope", "ServiceRegistration", "get_container"]:
            from .di_container import (
                DependencyInjectionContainer,
                ServiceScope,
                ServiceRegistration,
                get_container,
            )
            return {
                "DependencyInjectionContainer": DependencyInjectionContainer,
                "ServiceScope": ServiceScope,
                "ServiceRegistration": ServiceRegistration,
                "get_container": get_container,
            }[name]

        # Service Registry imports
        if name in ["ServiceRegistry", "ServiceFactory", "ServiceLifecycleManager", "ServiceDefinition", "ServicePriority"]:
            from .service_registry import (
                ServiceRegistry,
                ServiceFactory,
                ServiceLifecycleManager,
                ServiceDefinition,
                ServicePriority,
            )
            return {
                "ServiceRegistry": ServiceRegistry,
                "ServiceFactory": ServiceFactory,
                "ServiceLifecycleManager": ServiceLifecycleManager,
                "ServiceDefinition": ServiceDefinition,
                "ServicePriority": ServicePriority,
            }[name]

        # Error Handler imports
        if name in ["CircuitBreaker", "CircuitBreakerState", "CircuitBreakerConfig", "ErrorMonitor", "RetryConfig", "ErrorHandler", "ErrorSeverity", "ErrorCategory", "ErrorContext", "ErrorRecord"]:
            from .error_handler import (
                CircuitBreaker,
                CircuitBreakerState,
                CircuitBreakerConfig,
                ErrorMonitor,
                RetryConfig,
                ErrorHandler,
                ErrorSeverity,
                ErrorCategory,
                ErrorContext,
                ErrorRecord,
            )
            return {
                "CircuitBreaker": CircuitBreaker,
                "CircuitBreakerState": CircuitBreakerState,
                "CircuitBreakerConfig": CircuitBreakerConfig,
                "ErrorMonitor": ErrorMonitor,
                "RetryConfig": RetryConfig,
                "ErrorHandler": ErrorHandler,
                "ErrorSeverity": ErrorSeverity,
                "ErrorCategory": ErrorCategory,
                "ErrorContext": ErrorContext,
                "ErrorRecord": ErrorRecord,
            }[name]

        # Configuration imports
        if name in ["ConfigurationManager", "ConfigurationLoader", "ConfigurationWatcher", "ServiceConfiguration", "ConfigFormat", "ConfigurationValidator"]:
            from .configuration_manager import (
                ConfigurationManager,
                ConfigurationLoader,
                ConfigurationWatcher,
                ServiceConfiguration,
                ConfigFormat,
                ConfigurationValidator,
            )
            return {
                "ConfigurationManager": ConfigurationManager,
                "ConfigurationLoader": ConfigurationLoader,
                "ConfigurationWatcher": ConfigurationWatcher,
                "ServiceConfiguration": ServiceConfiguration,
                "ConfigFormat": ConfigFormat,
                "ConfigurationValidator": ConfigurationValidator,
            }[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
