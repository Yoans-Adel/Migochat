"""
Service Interfaces for BWW Assistant Chatbot
Defines contracts and interfaces for all services
"""

from typing import Dict, Any, Optional, List, Protocol, runtime_checkable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """Service health information"""
    status: ServiceStatus
    message: str
    timestamp: datetime
    metrics: Dict[str, Any]
    dependencies: List[str]


@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    enabled: bool
    timeout: int
    retry_count: int
    dependencies: List[str]
    config: Dict[str, Any]


@runtime_checkable
class ServiceInterface(Protocol):
    """Base service interface"""

    def initialize(self) -> bool:
        """Initialize the service"""
        ...

    def shutdown(self) -> None:
        """Shutdown the service"""
        ...

    def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        ...

    def health_check(self) -> ServiceHealth:
        """Perform health check"""
        ...

# DatabaseServiceInterface removed - archived with database_service_professional.py
# Database operations now handled directly through app.database module


class AIServiceInterface(ServiceInterface, Protocol):
    """AI service interface"""

    def generate_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate AI response"""
        ...

    def detect_intent(self, message: str) -> Dict[str, Any]:
        """Detect user intent"""
        ...

    def extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities from message"""
        ...


class MessageServiceInterface(ServiceInterface, Protocol):
    """Message service interface"""

    def send_message(self, recipient_id: str, message: str, **kwargs: Any) -> Dict[str, Any]:
        """Send message to recipient"""
        ...

    def process_message(self, message_data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Process incoming message"""
        ...


class APIServiceInterface(ServiceInterface, Protocol):
    """API service interface"""

    def make_request(self, method: str, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Make API request"""
        ...

    def get_headers(self) -> Dict[str, str]:
        """Get API headers"""
        ...


class LeadServiceInterface(ServiceInterface, Protocol):
    """Lead management service interface"""

    def classify_lead(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify lead"""
        ...

    def calculate_lead_score(self, user: Any) -> int:
        """Calculate lead score"""
        ...

    def update_lead_stage(self, user: Any, stage: str) -> bool:
        """Update lead stage"""
        ...


class ProductServiceInterface(ServiceInterface, Protocol):
    """Product service interface"""

    def search_products(self, query: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search products"""
        ...

    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get product details"""
        ...

    def get_product_recommendations(self, user: Any) -> List[Dict[str, Any]]:
        """Get product recommendations"""
        ...


class NotificationServiceInterface(ServiceInterface, Protocol):
    """Notification service interface"""

    def send_notification(self, recipient: str, message: str, **kwargs: Any) -> bool:
        """Send notification"""
        ...

    def schedule_notification(self, recipient: str, message: str, delay: int) -> str:
        """Schedule notification"""
        ...


class AnalyticsServiceInterface(ServiceInterface, Protocol):
    """Analytics service interface"""

    def track_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Track analytics event"""
        ...

    def get_analytics(self, time_range: str) -> Dict[str, Any]:
        """Get analytics data"""
        ...


class CacheServiceInterface(ServiceInterface, Protocol):
    """Cache service interface"""

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        ...

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        ...

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        ...

    def clear(self) -> bool:
        """Clear all cache"""
        ...


class SecurityServiceInterface(ServiceInterface, Protocol):
    """Security service interface"""

    def validate_token(self, token: str) -> bool:
        """Validate security token"""
        ...

    def encrypt_data(self, data: str) -> str:
        """Encrypt data"""
        ...

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        ...


class ConfigurationServiceInterface(ServiceInterface, Protocol):
    """Configuration service interface"""

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        ...

    def set_config(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        ...

    def reload_config(self) -> bool:
        """Reload configuration"""
        ...


class LoggingServiceInterface(ServiceInterface, Protocol):
    """Logging service interface"""

    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message"""
        ...

    def log_error(self, message: str, error: Optional[Exception] = None, **kwargs: Any) -> None:
        """Log error message"""
        ...

    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message"""
        ...

    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message"""
        ...


class ServiceRegistryInterface(Protocol):
    """Service registry interface"""

    def register_service(self, name: str, service: ServiceInterface) -> None:
        """Register service"""
        ...

    def get_service(self, name: str) -> Optional[ServiceInterface]:
        """Get service by name"""
        ...

    def unregister_service(self, name: str) -> bool:
        """Unregister service"""
        ...

    def list_services(self) -> List[str]:
        """List all registered services"""
        ...

    def get_service_dependencies(self, name: str) -> List[str]:
        """Get service dependencies"""
        ...


class ServiceFactoryInterface(Protocol):
    """Service factory interface"""

    def create_service(self, service_type: str, config: ServiceConfig) -> ServiceInterface:
        """Create service instance"""
        ...

    def get_supported_services(self) -> List[str]:
        """Get list of supported service types"""
        ...


class ServiceLifecycleInterface(Protocol):
    """Service lifecycle management interface"""

    def start_service(self, name: str) -> bool:
        """Start service"""
        ...

    def stop_service(self, name: str) -> bool:
        """Stop service"""
        ...

    def restart_service(self, name: str) -> bool:
        """Restart service"""
        ...

    def get_service_status(self, name: str) -> ServiceStatus:
        """Get service status"""
        ...

    def get_all_services_status(self) -> Dict[str, ServiceStatus]:
        """Get all services status"""
        ...
