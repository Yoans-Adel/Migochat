"""
Dependency Injection Container for BWW Assistant Chatbot
Professional dependency injection implementation
"""

import logging
import threading
from typing import Dict, Any, Optional, Type, TypeVar, Callable, List
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

from app.services.core.interfaces import ServiceInterface, ServiceConfig, ServiceStatus

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=ServiceInterface)

class ServiceScope(Enum):
    """Service scope enumeration"""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

@dataclass
class ServiceRegistration:
    """Service registration information"""
    service_type: Type[ServiceInterface]
    implementation: Optional[Type[ServiceInterface]] = None
    factory: Optional[Callable[[], ServiceInterface]] = None
    instance: Optional[ServiceInterface] = None
    scope: ServiceScope = ServiceScope.SINGLETON
    config: Optional[ServiceConfig] = None
    dependencies: List[str] = None

class DependencyInjectionContainer:
    """Professional dependency injection container"""
    
    def __init__(self):
        self._services: Dict[str, ServiceRegistration] = {}
        self._instances: Dict[str, ServiceInterface] = {}
        self._lock = threading.RLock()
        self._logger = logging.getLogger(__name__)
    
    def register_singleton(self, name: str, service_type: Type[T], 
                          implementation: Optional[Type[T]] = None,
                          factory: Optional[Callable[[], T]] = None,
                          config: Optional[ServiceConfig] = None) -> 'DependencyInjectionContainer':
        """Register singleton service"""
        return self._register_service(name, service_type, implementation, factory, 
                                    ServiceScope.SINGLETON, config)
    
    def register_transient(self, name: str, service_type: Type[T],
                          implementation: Optional[Type[T]] = None,
                          factory: Optional[Callable[[], T]] = None,
                          config: Optional[ServiceConfig] = None) -> 'DependencyInjectionContainer':
        """Register transient service"""
        return self._register_service(name, service_type, implementation, factory,
                                    ServiceScope.TRANSIENT, config)
    
    def register_scoped(self, name: str, service_type: Type[T],
                       implementation: Optional[Type[T]] = None,
                       factory: Optional[Callable[[], T]] = None,
                       config: Optional[ServiceConfig] = None) -> 'DependencyInjectionContainer':
        """Register scoped service"""
        return self._register_service(name, service_type, implementation, factory,
                                    ServiceScope.SCOPED, config)
    
    def _register_service(self, name: str, service_type: Type[T],
                          implementation: Optional[Type[T]] = None,
                          factory: Optional[Callable[[], T]] = None,
                          scope: ServiceScope = ServiceScope.SINGLETON,
                          config: Optional[ServiceConfig] = None) -> 'DependencyInjectionContainer':
        """Internal service registration"""
        with self._lock:
            if name in self._services:
                self._logger.warning(f"Service '{name}' is already registered. Overwriting.")
            
            self._services[name] = ServiceRegistration(
                service_type=service_type,
                implementation=implementation or service_type,
                factory=factory,
                scope=scope,
                config=config,
                dependencies=[]
            )
            
            self._logger.info(f"Registered service '{name}' with scope '{scope.value}'")
        
        return self
    
    def get_service(self, name: str) -> Optional[ServiceInterface]:
        """Get service instance"""
        with self._lock:
            if name not in self._services:
                self._logger.error(f"Service '{name}' not registered")
                return None
            
            registration = self._services[name]
            
            # Return existing instance for singleton
            if registration.scope == ServiceScope.SINGLETON:
                if name in self._instances:
                    return self._instances[name]
            
            # Create new instance
            instance = self._create_service_instance(registration)
            if not instance:
                return None
            
            # Store instance for singleton
            if registration.scope == ServiceScope.SINGLETON:
                self._instances[name] = instance
            
            return instance
    
    def get_service_by_type(self, service_type: Type[T]) -> Optional[T]:
        """Get service by type"""
        with self._lock:
            for name, registration in self._services.items():
                if registration.service_type == service_type:
                    return self.get_service(name)
            return None
    
    def _create_service_instance(self, registration: ServiceRegistration) -> Optional[ServiceInterface]:
        """Create service instance"""
        try:
            if registration.factory:
                instance = registration.factory()
            else:
                # Resolve dependencies
                dependencies = self._resolve_dependencies(registration)
                instance = registration.implementation(**dependencies)
            
            # Initialize service if it has initialize method
            if hasattr(instance, 'initialize'):
                if not instance.initialize():
                    self._logger.error(f"Failed to initialize service '{registration.service_type.__name__}'")
                    return None
            
            return instance
            
        except Exception as e:
            self._logger.error(f"Failed to create service instance: {e}")
            return None
    
    def _resolve_dependencies(self, registration: ServiceRegistration) -> Dict[str, Any]:
        """Resolve service dependencies"""
        dependencies = {}
        
        # Add configuration if available
        if registration.config:
            dependencies['config'] = registration.config
        
        # Resolve other dependencies based on constructor parameters
        if hasattr(registration.implementation, '__init__'):
            import inspect
            sig = inspect.signature(registration.implementation.__init__)
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                # Try to resolve dependency by type annotation
                if param.annotation != inspect.Parameter.empty:
                    dependency = self.get_service_by_type(param.annotation)
                    if dependency:
                        dependencies[param_name] = dependency
        
        return dependencies
    
    def is_registered(self, name: str) -> bool:
        """Check if service is registered"""
        return name in self._services
    
    def unregister_service(self, name: str) -> bool:
        """Unregister service"""
        with self._lock:
            if name not in self._services:
                return False
            
            # Shutdown existing instance
            if name in self._instances:
                instance = self._instances[name]
                if hasattr(instance, 'shutdown'):
                    try:
                        instance.shutdown()
                    except Exception as e:
                        self._logger.error(f"Error shutting down service '{name}': {e}")
                
                del self._instances[name]
            
            del self._services[name]
            self._logger.info(f"Unregistered service '{name}'")
            return True
    
    def get_all_services(self) -> Dict[str, ServiceInterface]:
        """Get all service instances"""
        with self._lock:
            services = {}
            for name in self._services:
                service = self.get_service(name)
                if service:
                    services[name] = service
            return services
    
    def shutdown_all(self) -> None:
        """Shutdown all services"""
        with self._lock:
            self._logger.info("Shutting down all services...")
            
            # Shutdown in reverse order of registration
            for name in reversed(list(self._instances.keys())):
                instance = self._instances[name]
                if hasattr(instance, 'shutdown'):
                    try:
                        instance.shutdown()
                        self._logger.info(f"Shutdown service '{name}'")
                    except Exception as e:
                        self._logger.error(f"Error shutting down service '{name}': {e}")
            
            self._instances.clear()
            self._services.clear()
    
    def get_service_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get service information"""
        with self._lock:
            if name not in self._services:
                return None
            
            registration = self._services[name]
            instance = self._instances.get(name)
            
            info = {
                "name": name,
                "service_type": registration.service_type.__name__,
                "implementation": registration.implementation.__name__,
                "scope": registration.scope.value,
                "has_instance": name in self._instances,
                "has_config": registration.config is not None,
                "dependencies": registration.dependencies
            }
            
            if instance and hasattr(instance, 'get_service_status'):
                info["status"] = instance.get_service_status()
            
            return info
    
    def get_all_services_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all services"""
        with self._lock:
            return {name: self.get_service_info(name) for name in self._services.keys()}
    
    @contextmanager
    def scoped_context(self):
        """Create scoped context for scoped services"""
        scoped_instances = {}
        
        try:
            # Create scoped instances
            for name, registration in self._services.items():
                if registration.scope == ServiceScope.SCOPED:
                    instance = self._create_service_instance(registration)
                    if instance:
                        scoped_instances[name] = instance
            
            # Temporarily replace singleton instances with scoped ones
            original_instances = {}
            for name, instance in scoped_instances.items():
                if name in self._instances:
                    original_instances[name] = self._instances[name]
                self._instances[name] = instance
            
            yield scoped_instances
            
        finally:
            # Restore original instances
            for name in scoped_instances:
                if name in original_instances:
                    self._instances[name] = original_instances[name]
                elif name in self._instances:
                    del self._instances[name]
            
            # Shutdown scoped instances
            for instance in scoped_instances.values():
                if hasattr(instance, 'shutdown'):
                    try:
                        instance.shutdown()
                    except Exception as e:
                        self._logger.error(f"Error shutting down scoped service: {e}")

