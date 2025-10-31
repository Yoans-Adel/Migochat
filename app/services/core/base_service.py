"""
Enhanced Base Service Classes for BWW Assistant Chatbot
Professional service base classes with comprehensive functionality
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional, List, Type, TypeVar
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager

from app.services.core.interfaces import ServiceInterface, ServiceHealth, ServiceStatus, ServiceConfig
from app.services.infrastructure.di_container import DependencyInjectionContainer, get_container

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ServiceState(Enum):
    """Service state enumeration"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"

@dataclass
class ServiceMetrics:
    """Service metrics"""
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    request_count: int = 0
    error_count: int = 0
    success_count: int = 0
    average_response_time: float = 0.0
    uptime_seconds: float = 0.0
    
    def update_uptime(self):
        """Update uptime"""
        self.uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
    
    def record_request(self, response_time: float, success: bool = True):
        """Record request metrics"""
        self.request_count += 1
        self.last_activity = datetime.now(timezone.utc)
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        
        # Update average response time
        if self.request_count == 1:
            self.average_response_time = response_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.request_count - 1) + response_time) 
                / self.request_count
            )

class BaseService(ABC):
    """Enhanced base service class with comprehensive functionality"""
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        self.config = config or ServiceConfig(
            name=self.__class__.__name__,
            enabled=True,
            timeout=30,
            retry_count=3,
            dependencies=[],
            config={}
        )
        
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._state = ServiceState.STOPPED
        self._initialized = False
        self._metrics = ServiceMetrics()
        self._dependencies: Dict[str, ServiceInterface] = {}
        self._health_checks: List[callable] = []
        self._startup_tasks: List[callable] = []
        self._shutdown_tasks: List[callable] = []
        
        # Performance monitoring
        self._performance_thresholds = {
            "max_response_time": 5.0,
            "max_error_rate": 0.1,
            "min_success_rate": 0.9
        }
    
    def initialize(self) -> bool:
        """Initialize the service"""
        if self._initialized:
            return True
        
        try:
            self._state = ServiceState.STARTING
            self.logger.info(f"Initializing {self.__class__.__name__}...")
            
            # Resolve dependencies
            self._resolve_dependencies()
            
            # Run startup tasks
            for task in self._startup_tasks:
                try:
                    if asyncio.iscoroutinefunction(task):
                        asyncio.run(task())
                    else:
                        task()
                except Exception as e:
                    self.logger.error(f"Startup task failed: {e}")
                    return False
            
            # Service-specific initialization
            if not self._do_initialize():
                self._state = ServiceState.ERROR
                return False
            
            self._initialized = True
            self._state = ServiceState.RUNNING
            self.logger.info(f"{self.__class__.__name__} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.__class__.__name__}: {e}")
            self._state = ServiceState.ERROR
            return False
    
    def _resolve_dependencies(self) -> None:
        """Resolve service dependencies"""
        container = get_container()
        
        for dep_name in self.config.dependencies:
            try:
                dependency = container.get_service(dep_name)
                if dependency:
                    self._dependencies[dep_name] = dependency
                    self.logger.debug(f"Resolved dependency: {dep_name}")
                else:
                    self.logger.warning(f"Could not resolve dependency: {dep_name}")
            except Exception as e:
                self.logger.error(f"Error resolving dependency {dep_name}: {e}")
    
    def get_dependency(self, name: str) -> Optional[ServiceInterface]:
        """Get dependency by name"""
        return self._dependencies.get(name)
    
    def add_startup_task(self, task: callable) -> None:
        """Add startup task"""
        self._startup_tasks.append(task)
    
    def add_shutdown_task(self, task: callable) -> None:
        """Add shutdown task"""
        self._shutdown_tasks.append(task)
    
    def add_health_check(self, check_func: callable) -> None:
        """Add health check function"""
        self._health_checks.append(check_func)
    
    @abstractmethod
    def _do_initialize(self) -> bool:
        """Service-specific initialization logic"""
        pass
    
    def shutdown(self) -> None:
        """Shutdown the service"""
        if self._state == ServiceState.STOPPED:
            return
        
        try:
            self._state = ServiceState.STOPPING
            self.logger.info(f"Shutting down {self.__class__.__name__}...")
            
            # Run shutdown tasks
            for task in reversed(self._shutdown_tasks):
                try:
                    if asyncio.iscoroutinefunction(task):
                        asyncio.run(task())
                    else:
                        task()
                except Exception as e:
                    self.logger.error(f"Shutdown task failed: {e}")
            
            # Service-specific shutdown
            self._do_shutdown()
            
            self._state = ServiceState.STOPPED
            self.logger.info(f"{self.__class__.__name__} shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            self._state = ServiceState.ERROR
    
    def _do_shutdown(self) -> None:
        """Service-specific shutdown logic"""
        pass
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        self._metrics.update_uptime()
        
        return {
            "service_name": self.__class__.__name__,
            "state": self._state.value,
            "initialized": self._initialized,
            "config": {
                "name": self.config.name,
                "enabled": self.config.enabled,
                "timeout": self.config.timeout,
                "retry_count": self.config.retry_count,
                "dependencies": self.config.dependencies
            },
            "metrics": {
                "uptime_seconds": self._metrics.uptime_seconds,
                "request_count": self._metrics.request_count,
                "error_count": self._metrics.error_count,
                "success_count": self._metrics.success_count,
                "average_response_time": self._metrics.average_response_time,
                "error_rate": self._metrics.error_count / max(self._metrics.request_count, 1),
                "success_rate": self._metrics.success_count / max(self._metrics.request_count, 1)
            },
            "dependencies": list(self._dependencies.keys()),
            "health_checks_count": len(self._health_checks),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def health_check(self) -> ServiceHealth:
        """Perform comprehensive health check"""
        try:
            status = ServiceStatus.HEALTHY
            messages = []
            metrics = {}
            
            # Check service state
            if self._state == ServiceState.ERROR:
                status = ServiceStatus.UNHEALTHY
                messages.append("Service is in error state")
            elif self._state == ServiceState.STOPPED:
                status = ServiceStatus.UNHEALTHY
                messages.append("Service is stopped")
            elif not self._initialized:
                status = ServiceStatus.UNHEALTHY
                messages.append("Service not initialized")
            
            # Check dependencies
            for dep_name, dependency in self._dependencies.items():
                if hasattr(dependency, 'health_check'):
                    dep_health = dependency.health_check()
                    if dep_health.status == ServiceStatus.UNHEALTHY:
                        status = ServiceStatus.DEGRADED
                        messages.append(f"Dependency {dep_name} is unhealthy")
            
            # Run custom health checks
            for check_func in self._health_checks:
                try:
                    result = check_func()
                    if not result:
                        status = ServiceStatus.DEGRADED
                        messages.append(f"Health check failed: {check_func.__name__}")
                except Exception as e:
                    status = ServiceStatus.DEGRADED
                    messages.append(f"Health check error: {e}")
            
            # Check performance metrics
            self._metrics.update_uptime()
            error_rate = self._metrics.error_count / max(self._metrics.request_count, 1)
            success_rate = self._metrics.success_count / max(self._metrics.request_count, 1)
            
            if error_rate > self._performance_thresholds["max_error_rate"]:
                status = ServiceStatus.DEGRADED
                messages.append(f"High error rate: {error_rate:.2%}")
            
            if success_rate < self._performance_thresholds["min_success_rate"]:
                status = ServiceStatus.DEGRADED
                messages.append(f"Low success rate: {success_rate:.2%}")
            
            if self._metrics.average_response_time > self._performance_thresholds["max_response_time"]:
                status = ServiceStatus.DEGRADED
                messages.append(f"Slow response time: {self._metrics.average_response_time:.2f}s")
            
            metrics = {
                "uptime_seconds": self._metrics.uptime_seconds,
                "request_count": self._metrics.request_count,
                "error_rate": error_rate,
                "success_rate": success_rate,
                "average_response_time": self._metrics.average_response_time
            }
            
            return ServiceHealth(
                status=status,
                message="; ".join(messages) if messages else "Service is healthy",
                timestamp=datetime.now(timezone.utc),
                metrics=metrics,
                dependencies=list(self._dependencies.keys())
            )
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return ServiceHealth(
                status=ServiceStatus.UNHEALTHY,
                message=f"Health check error: {e}",
                timestamp=datetime.now(timezone.utc),
                metrics={},
                dependencies=[]
            )
    
    def record_request(self, response_time: float, success: bool = True) -> None:
        """Record request metrics"""
        self._metrics.record_request(response_time, success)
    
    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        health = self.health_check()
        return health.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]
    
    def is_running(self) -> bool:
        """Check if service is running"""
        return self._state == ServiceState.RUNNING and self._initialized
    
    @asynccontextmanager
    async def request_context(self, operation_name: str):
        """Context manager for request tracking"""
        start_time = time.time()
        success = True
        
        try:
            self.logger.debug(f"Starting {operation_name}")
            yield
        except Exception as e:
            success = False
            self.logger.error(f"Error in {operation_name}: {e}")
            raise
        finally:
            response_time = time.time() - start_time
            self.record_request(response_time, success)
            self.logger.debug(f"Completed {operation_name} in {response_time:.3f}s")

class DatabaseService(BaseService):
    """Enhanced database service base class"""
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        super().__init__(config)
        self._session_pool = None
        self._connection_pool = None
    
    def _do_initialize(self) -> bool:
        """Initialize database service"""
        try:
            # Add database-specific health check
            self.add_health_check(self._check_database_connection)
            return True
        except Exception as e:
            self.logger.error(f"Database service initialization failed: {e}")
            return False
    
    def _check_database_connection(self) -> bool:
        """Check database connection health"""
        try:
            # Implement database connection check
            return True
        except Exception as e:
            self.logger.error(f"Database connection check failed: {e}")
            return False
    
    @abstractmethod
    def get_session(self):
        """Get database session"""
        pass

class APIService(BaseService):
    """Enhanced API service base class"""
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        super().__init__(config)
        self.base_url: str = ""
        self.headers: Dict[str, str] = {}
        self.timeout: int = 30
        self.retry_count: int = 3
    
    def _do_initialize(self) -> bool:
        """Initialize API service"""
        try:
            # Add API-specific health check
            self.add_health_check(self._check_api_connectivity)
            return True
        except Exception as e:
            self.logger.error(f"API service initialization failed: {e}")
            return False
    
    def _check_api_connectivity(self) -> bool:
        """Check API connectivity"""
        try:
            # Implement API connectivity check
            return True
        except Exception as e:
            self.logger.error(f"API connectivity check failed: {e}")
            return False
    
    @abstractmethod
    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request"""
        pass

class MessageService(BaseService):
    """Enhanced message service base class"""
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        super().__init__(config)
        self.platform: str = ""
    
    def _do_initialize(self) -> bool:
        """Initialize message service"""
        try:
            # Add message-specific health check
            self.add_health_check(self._check_message_service)
            return True
        except Exception as e:
            self.logger.error(f"Message service initialization failed: {e}")
            return False
    
    def _check_message_service(self) -> bool:
        """Check message service health"""
        try:
            # Implement message service health check
            return True
        except Exception as e:
            self.logger.error(f"Message service health check failed: {e}")
            return False
    
    @abstractmethod
    def send_message(self, recipient_id: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send message to recipient"""
        pass
    
    @abstractmethod
    def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message"""
        pass

class AIService(BaseService):
    """Enhanced AI service base class"""
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        super().__init__(config)
        self.model_loaded: bool = False
        self.model = None
    
    def _do_initialize(self) -> bool:
        """Initialize AI service"""
        try:
            # Add AI-specific health check
            self.add_health_check(self._check_ai_model)
            return True
        except Exception as e:
            self.logger.error(f"AI service initialization failed: {e}")
            return False
    
    def _check_ai_model(self) -> bool:
        """Check AI model health"""
        try:
            return self.model_loaded and self.model is not None
        except Exception as e:
            self.logger.error(f"AI model health check failed: {e}")
            return False
    
    @abstractmethod
    def generate_response(self, message: str, context: Optional[Dict] = None) -> str:
        """Generate AI response"""
        pass
    
    @abstractmethod
    def detect_intent(self, message: str) -> Dict[str, Any]:
        """Detect user intent"""
        pass

class LeadService(BaseService):
    """Enhanced lead service base class"""
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        super().__init__(config)
        self.lead_stages: List[str] = []
        self.customer_types: List[str] = []
    
    def _do_initialize(self) -> bool:
        """Initialize lead service"""
        try:
            # Initialize lead-specific data
            self.lead_stages = ["Intake", "Qualified", "In-Progress", "Converted"]
            self.customer_types = ["SCARCITY_BUYER", "EMOTIONAL_BUYER", "VALUE_SEEKER", 
                                  "LOYAL_BUYER", "LOGICAL_BUYER", "BARGAIN_HUNTER", "HESITANT_BUYER"]
            
            # Add lead-specific health check
            self.add_health_check(self._check_lead_service)
            return True
        except Exception as e:
            self.logger.error(f"Lead service initialization failed: {e}")
            return False
    
    def _check_lead_service(self) -> bool:
        """Check lead service health"""
        try:
            return len(self.lead_stages) > 0 and len(self.customer_types) > 0
        except Exception as e:
            self.logger.error(f"Lead service health check failed: {e}")
            return False
    
    @abstractmethod
    def classify_lead(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify lead"""
        pass
    
    @abstractmethod
    def calculate_lead_score(self, user: Any) -> int:
        """Calculate lead score"""
        pass

class ProductService(BaseService):
    """Enhanced product service base class"""
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        super().__init__(config)
        self.product_cache: Dict[str, Any] = {}
    
    def _do_initialize(self) -> bool:
        """Initialize product service"""
        try:
            # Add product-specific health check
            self.add_health_check(self._check_product_service)
            return True
        except Exception as e:
            self.logger.error(f"Product service initialization failed: {e}")
            return False
    
    def _check_product_service(self) -> bool:
        """Check product service health"""
        try:
            # Implement product service health check
            return True
        except Exception as e:
            self.logger.error(f"Product service health check failed: {e}")
            return False
    
    @abstractmethod
    def search_products(self, query: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Search products"""
        pass
    
    @abstractmethod
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get product details"""
        pass
