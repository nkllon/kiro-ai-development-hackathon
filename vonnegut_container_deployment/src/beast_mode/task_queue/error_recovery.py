"""
Error handling and recovery mechanisms for TaskQueueManager

This module implements comprehensive error handling with graceful degradation,
exponential backoff retry logic, and circuit breaker patterns.
"""

import asyncio
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import functools


class ErrorType(Enum):
    """Types of errors that can occur in the task queue system."""
    REDIS_CONNECTION_ERROR = "redis_connection_error"
    REDIS_TIMEOUT_ERROR = "redis_timeout_error"
    TASK_PROCESSING_ERROR = "task_processing_error"
    STATE_PERSISTENCE_ERROR = "state_persistence_error"
    VALIDATION_ERROR = "validation_error"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    UNKNOWN_ERROR = "unknown_error"


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types."""
    EXPONENTIAL_BACKOFF_RETRY = "exponential_backoff_retry"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    FALLBACK_MODE = "fallback_mode"
    IMMEDIATE_FAILURE = "immediate_failure"


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    exponential_base: float = 2.0
    jitter_factor: float = 0.1


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern."""
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 30
    half_open_max_calls: int = 3


@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    error_id: str
    error_type: ErrorType
    timestamp: datetime
    error_message: str
    recovery_strategy: RecoveryStrategy
    retry_count: int = 0
    resolved: bool = False


class CircuitBreaker:
    """Circuit breaker implementation for protecting against cascading failures."""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self._state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._failure_count = 0
        self._last_failure_time = None
        self._half_open_calls = 0
        self._logger = logging.getLogger(f"{__name__}.CircuitBreaker")

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function through circuit breaker."""
        if self._state == "OPEN":
            if self._should_attempt_reset():
                self._state = "HALF_OPEN"
                self._half_open_calls = 0
                self._logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        if self._state == "HALF_OPEN":
            if self._half_open_calls >= self.config.half_open_max_calls:
                raise CircuitBreakerOpenError("Circuit breaker HALF_OPEN call limit exceeded")

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Success - handle state transitions
            if self._state == "HALF_OPEN":
                self._half_open_calls += 1
                if self._half_open_calls >= self.config.half_open_max_calls:
                    self._state = "CLOSED"
                    self._failure_count = 0
                    self._logger.info("Circuit breaker reset to CLOSED")

            return result

        except Exception as e:
            self._failure_count += 1
            self._last_failure_time = datetime.now()

            if self._state == "HALF_OPEN":
                self._state = "OPEN"
                self._logger.warning("Circuit breaker reopened after HALF_OPEN failure")

            if self._failure_count >= self.config.failure_threshold:
                self._state = "OPEN"
                self._logger.error(f"Circuit breaker opened after {self._failure_count} failures")

            raise

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        if self._last_failure_time is None:
            return True

        time_since_failure = datetime.now() - self._last_failure_time
        return time_since_failure.total_seconds() >= self.config.recovery_timeout_seconds

    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        return {
            "state": self._state,
            "failure_count": self._failure_count,
            "last_failure_time": self._last_failure_time.isoformat() if self._last_failure_time else None,
            "half_open_calls": self._half_open_calls
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class ExponentialBackoffRetry:
    """Exponential backoff retry mechanism with jitter."""

    def __init__(self, config: RetryConfig):
        self.config = config
        self._logger = logging.getLogger(f"{__name__}.ExponentialBackoffRetry")

    async def retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with exponential backoff retry."""
        last_exception = None

        for attempt in range(self.config.max_attempts):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                if attempt == self.config.max_attempts - 1:
                    # Final attempt failed
                    break

                # Calculate delay with exponential backoff and jitter
                delay = min(
                    self.config.initial_delay_seconds * (self.config.exponential_base ** attempt),
                    self.config.max_delay_seconds
                )

                # Add jitter to prevent thundering herd
                jitter = delay * self.config.jitter_factor * random.random()
                total_delay = delay + jitter

                self._logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. Retrying in {total_delay:.2f}s"
                )

                await asyncio.sleep(total_delay)

        # All retries exhausted
        self._logger.error(f"All {self.config.max_attempts} retry attempts failed")
        raise last_exception


