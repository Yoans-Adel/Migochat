"""
Minimal base service and error-handling decorators for the standalone BWW client.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, TypeVar, cast

from .models import APIResponse

logger = logging.getLogger(__name__)


class APIService:
    """Lightweight base class to align with previous usage patterns."""

    def __init__(self) -> None:
        # Mark as initialized to satisfy status checks in existing tests/usages
        self._initialized: bool = True

    # Concrete clients must implement this
    def make_request(self, method: str, endpoint: str, **kwargs: Any) -> Any:  # pragma: no cover - interface
        raise NotImplementedError


@dataclass
class RetryConfig:
    max_retries: int = 3
    delay: float = 1.0


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    reset_timeout: float = 60.0


F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


def api_error_handler(func: F) -> F:
    """Capture unexpected errors and return a consistent APIResponse for async call sites."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> APIResponse:
        try:
            return await func(*args, **kwargs)
        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            logger.error("Expected error in %s: %s", func.__name__, exc)
            return APIResponse(success=False, error=str(exc), status_code=500)
        except Exception as exc:
            logger.exception("Unexpected error in %s: %s", func.__name__, exc)
            return APIResponse(success=False, error=str(exc), status_code=500)

    return cast(F, wrapper)


def retry_on_error(config: RetryConfig) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> APIResponse:
            attempt = 0
            last_error: Optional[str] = None
            while attempt <= config.max_retries:
                try:
                    return await func(*args, **kwargs)
                except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, ConnectionError, TimeoutError) as exc:
                    last_error = str(exc)
                    attempt += 1
                    if attempt > config.max_retries:
                        break
                    logger.debug("Retry attempt %d/%d for %s: %s", attempt, config.max_retries, func.__name__, exc)
                    await asyncio.sleep(config.delay)
                except Exception as exc:
                    # Unexpected errors should not be retried
                    logger.exception("Unexpected error in %s (not retrying): %s", func.__name__, exc)
                    return APIResponse(success=False, error=str(exc), status_code=500)
            return APIResponse(success=False, error=last_error or "retry failed", status_code=500)

        return cast(F, wrapper)

    return decorator


def circuit_breaker(name: str, config: CircuitBreakerConfig) -> Callable[[F], F]:
    state: dict[str, Any] = {"failures": 0, "open_until": 0.0}

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> APIResponse:
            import time

            now = time.time()
            if state["failures"] >= config.failure_threshold and now < state["open_until"]:
                logger.warning("Circuit breaker %s is OPEN", name)
                return APIResponse(success=False, error="Circuit breaker is open", status_code=503)

            try:
                result = await func(*args, **kwargs)
                # close the circuit on success
                state["failures"] = 0
                return result
            except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, ConnectionError, TimeoutError) as exc:
                state["failures"] += 1
                if state["failures"] >= config.failure_threshold:
                    state["open_until"] = now + config.reset_timeout
                    logger.warning("Circuit breaker %s tripped (failures=%s)", name, state["failures"])
                logger.error("Error in circuit breaker %s: %s", name, exc)
                return APIResponse(success=False, error=str(exc), status_code=500)
            except Exception as exc:
                # Unexpected errors increment counter but log as critical
                state["failures"] += 1
                if state["failures"] >= config.failure_threshold:
                    state["open_until"] = now + config.reset_timeout
                logger.exception("Unexpected error in circuit breaker %s (failures=%s)", name, state["failures"])
                return APIResponse(success=False, error=str(exc), status_code=500)

        return cast(F, wrapper)

    return decorator
