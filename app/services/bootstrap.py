"""
Professional Service Bootstrap and Initialization for BWW Assistant Chatbot
Centralized service initialization with dependency management and health monitoring
"""

import logging
import threading
from typing import Dict, Any, Optional, List, Type
from datetime import datetime, timezone
from pathlib import Path

from app.services.core.interfaces import ServiceInterface, ServiceStatus
from app.services.infrastructure.di_container import DependencyInjectionContainer, ServiceScope
from app.services.infrastructure.service_registry import ServiceRegistry, ServiceDefinition, ServicePriority
from app.services.infrastructure.configuration_manager import ConfigurationManager
from app.services.infrastructure.error_handler import ErrorHandler
from app.services.core.base_service import BaseService

logger = logging.getLogger(__name__)


class ServiceBootstrap:
    """Professional service bootstrap and initialization system"""

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path("config")
        self.config_dir.mkdir(exist_ok=True)

        # Core components
        self._config_manager: Optional[ConfigurationManager] = None
        self._error_handler: Optional[ErrorHandler] = None
        self._di_container: Optional[DependencyInjectionContainer] = None
        self._service_registry: Optional[ServiceRegistry] = None

        # Service definitions
        self._service_definitions: Dict[str, ServiceDefinition] = {}
        self._initialized_services: Dict[str, ServiceInterface] = {}

        # Bootstrap state
        self._bootstrap_complete = False
        self._lock = threading.RLock()

        # Performance monitoring
        self._startup_time: Optional[datetime] = None
        self._initialization_errors: List[str] = []

    def initialize(self) -> bool:
        """Initialize the service bootstrap system"""
        try:
            with self._lock:
                if self._bootstrap_complete:
                    logger.info("Service bootstrap already initialized")
                    return True

                self._startup_time = datetime.now(timezone.utc)
                logger.info("Starting service bootstrap initialization...")

                # Initialize core components in order
                if not self._initialize_core_components():
                    return False

                # Register service definitions
                if not self._register_service_definitions():
                    return False

                # Initialize services
                if not self._initialize_services():
                    return False

                self._bootstrap_complete = True
                startup_duration = (datetime.now(timezone.utc) - self._startup_time).total_seconds()

                logger.info(f"Service bootstrap completed successfully in {startup_duration:.2f}s")
                logger.info(f"Initialized {len(self._initialized_services)} services")

                return True

        except Exception as e:
            logger.error(f"Service bootstrap initialization failed: {e}")
            self._initialization_errors.append(str(e))
            return False

    def _initialize_core_components(self) -> bool:
        """Initialize core components"""
        try:
            # 1. Initialize Configuration Manager
            logger.info("Initializing configuration manager...")
            self._config_manager = ConfigurationManager(str(self.config_dir))
            if not self._config_manager.initialize():
                logger.error("Failed to initialize configuration manager")
                return False

            # 2. Initialize Error Handler
            logger.info("Initializing error handler...")
            self._error_handler = ErrorHandler()

            # 3. Initialize Dependency Injection Container
            logger.info("Initializing dependency injection container...")
            self._di_container = DependencyInjectionContainer()

            # 4. Initialize Service Registry
            logger.info("Initializing service registry...")
            self._service_registry = ServiceRegistry()

            logger.info("Core components initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize core components: {e}")
            return False

    def _register_service_definitions(self) -> bool:
        """Register all service definitions"""
        try:
            logger.info("Registering service definitions...")

            # Register core services (skip database_service - use app.database directly)
            self._register_core_services()

            # Register platform services
            self._register_platform_services()

            # Register AI services
            self._register_ai_services()

            # Register integration services
            self._register_integration_services()

            logger.info(f"Registered {len(self._service_definitions)} service definitions")
            return True

        except Exception as e:
            logger.error(f"Failed to register service definitions: {e}")
            return False

    def _register_core_services(self) -> None:
        """Register core services"""
        # Note: Database Service has been archived - use database module directly
        # from database import get_session, User, Message, etc.

        # Configuration Service
        self._register_service(
            name="configuration_service",
            service_type=BaseService,
            implementation=self._get_configuration_service_class(),
            scope=ServiceScope.SINGLETON,
            priority=ServicePriority.CRITICAL,
            dependencies=[]
        )

        # Error Handler Service
        self._register_service(
            name="error_handler_service",
            service_type=BaseService,
            implementation=self._get_error_handler_service_class(),
            scope=ServiceScope.SINGLETON,
            priority=ServicePriority.CRITICAL,
            dependencies=[]
        )

    def _register_platform_services(self) -> None:
        """Register platform services"""
        # Messenger Service (no database_service dependency - uses app.database directly)
        self._register_service(
            name="messenger_service",
            service_type=BaseService,
            implementation=self._get_messenger_service_class(),
            scope=ServiceScope.SINGLETON,
            priority=ServicePriority.HIGH,
            dependencies=["ai_service"]
        )

        # WhatsApp Service
        self._register_service(
            name="whatsapp_service",
            service_type=BaseService,
            implementation=self._get_whatsapp_service_class(),
            scope=ServiceScope.SINGLETON,
            priority=ServicePriority.HIGH,
            dependencies=["ai_service"]
        )

        # Message Handler
        self._register_service(
            name="message_handler",
            service_type=BaseService,
            implementation=self._get_message_handler_class(),
            scope=ServiceScope.SINGLETON,
            priority=ServicePriority.HIGH,
            dependencies=["messenger_service", "ai_service"]
        )

        # WhatsApp Message Handler
        self._register_service(
            name="whatsapp_message_handler",
            service_type=BaseService,
            implementation=self._get_whatsapp_message_handler_class(),
            scope=ServiceScope.SINGLETON,
            priority=ServicePriority.HIGH,
            dependencies=["whatsapp_service", "ai_service"]
        )

    def _register_ai_services(self) -> None:
        """Register AI services"""
        # AI Service (no database_service dependency)
        self._register_service(
            name="ai_service",
            service_type=BaseService,
            implementation=self._get_ai_service_class(),
            scope=ServiceScope.SINGLETON,
            priority=ServicePriority.CRITICAL,
            dependencies=[]
        )

        # Gemini Service
        self._register_service(
            name="gemini_service",
            service_type=BaseService,
            implementation=self._get_gemini_service_class(),
            scope=ServiceScope.SINGLETON,
            priority=ServicePriority.NORMAL,
            dependencies=[]
        )

        # Keyword Manager
        self._register_service(
            name="keyword_manager",
            service_type=BaseService,
            implementation=self._get_keyword_manager_class(),
            scope=ServiceScope.SINGLETON,
            priority=ServicePriority.NORMAL,
            dependencies=[]
        )

    def _register_integration_services(self) -> None:
        """Register integration services"""
        # Facebook Lead Center Service (no database_service dependency)
        self._register_service(
            name="facebook_lead_center_service",
            service_type=BaseService,
            implementation=self._get_facebook_lead_center_service_class(),
            scope=ServiceScope.SINGLETON,
            priority=ServicePriority.NORMAL,
            dependencies=[]
        )

        # Message Source Tracker (no database_service dependency)
        self._register_service(
            name="message_source_tracker",
            service_type=BaseService,
            implementation=self._get_message_source_tracker_class(),
            scope=ServiceScope.SINGLETON,
            priority=ServicePriority.LOW,
            dependencies=[]
        )

        # Note: Health Monitor service has been archived and is no longer registered
        # The _get_health_monitor_class() method is kept for backward compatibility

    def _register_service(self, name: str, service_type: Type[ServiceInterface],
                          implementation: Optional[Type[ServiceInterface]] = None,
                          scope: ServiceScope = ServiceScope.SINGLETON,
                          priority: ServicePriority = ServicePriority.NORMAL,
                          dependencies: List[str] = None) -> None:
        """Register a service definition"""
        definition = ServiceDefinition(
            name=name,
            service_type=service_type,
            implementation=implementation or service_type,
            scope=scope,
            priority=priority,
            dependencies=dependencies or [],
            auto_start=True
        )

        self._service_definitions[name] = definition
        logger.debug(f"Registered service definition: {name}")

    def _initialize_services(self) -> bool:
        """Initialize all services in dependency order"""
        try:
            logger.info("Initializing services...")

            # Get startup order from registry
            startup_order = self._service_registry.get_startup_order()

            for service_name in startup_order:
                if service_name not in self._service_definitions:
                    logger.warning(f"Service definition not found: {service_name}")
                    continue

                try:
                    logger.info(f"Initializing service: {service_name}")

                    # Get service from DI container
                    service = self._di_container.get_service(service_name)
                    if not service:
                        logger.error(f"Failed to get service from container: {service_name}")
                        continue

                    # Initialize service
                    if hasattr(service, 'initialize'):
                        if not service.initialize():
                            logger.error(f"Service initialization failed: {service_name}")
                            continue

                    self._initialized_services[service_name] = service
                    logger.info(f"Service initialized successfully: {service_name}")

                except Exception as e:
                    logger.error(f"Failed to initialize service {service_name}: {e}")
                    self._initialization_errors.append(f"{service_name}: {e}")
                    continue

            logger.info(f"Successfully initialized {len(self._initialized_services)} services")
            # Return True even if no services initialized - bootstrap itself is working
            return True

        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            return False

    def get_service(self, name: str) -> Optional[ServiceInterface]:
        """Get initialized service by name"""
        with self._lock:
            return self._initialized_services.get(name)

    def get_all_services(self) -> Dict[str, ServiceInterface]:
        """Get all initialized services"""
        with self._lock:
            return self._initialized_services.copy()

    def get_service_status(self) -> Dict[str, Any]:
        """Get bootstrap system status"""
        with self._lock:
            startup_duration = None
            if self._startup_time:
                startup_duration = (datetime.now(timezone.utc) - self._startup_time).total_seconds()

            return {
                "bootstrap_complete": self._bootstrap_complete,
                "startup_time": self._startup_time.isoformat() if self._startup_time else None,
                "startup_duration_seconds": startup_duration,
                "services_initialized": len(self._initialized_services),
                "services_registered": len(self._service_definitions),
                "initialization_errors": self._initialization_errors,
                "service_names": list(self._initialized_services.keys())
            }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all services"""
        try:
            healthy_services = 0
            unhealthy_services = 0
            degraded_services = 0

            service_health = {}

            for name, service in self._initialized_services.items():
                try:
                    if hasattr(service, 'health_check'):
                        health = service.health_check()
                        service_health[name] = health

                        if health.status == ServiceStatus.HEALTHY:
                            healthy_services += 1
                        elif health.status == ServiceStatus.DEGRADED:
                            degraded_services += 1
                        else:
                            unhealthy_services += 1
                    else:
                        service_health[name] = {"status": "unknown", "message": "No health check available"}
                        unhealthy_services += 1

                except Exception as e:
                    service_health[name] = {"status": "error", "message": str(e)}
                    unhealthy_services += 1

            return {
                "overall_status": "healthy" if unhealthy_services == 0 else "degraded" if degraded_services > 0 else "unhealthy",
                "healthy_services": healthy_services,
                "degraded_services": degraded_services,
                "unhealthy_services": unhealthy_services,
                "total_services": len(self._initialized_services),
                "service_health": service_health,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "overall_status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def shutdown(self) -> None:
        """Shutdown all services"""
        try:
            logger.info("Shutting down services...")

            # Shutdown services in reverse order
            shutdown_order = list(reversed(self._initialized_services.keys()))

            for service_name in shutdown_order:
                try:
                    service = self._initialized_services[service_name]
                    if hasattr(service, 'shutdown'):
                        service.shutdown()
                        logger.info(f"Service shutdown completed: {service_name}")
                except Exception as e:
                    logger.error(f"Error shutting down service {service_name}: {e}")

            # Shutdown core components
            if self._config_manager:
                self._config_manager.shutdown()

            self._initialized_services.clear()
            self._bootstrap_complete = False

            logger.info("Service bootstrap shutdown completed")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    # Service class getters (to be implemented based on actual service classes)
    def _get_database_service_class(self) -> Type[ServiceInterface]:
        """Get database service class - ARCHIVED"""
        # Database service has been archived
        # Use database module directly for database operations
        raise NotImplementedError(
            "DatabaseServiceProfessional has been archived. "
            "Use database module directly: from database import get_session, User, etc."
        )

    def _get_configuration_service_class(self) -> Type[ServiceInterface]:
        """Get configuration service class"""
        return ConfigurationManager

    def _get_error_handler_service_class(self) -> Type[ServiceInterface]:
        """Get error handler service class"""
        return ErrorHandler

    def _get_messenger_service_class(self) -> Type[ServiceInterface]:
        """Get messenger service class"""
        from app.services.messaging.messenger_service import MessengerService
        return MessengerService

    def _get_whatsapp_service_class(self) -> Type[ServiceInterface]:
        """Get WhatsApp service class"""
        from app.services.messaging.whatsapp_service import WhatsAppService
        return WhatsAppService

    def _get_message_handler_class(self) -> Type[ServiceInterface]:
        """Get message handler class"""
        from app.services.messaging.message_handler import MessageHandler
        return MessageHandler

    def _get_whatsapp_message_handler_class(self) -> Type[ServiceInterface]:
        """Get WhatsApp message handler class (using professional handler)"""
        from app.services.messaging.message_handler import MessageHandler
        return MessageHandler

    def _get_ai_service_class(self) -> Type[ServiceInterface]:
        """Get AI service class"""
        from app.services.ai.ai_service import AIService
        return AIService

    def _get_gemini_service_class(self) -> Type[ServiceInterface]:
        """Get Gemini service class"""
        from app.services.ai.gemini_service import GeminiService
        return GeminiService

    def _get_keyword_manager_class(self) -> Type[ServiceInterface]:
        """Get keyword manager class"""
        from app.services.business.keyword_manager import KeywordManager
        return KeywordManager

    def _get_facebook_lead_center_service_class(self) -> Type[ServiceInterface]:
        """Get Facebook lead center service class"""
        from app.services.business.facebook_lead_center_service import FacebookLeadCenterService
        return FacebookLeadCenterService

    def _get_message_source_tracker_class(self) -> Type[ServiceInterface]:
        """Get message source tracker class"""
        from app.services.business.message_source_tracker import MessageSourceTracker
        return MessageSourceTracker

    def _get_health_monitor_class(self) -> Type[ServiceInterface]:
        """Get health monitor class (archived - returns None)"""
        logger.warning("Health monitor service has been archived and is no longer available")
        return None


# Global service bootstrap instance
_service_bootstrap: Optional[ServiceBootstrap] = None
_bootstrap_lock = threading.Lock()


def get_service_bootstrap(config_dir: Optional[str] = None) -> ServiceBootstrap:
    """Get global service bootstrap instance"""
    global _service_bootstrap

    if _service_bootstrap is None:
        with _bootstrap_lock:
            if _service_bootstrap is None:
                _service_bootstrap = ServiceBootstrap(config_dir)

    return _service_bootstrap


def initialize_services(config_dir: Optional[str] = None) -> bool:
    """Initialize all services"""
    bootstrap = get_service_bootstrap(config_dir)
    return bootstrap.initialize()


def get_service(name: str) -> Optional[ServiceInterface]:
    """Get service by name"""
    bootstrap = get_service_bootstrap()
    return bootstrap.get_service(name)


def get_all_services() -> Dict[str, ServiceInterface]:
    """Get all services"""
    bootstrap = get_service_bootstrap()
    return bootstrap.get_all_services()


def shutdown_services() -> None:
    """Shutdown all services"""
    global _service_bootstrap
    if _service_bootstrap:
        _service_bootstrap.shutdown()
        _service_bootstrap = None