class GracefulDegradationManager:
    """Manage graceful degradation during system failures."""

    def __init__(self):
        self._degraded_operations = set()
        self._fallback_handlers = {}
        self._logger = logging.getLogger(f"{__name__}.GracefulDegradationManager")

    def degrade_operation(self, operation_name: str, fallback_handler: Optional[Callable] = None):
        """Degrade a specific operation."""
        self._degraded_operations.add(operation_name)
        if fallback_handler:
            self._fallback_handlers[operation_name] = fallback_handler

        self._logger.warning(f"Degraded operation: {operation_name}")

    def restore_operation(self, operation_name: str):
        """Restore a previously degraded operation."""
        self._degraded_operations.discard(operation_name)
        self._fallback_handlers.pop(operation_name, None)

        self._logger.info(f"Restored operation: {operation_name}")

    def is_degraded(self, operation_name: str) -> bool:
        """Check if operation is currently degraded."""
        return operation_name in self._degraded_operations

    async def execute_with_fallback(self, operation_name: str, primary_func: Callable,
                                   *args, **kwargs) -> Any:
        """Execute operation with fallback if degraded."""
        if not self.is_degraded(operation_name):
            # Operation not degraded, execute normally
            if asyncio.iscoroutinefunction(primary_func):
                return await primary_func(*args, **kwargs)
            else:
                return primary_func(*args, **kwargs)

        # Operation is degraded, use fallback
        fallback = self._fallback_handlers.get(operation_name)
        if fallback:
            self._logger.debug(f"Using fallback for degraded operation: {operation_name}")
            if asyncio.iscoroutinefunction(fallback):
                return await fallback(*args, **kwargs)
            else:
                return fallback(*args, **kwargs)
        else:
            raise OperationDegradedException(f"Operation {operation_name} is degraded and no fallback available")

    def get_degradation_status(self) -> Dict[str, Any]:
        """Get current degradation status."""
        return {
            "degraded_operations": list(self._degraded_operations),
            "fallback_handlers_available": list(self._fallback_handlers.keys()),
            "degradation_count": len(self._degraded_operations)
        }


class OperationDegradedException(Exception):
    """Raised when operation is degraded and no fallback available."""
    pass