# Global DI container instance
_di_container: Optional[DependencyInjectionContainer] = None
_container_lock = threading.Lock()

def get_container() -> DependencyInjectionContainer:
    """Get global DI container instance"""
    global _di_container
    
    if _di_container is None:
        with _container_lock:
            if _di_container is None:
                _di_container = DependencyInjectionContainer()
    
    return _di_container

def register_service(name: str, service_type: Type[T], 
                    implementation: Optional[Type[T]] = None,
                    factory: Optional[Callable[[], T]] = None,
                    scope: ServiceScope = ServiceScope.SINGLETON,
                    config: Optional[ServiceConfig] = None) -> DependencyInjectionContainer:
    """Register service in global container"""
    container = get_container()
    
    if scope == ServiceScope.SINGLETON:
        return container.register_singleton(name, service_type, implementation, factory, config)
    elif scope == ServiceScope.TRANSIENT:
        return container.register_transient(name, service_type, implementation, factory, config)
    elif scope == ServiceScope.SCOPED:
        return container.register_scoped(name, service_type, implementation, factory, config)
    else:
        raise ValueError(f"Unknown scope: {scope}")

def get_service(name: str) -> Optional[ServiceInterface]:
    """Get service from global container"""
    return get_container().get_service(name)

def get_service_by_type(service_type: Type[T]) -> Optional[T]:
    """Get service by type from global container"""
    return get_container().get_service_by_type(service_type)

def shutdown_container() -> None:
    """Shutdown global container"""
    global _di_container
    if _di_container:
        _di_container.shutdown_all()
        _di_container = None
