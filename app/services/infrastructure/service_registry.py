"""
Service Registry and Factory for BWW Assistant Chatbot
Professional service management and factory pattern implementation
"""

import logging
import threading
from typing import Dict, Any, Optional, Type, List, Callable, Union
from dataclasses import dataclass
from enum import Enum

from app.services.core.interfaces import (
    ServiceInterface, ServiceRegistryInterface, ServiceFactoryInterface,
    ServiceLifecycleInterface, ServiceConfig, ServiceStatus
)
from app.services.infrastructure.di_container import DependencyInjectionContainer, ServiceScope

logger = logging.getLogger(__name__)

class ServicePriority(Enum):
    """Service priority enumeration"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

@dataclass
class ServiceDefinition:
    """Service definition with metadata"""
    name: str
    service_type: Type[ServiceInterface]
    implementation: Optional[Type[ServiceInterface]] = None
    factory: Optional[Callable[[], ServiceInterface]] = None
    scope: ServiceScope = ServiceScope.SINGLETON
    priority: ServicePriority = ServicePriority.NORMAL
    config: Optional[ServiceConfig] = None
    dependencies: List[str] = None
    auto_start: bool = True
    health_check_interval: int = 30
    retry_count: int = 3
    timeout: int = 30

class ServiceRegistry(ServiceRegistryInterface):
    """Professional service registry implementation"""

    def __init__(self):
        self._services: Dict[str, ServiceDefinition] = {}
        self._instances: Dict[str, ServiceInterface] = {}
        self._lock = threading.RLock()
        self._logger = logging.getLogger(__name__)
        self._container = DependencyInjectionContainer()
        self._startup_order: List[str] = []
        self._shutdown_order: List[str] = []

    def register_service(self, name: str, service: ServiceInterface) -> None:
        """Register service instance"""
        with self._lock:
            if name in self._services:
                self._logger.warning(f"Service '{name}' is already registered. Overwriting.")

            # Create service definition
            definition = ServiceDefinition(
                name=name,
                service_type=type(service),
                implementation=type(service),
                scope=ServiceScope.SINGLETON,
                auto_start=True
            )

            self._services[name] = definition
            self._instances[name] = service

            # Update startup/shutdown order
            self._update_service_order()

            self._logger.info(f"Registered service instance '{name}'")

    def register_service_definition(self, definition: ServiceDefinition) -> None:
        """Register service definition"""
        with self._lock:
            if definition.name in self._services:
                self._logger.warning(f"Service '{definition.name}' is already registered. Overwriting.")

            self._services[definition.name] = definition

            # Register in DI container
            if definition.scope == ServiceScope.SINGLETON:
                self._container.register_singleton(
                    definition.name,
                    definition.service_type,
                    definition.implementation,
                    definition.factory,
                    definition.config
                )
            elif definition.scope == ServiceScope.TRANSIENT:
                self._container.register_transient(
                    definition.name,
                    definition.service_type,
                    definition.implementation,
                    definition.factory,
                    definition.config
                )
            elif definition.scope == ServiceScope.SCOPED:
                self._container.register_scoped(
                    definition.name,
                    definition.service_type,
                    definition.implementation,
                    definition.factory,
                    definition.config
                )

            # Update startup/shutdown order
            self._update_service_order()

            self._logger.info(f"Registered service definition '{definition.name}'")

    def get_service(self, name: str) -> Optional[ServiceInterface]:
        """Get service by name"""
        with self._lock:
            # Check if we have an instance
            if name in self._instances:
                return self._instances[name]

            # Try to get from container
            if name in self._services:
                service = self._container.get_service(name)
                if service:
                    # Store instance for singleton services
                    definition = self._services[name]
                    if definition.scope == ServiceScope.SINGLETON:
                        self._instances[name] = service
                    return service

            return None

    def unregister_service(self, name: str) -> bool:
        """Unregister service"""
        with self._lock:
            if name not in self._services:
                return False

            # Shutdown service if running
            if name in self._instances:
                instance = self._instances[name]
                if hasattr(instance, 'shutdown'):
                    try:
                        instance.shutdown()
                    except Exception as e:
                        self._logger.error(f"Error shutting down service '{name}': {e}")

                del self._instances[name]

            # Remove from container
            self._container.unregister_service(name)

            # Remove definition
            del self._services[name]

            # Update startup/shutdown order
            self._update_service_order()

            self._logger.info(f"Unregistered service '{name}'")
            return True

    def list_services(self) -> List[str]:
        """List all registered services"""
        with self._lock:
            return list(self._services.keys())

    def get_service_dependencies(self, name: str) -> List[str]:
        """Get service dependencies"""
        with self._lock:
            if name not in self._services:
                return []

            definition = self._services[name]
            return definition.dependencies or []

    def get_service_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed service information"""
        with self._lock:
            if name not in self._services:
                return None

            definition = self._services[name]
            instance = self._instances.get(name)

            info = {
                "name": name,
                "service_type": definition.service_type.__name__,
                "implementation": definition.implementation.__name__ if definition.implementation else None,
                "scope": definition.scope.value,
                "priority": definition.priority.value,
                "auto_start": definition.auto_start,
                "health_check_interval": definition.health_check_interval,
                "retry_count": definition.retry_count,
                "timeout": definition.timeout,
                "dependencies": definition.dependencies or [],
                "has_instance": name in self._instances,
                "has_config": definition.config is not None
            }

            if instance:
                if hasattr(instance, 'get_service_status'):
                    info["status"] = instance.get_service_status()
                if hasattr(instance, 'health_check'):
                    info["health"] = instance.health_check()

            return info

    def get_all_services_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all services"""
        with self._lock:
            return {name: self.get_service_info(name) for name in self._services.keys()}

    def _update_service_order(self) -> None:
        """Update startup and shutdown order based on dependencies and priority"""
        # Create dependency graph
        graph = {}
        for name, definition in self._services.items():
            graph[name] = definition.dependencies or []

        # Topological sort for startup order
        self._startup_order = self._topological_sort(graph)

        # Reverse for shutdown order
        self._shutdown_order = list(reversed(self._startup_order))

    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """Topological sort of service dependencies"""
        visited = set()
        temp_visited = set()
        result = []

        def visit(node):
            if node in temp_visited:
                raise ValueError(f"Circular dependency detected involving '{node}'")
            if node in visited:
                return

            temp_visited.add(node)

            # Visit dependencies first
            for dep in graph.get(node, []):
                if dep in self._services:  # Only visit registered services
                    visit(dep)

            temp_visited.remove(node)
            visited.add(node)
            result.append(node)

        # Visit all nodes
        for node in self._services.keys():
            if node not in visited:
                visit(node)

        return result

    def get_startup_order(self) -> List[str]:
        """Get service startup order"""
        return self._startup_order.copy()

    def get_shutdown_order(self) -> List[str]:
        """Get service shutdown order"""
        return self._shutdown_order.copy()

class ServiceFactory(ServiceFactoryInterface):
    """Professional service factory implementation"""

    def __init__(self):
        self._creators: Dict[str, Callable[[ServiceConfig], ServiceInterface]] = {}
        self._logger = logging.getLogger(__name__)

    def register_creator(self, service_type: str, creator: Callable[[ServiceConfig], ServiceInterface]) -> None:
        """Register service creator"""
        self._creators[service_type] = creator
        self._logger.info(f"Registered creator for service type '{service_type}'")

    def create_service(self, service_type: str, config: ServiceConfig) -> ServiceInterface:
        """Create service instance"""
        if service_type not in self._creators:
            raise ValueError(f"No creator registered for service type '{service_type}'")

        try:
            creator = self._creators[service_type]
            service = creator(config)
            self._logger.info(f"Created service instance of type '{service_type}'")
            return service
        except Exception as e:
            self._logger.error(f"Failed to create service of type '{service_type}': {e}")
            raise

    def get_supported_services(self) -> List[str]:
        """Get list of supported service types"""
        return list(self._creators.keys())

class ServiceLifecycleManager(ServiceLifecycleInterface):
    """Professional service lifecycle management"""

    def __init__(self, registry: ServiceRegistry):
        self._registry = registry
        self._logger = logging.getLogger(__name__)
        self._running_services: set = set()
        self._lock = threading.RLock()

    def start_service(self, name: str) -> bool:
        """Start service"""
        with self._lock:
            if name in self._running_services:
                self._logger.info(f"Service '{name}' is already running")
                return True

            try:
                service = self._registry.get_service(name)
                if not service:
                    self._logger.error(f"Service '{name}' not found")
                    return False

                if hasattr(service, 'initialize'):
                    if service.initialize():
                        self._running_services.add(name)
                        self._logger.info(f"Started service '{name}'")
                        return True
                    else:
                        self._logger.error(f"Failed to initialize service '{name}'")
                        return False
                else:
                    self._running_services.add(name)
                    self._logger.info(f"Started service '{name}' (no initialization required)")
                    return True

            except Exception as e:
                self._logger.error(f"Error starting service '{name}': {e}")
                return False

    def stop_service(self, name: str) -> bool:
        """Stop service"""
        with self._lock:
            if name not in self._running_services:
                self._logger.info(f"Service '{name}' is not running")
                return True

            try:
                service = self._registry.get_service(name)
                if service and hasattr(service, 'shutdown'):
                    service.shutdown()

                self._running_services.discard(name)
                self._logger.info(f"Stopped service '{name}'")
                return True

            except Exception as e:
                self._logger.error(f"Error stopping service '{name}': {e}")
                return False

    def restart_service(self, name: str) -> bool:
        """Restart service"""
        self._logger.info(f"Restarting service '{name}'...")

        if not self.stop_service(name):
            return False

        # Small delay to ensure clean shutdown
        import time
        time.sleep(0.1)

        return self.start_service(name)

    def get_service_status(self, name: str) -> ServiceStatus:
        """Get service status"""
        with self._lock:
            if name not in self._running_services:
                return ServiceStatus.UNHEALTHY

            service = self._registry.get_service(name)
            if not service:
                return ServiceStatus.UNHEALTHY

            if hasattr(service, 'health_check'):
                health = service.health_check()
                return health.status
            elif hasattr(service, 'is_healthy'):
                return ServiceStatus.HEALTHY if service.is_healthy() else ServiceStatus.UNHEALTHY
            else:
                return ServiceStatus.UNKNOWN

    def get_all_services_status(self) -> Dict[str, ServiceStatus]:
        """Get all services status"""
        with self._lock:
            statuses = {}
            for name in self._registry.list_services():
                statuses[name] = self.get_service_status(name)
            return statuses

    def start_all_services(self) -> Dict[str, bool]:
        """Start all services in dependency order"""
        results = {}
        startup_order = self._registry.get_startup_order()

        self._logger.info("Starting all services...")

        for name in startup_order:
            results[name] = self.start_service(name)

        self._logger.info(f"Started {sum(results.values())}/{len(results)} services")
        return results

    def stop_all_services(self) -> Dict[str, bool]:
        """Stop all services in reverse dependency order"""
        results = {}
        shutdown_order = self._registry.get_shutdown_order()

        self._logger.info("Stopping all services...")

        for name in shutdown_order:
            results[name] = self.stop_service(name)

        self._logger.info(f"Stopped {sum(results.values())}/{len(results)} services")
        return results

    def get_running_services(self) -> List[str]:
        """Get list of running services"""
        with self._lock:
            return list(self._running_services)

# Global service management instances
_registry: Optional[ServiceRegistry] = None
_factory: Optional[ServiceFactory] = None
_lifecycle_manager: Optional[ServiceLifecycleManager] = None
_lock = threading.Lock()

def get_registry() -> ServiceRegistry:
    """Get global service registry"""
    global _registry
    if _registry is None:
        with _lock:
            if _registry is None:
                _registry = ServiceRegistry()
    return _registry

def get_factory() -> ServiceFactory:
    """Get global service factory"""
    global _factory
    if _factory is None:
        with _lock:
            if _factory is None:
                _factory = ServiceFactory()
    return _factory

def get_lifecycle_manager() -> ServiceLifecycleManager:
    """Get global service lifecycle manager"""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        with _lock:
            if _lifecycle_manager is None:
                _lifecycle_manager = ServiceLifecycleManager(get_registry())
    return _lifecycle_manager

def register_service_definition(definition: ServiceDefinition) -> None:
    """Register service definition in global registry"""
    get_registry().register_service_definition(definition)

def get_service(name: str) -> Optional[ServiceInterface]:
    """Get service from global registry"""
    return get_registry().get_service(name)

def start_all_services() -> Dict[str, bool]:
    """Start all services"""
    return get_lifecycle_manager().start_all_services()

def stop_all_services() -> Dict[str, bool]:
    """Stop all services"""
    return get_lifecycle_manager().stop_all_services()

def shutdown_service_management() -> None:
    """Shutdown service management"""
    global _registry, _factory, _lifecycle_manager

    if _lifecycle_manager:
        _lifecycle_manager.stop_all_services()

    _registry = None
    _factory = None
    _lifecycle_manager = None