class ErrorRecoveryManager:
    """Main error recovery coordination system."""

    def __init__(self, retry_config: Optional[RetryConfig] = None,
                 circuit_breaker_config: Optional[CircuitBreakerConfig] = None):
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()

        # Recovery components
        self.exponential_backoff = ExponentialBackoffRetry(self.retry_config)
        self.circuit_breaker = CircuitBreaker(self.circuit_breaker_config)
        self.degradation_manager = GracefulDegradationManager()

        # Error tracking
        self._error_history: List[ErrorRecord] = []
        self._recovery_strategies: Dict[ErrorType, RecoveryStrategy] = self._initialize_strategies()

        self._logger = logging.getLogger(f"{__name__}.ErrorRecoveryManager")

    def _initialize_strategies(self) -> Dict[ErrorType, RecoveryStrategy]:
        """Initialize default recovery strategies for error types."""
        return {
            ErrorType.REDIS_CONNECTION_ERROR: RecoveryStrategy.EXPONENTIAL_BACKOFF_RETRY,
            ErrorType.REDIS_TIMEOUT_ERROR: RecoveryStrategy.CIRCUIT_BREAKER,
            ErrorType.TASK_PROCESSING_ERROR: RecoveryStrategy.EXPONENTIAL_BACKOFF_RETRY,
            ErrorType.STATE_PERSISTENCE_ERROR: RecoveryStrategy.GRACEFUL_DEGRADATION,
            ErrorType.VALIDATION_ERROR: RecoveryStrategy.IMMEDIATE_FAILURE,
            ErrorType.RESOURCE_EXHAUSTION: RecoveryStrategy.GRACEFUL_DEGRADATION,
            ErrorType.UNKNOWN_ERROR: RecoveryStrategy.EXPONENTIAL_BACKOFF_RETRY,
        }

    async def execute_with_recovery(self, func: Callable, error_type: ErrorType,
                                   operation_name: str, *args, **kwargs) -> Any:
        """Execute function with appropriate recovery strategy."""
        strategy = self._recovery_strategies.get(error_type, RecoveryStrategy.EXPONENTIAL_BACKOFF_RETRY)

        try:
            if strategy == RecoveryStrategy.EXPONENTIAL_BACKOFF_RETRY:
                return await self.exponential_backoff.retry(func, *args, **kwargs)

            elif strategy == RecoveryStrategy.CIRCUIT_BREAKER:
                return await self.circuit_breaker.call(func, *args, **kwargs)

            elif strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
                return await self.degradation_manager.execute_with_fallback(
                    operation_name, func, *args, **kwargs
                )

            elif strategy == RecoveryStrategy.IMMEDIATE_FAILURE:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            else:
                # Fallback to direct execution
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

        except Exception as e:
            # Record error for analysis
            error_record = ErrorRecord(
                error_id=f"error_{int(time.time())}_{random.randint(1000, 9999)}",
                error_type=error_type,
                timestamp=datetime.now(),
                error_message=str(e),
                recovery_strategy=strategy
            )
            self._error_history.append(error_record)

            # Trigger additional recovery actions based on error type
            await self._handle_error_recovery(error_record, operation_name)

            raise

    async def _handle_error_recovery(self, error: ErrorRecord, operation_name: str):
        """Handle additional recovery actions for specific errors."""
        if error.error_type == ErrorType.REDIS_CONNECTION_ERROR:
            # Degrade Redis-dependent operations
            self.degradation_manager.degrade_operation("redis_operations")
            self._logger.error("Redis connection error - degrading Redis operations")

        elif error.error_type == ErrorType.RESOURCE_EXHAUSTION:
            # Degrade resource-intensive operations
            self.degradation_manager.degrade_operation("heavy_processing")
            self._logger.error("Resource exhaustion - degrading heavy processing")

        elif error.error_type == ErrorType.STATE_PERSISTENCE_ERROR:
            # Degrade state persistence temporarily
            self.degradation_manager.degrade_operation("state_persistence")
            self._logger.error("State persistence error - degrading persistence operations")

    def classify_error(self, exception: Exception) -> ErrorType:
        """Classify exception into appropriate error type."""
        error_message = str(exception).lower()
        exception_type = type(exception).__name__.lower()

        # Redis-related errors
        if any(term in error_message for term in ['redis', 'connection', 'timeout']):
            if 'timeout' in error_message:
                return ErrorType.REDIS_TIMEOUT_ERROR
            else:
                return ErrorType.REDIS_CONNECTION_ERROR

        # Resource errors
        if any(term in error_message for term in ['memory', 'disk', 'cpu', 'resource']):
            return ErrorType.RESOURCE_EXHAUSTION

        # Validation errors
        if any(term in error_message for term in ['validation', 'invalid', 'malformed']):
            return ErrorType.VALIDATION_ERROR

        # Task processing errors
        if any(term in error_message for term in ['task', 'processing', 'execution']):
            return ErrorType.TASK_PROCESSING_ERROR

        # State persistence errors
        if any(term in error_message for term in ['persist', 'checkpoint', 'storage']):
            return ErrorType.STATE_PERSISTENCE_ERROR

        return ErrorType.UNKNOWN_ERROR

    def get_recovery_status(self) -> Dict[str, Any]:
        """Get comprehensive recovery system status."""
        recent_errors = [
            error for error in self._error_history
            if (datetime.now() - error.timestamp).total_seconds() < 3600  # Last hour
        ]

        error_counts = {}
        for error in recent_errors:
            error_type = error.error_type.value
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        return {
            "circuit_breaker": self.circuit_breaker.get_state(),
            "degradation": self.degradation_manager.get_degradation_status(),
            "recent_error_counts": error_counts,
            "total_errors_tracked": len(self._error_history),
            "recovery_strategies": {
                error_type.value: strategy.value
                for error_type, strategy in self._recovery_strategies.items()
            }
        }

    def configure_strategy(self, error_type: ErrorType, strategy: RecoveryStrategy):
        """Configure recovery strategy for specific error type."""
        self._recovery_strategies[error_type] = strategy
        self._logger.info(f"Configured {strategy.value} for {error_type.value}")

    async def test_recovery_mechanisms(self) -> Dict[str, Any]:
        """Test all recovery mechanisms for health checking."""
        results = {}

        # Test exponential backoff
        try:
            test_func = lambda: True
            await self.exponential_backoff.retry(test_func)
            results["exponential_backoff"] = "healthy"
        except Exception as e:
            results["exponential_backoff"] = f"error: {e}"

        # Test circuit breaker
        try:
            test_func = lambda: True
            await self.circuit_breaker.call(test_func)
            results["circuit_breaker"] = "healthy"
        except Exception as e:
            results["circuit_breaker"] = f"error: {e}"

        # Test degradation manager
        try:
            status = self.degradation_manager.get_degradation_status()
            results["degradation_manager"] = "healthy"
            results["degradation_status"] = status
        except Exception as e:
            results["degradation_manager"] = f"error: {e}"

        return results


def with_error_recovery(error_type: ErrorType, operation_name: str,
                       recovery_manager: ErrorRecoveryManager):
    """Decorator for adding error recovery to functions."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await recovery_manager.execute_with_recovery(
                func, error_type, operation_name, *args, **kwargs
            )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we need to handle this differently
            # This is a simplified version - full implementation would
            # properly handle sync functions
            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator