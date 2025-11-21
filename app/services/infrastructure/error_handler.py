"""
Enhanced Error Handling and Monitoring for BWW Assistant Chatbot
Professional error handling with circuit breakers, retry logic, and monitoring
"""

import logging
import time
import asyncio
import threading
from typing import Dict, Any, Optional, List, Callable, Type, TypeVar, Tuple, cast
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import wraps
import traceback
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

# Type variables for generic decorators
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""
    NETWORK = "network"
    DATABASE = "database"
    API = "api"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL = "internal"
    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"


@dataclass
class ErrorContext:
    """Error context information"""
    service_name: str
    operation: str
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=lambda: {})


@dataclass
class ErrorRecord:
    """Error record for tracking and analysis"""
    error_id: str
    error_type: str
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    stack_trace: Optional[str] = None
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    retry_count: int = 0
    last_occurrence: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    occurrence_count: int = 1


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service is back


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: Type[Exception] = Exception
    success_threshold: int = 3


class CircuitBreaker:
    """Circuit breaker implementation"""

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.logger = logging.getLogger(f"{__name__}.CircuitBreaker.{name}")
        self._lock = threading.Lock()

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.success_count = 0
                    self.logger.info(f"Circuit breaker '{self.name}' moved to HALF_OPEN")
                else:
                    raise Exception(f"Circuit breaker '{self.name}' is OPEN")

            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.config.expected_exception as e:
                self._on_failure()
                raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if self.last_failure_time is None:
            return True

        return (datetime.now(timezone.utc) - self.last_failure_time).total_seconds() >= self.config.recovery_timeout

    def _on_success(self) -> None:
        """Handle successful operation"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.logger.info(f"Circuit breaker '{self.name}' moved to CLOSED")
        else:
            self.failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning(f"Circuit breaker '{self.name}' moved to OPEN (HALF_OPEN failure)")
        elif self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning(f"Circuit breaker '{self.name}' moved to OPEN (failure threshold reached)")


class RetryConfig:
    """Retry configuration"""
    def __init__(self, max_retries: int = 3, delay: float = 1.0,
                 backoff_factor: float = 2.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay


def retry_on_error(
    config: Optional[RetryConfig] = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable[[F], F]:
    """Retry decorator with exponential backoff"""
    # Ensure config is never None inside decorator
    retry_config = config if config is not None else RetryConfig()

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None

            for attempt in range(retry_config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == retry_config.max_retries:
                        logger.error(f"Function {func.__name__} failed after {retry_config.max_retries} retries: {e}")
                        raise e

                    delay = min(retry_config.delay * (retry_config.backoff_factor ** attempt), retry_config.max_delay)
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{retry_config.max_retries + 1}): {e}. "
                        f"Retrying in {delay}s"
                    )
                    time.sleep(delay)

            if last_exception:
                raise last_exception
            raise RuntimeError("Retry logic failed unexpectedly")

        return cast(F, wrapper)
    return decorator


def async_retry_on_error(
    config: Optional[RetryConfig] = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable[[F], F]:
    """Async retry decorator with exponential backoff"""
    # Ensure config is never None inside decorator
    retry_config = config if config is not None else RetryConfig()

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None

            for attempt in range(retry_config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == retry_config.max_retries:
                        logger.error(f"Async function {func.__name__} failed after {retry_config.max_retries} retries: {e}")
                        raise e

                    delay = min(retry_config.delay * (retry_config.backoff_factor ** attempt), retry_config.max_delay)
                    logger.warning(
                        f"Async function {func.__name__} failed (attempt {attempt + 1}/{retry_config.max_retries + 1}): {e}. "
                        f"Retrying in {delay}s"
                    )
                    await asyncio.sleep(delay)

            if last_exception:
                raise last_exception
            raise RuntimeError("Async retry logic failed unexpectedly")

        return cast(F, wrapper)
    return decorator


class ErrorMonitor:
    """Error monitoring and analysis system"""

    def __init__(self):
        self._errors: Dict[str, ErrorRecord] = {}
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._error_timeline: deque[Dict[str, Any]] = deque(maxlen=1000)
        self._lock = threading.RLock()
        self._logger = logging.getLogger(__name__)

    def record_error(self, error: Exception, context: ErrorContext,
                     severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                     category: ErrorCategory = ErrorCategory.INTERNAL) -> str:
        """Record error for monitoring"""
        with self._lock:
            error_id = f"{context.service_name}_{context.operation}_{int(time.time())}"

            # Check if this is a recurring error
            error_key = f"{type(error).__name__}_{context.service_name}_{context.operation}"

            if error_key in self._errors:
                # Update existing error record
                record = self._errors[error_key]
                record.occurrence_count += 1
                record.last_occurrence = datetime.now(timezone.utc)
                record.retry_count += 1
            else:
                # Create new error record
                record = ErrorRecord(
                    error_id=error_id,
                    error_type=type(error).__name__,
                    message=str(error),
                    severity=severity,
                    category=category,
                    context=context,
                    stack_trace=traceback.format_exc()
                )
                self._errors[error_key] = record

            self._error_counts[error_key] += 1
            self._error_timeline.append({
                "timestamp": datetime.now(timezone.utc),
                "error_key": error_key,
                "severity": severity.value,
                "category": category.value
            })

            self._logger.error(f"Error recorded: {error_key} - {error}")
            return error_key

    def get_error_stats(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get error statistics for time window"""
        with self._lock:
            cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=time_window)

            recent_errors = [
                error for error in self._error_timeline
                if error["timestamp"] >= cutoff_time
            ]

            stats: Dict[str, Any] = {
                "total_errors": len(recent_errors),
                "error_types": defaultdict(int),
                "severity_counts": defaultdict(int),
                "category_counts": defaultdict(int),
                "service_counts": defaultdict(int),
                "time_window_seconds": time_window
            }

            for error in recent_errors:
                error_key = error["error_key"]
                if error_key in self._errors:
                    record = self._errors[error_key]
                    stats["error_types"][record.error_type] += 1
                    stats["severity_counts"][record.severity.value] += 1
                    stats["category_counts"][record.category.value] += 1
                    stats["service_counts"][record.context.service_name] += 1

            return stats

    def get_top_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top errors by occurrence count"""
        with self._lock:
            sorted_errors = sorted(
                self._errors.items(),
                key=lambda x: x[1].occurrence_count,
                reverse=True
            )

            return [
                {
                    "error_key": key,
                    "error_type": record.error_type,
                    "message": record.message,
                    "severity": record.severity.value,
                    "category": record.category.value,
                    "occurrence_count": record.occurrence_count,
                    "last_occurrence": record.last_occurrence.isoformat(),
                    "service_name": record.context.service_name,
                    "operation": record.context.operation
                }
                for key, record in sorted_errors[:limit]
            ]

    def resolve_error(self, error_key: str) -> bool:
        """Mark error as resolved"""
        with self._lock:
            if error_key in self._errors:
                self._errors[error_key].resolved = True
                self._errors[error_key].resolution_time = datetime.now(timezone.utc)
                self._logger.info(f"Error resolved: {error_key}")
                return True
            return False


class ErrorHandler:
    """Professional error handling system"""

    def __init__(self):
        self._monitor = ErrorMonitor()
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._error_handlers: Dict[ErrorCategory, List[Callable[[Exception, ErrorContext], None]]] = defaultdict(list)
        self._logger = logging.getLogger(__name__)

    def register_error_handler(self, category: ErrorCategory, handler: Callable[[Exception, ErrorContext], None]) -> None:
        """Register error handler for specific category"""
        self._error_handlers[category].append(handler)
        self._logger.info(f"Registered error handler for category {category.value}")

    def create_circuit_breaker(self, name: str, config: CircuitBreakerConfig) -> CircuitBreaker:
        """Create circuit breaker"""
        circuit_breaker = CircuitBreaker(name, config)
        self._circuit_breakers[name] = circuit_breaker
        self._logger.info(f"Created circuit breaker '{name}'")
        return circuit_breaker

    def handle_error(self, error: Exception, context: ErrorContext,
                     severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                     category: ErrorCategory = ErrorCategory.INTERNAL) -> str:
        """Handle error with monitoring and recovery"""
        # Record error
        error_key = self._monitor.record_error(error, context, severity, category)

        # Execute category-specific handlers
        handlers = self._error_handlers.get(category, [])
        for handler in handlers:
            try:
                handler(error, context)
            except Exception as e:
                self._logger.error(f"Error handler failed: {e}")

        # Log error based on severity
        if severity == ErrorSeverity.CRITICAL:
            self._logger.critical(f"CRITICAL ERROR: {error}")
        elif severity == ErrorSeverity.HIGH:
            self._logger.error(f"HIGH SEVERITY ERROR: {error}")
        elif severity == ErrorSeverity.MEDIUM:
            self._logger.warning(f"MEDIUM SEVERITY ERROR: {error}")
        else:
            self._logger.info(f"LOW SEVERITY ERROR: {error}")

        return error_key

    def get_error_monitor(self) -> ErrorMonitor:
        """Get error monitor instance"""
        return self._monitor

    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        return self._circuit_breakers.get(name)

    def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        return {
            name: {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "success_count": breaker.success_count,
                "last_failure_time": breaker.last_failure_time.isoformat() if breaker.last_failure_time else None
            }
            for name, breaker in self._circuit_breakers.items()
        }

# Service-specific error handlers


def database_error_handler(func: F) -> F:
    """Database error handler decorator"""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = ErrorContext(
                service_name="DatabaseService",
                operation=func.__name__
            )
            error_handler = get_error_handler()
            error_handler.handle_error(e, context, ErrorSeverity.HIGH, ErrorCategory.DATABASE)
            raise
    return cast(F, wrapper)


def api_error_handler(func: F) -> F:
    """API error handler decorator"""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = ErrorContext(
                service_name="APIService",
                operation=func.__name__
            )
            error_handler = get_error_handler()
            error_handler.handle_error(e, context, ErrorSeverity.MEDIUM, ErrorCategory.API)
            raise
    return cast(F, wrapper)


def ai_error_handler(func: F) -> F:
    """AI service error handler decorator"""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = ErrorContext(
                service_name="AIService",
                operation=func.__name__
            )
            error_handler = get_error_handler()
            error_handler.handle_error(e, context, ErrorSeverity.MEDIUM, ErrorCategory.EXTERNAL_SERVICE)
            raise
    return cast(F, wrapper)


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None
_error_handler_lock = threading.Lock()


def get_error_handler() -> ErrorHandler:
    """Get global error handler"""
    global _error_handler

    if _error_handler is None:
        with _error_handler_lock:
            if _error_handler is None:
                _error_handler = ErrorHandler()

    return _error_handler


def create_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
    """Create circuit breaker in global error handler"""
    if config is None:
        config = CircuitBreakerConfig()

    return get_error_handler().create_circuit_breaker(name, config)


def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None) -> Callable[[F], F]:
    """Circuit breaker decorator"""
    if config is None:
        config = CircuitBreakerConfig()

    def decorator(func: F) -> F:
        breaker = get_error_handler().get_circuit_breaker(name)
        if breaker is None:
            breaker = get_error_handler().create_circuit_breaker(name, config)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return breaker.call(func, *args, **kwargs)

        return cast(F, wrapper)
    return decorator
