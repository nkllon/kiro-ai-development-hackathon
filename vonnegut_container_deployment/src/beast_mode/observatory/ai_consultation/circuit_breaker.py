"""
Circuit Breaker Pattern Implementation for AI Consultation System

Provides circuit breaker protection for external services and expensive operations
to prevent cascading failures and protect the Observatory system.
"""

import asyncio
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional, Union
from dataclasses import dataclass, field
import logging

from .exceptions import CircuitBreakerOpenError
from .interfaces import ICircuitBreaker

logger = logging.getLogger(__name__)


class CircuitBreakerState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting calls
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    consecutive_failures: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changed_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate percentage"""
        if self.total_calls == 0:
            return 0.0
        return (self.failed_calls / self.total_calls) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        return 100.0 - self.failure_rate


class CircuitBreaker(ICircuitBreaker):
    """
    Circuit breaker implementation with configurable thresholds and timeouts.
    
    Protects against cascading failures by:
    1. Monitoring failure rates and consecutive failures
    2. Opening circuit when thresholds are exceeded
    3. Allowing limited testing when circuit is half-open
    4. Automatically recovering when service is healthy
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        failure_rate_threshold: float = 50.0,
        recovery_timeout: int = 60,
        expected_exception: Union[Exception, tuple] = Exception,
        fallback_function: Optional[Callable] = None
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.failure_rate_threshold = failure_rate_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.fallback_function = fallback_function
        
        self._state = CircuitBreakerState.CLOSED
        self._stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
        
        logger.info(f"Circuit breaker '{name}' initialized with thresholds: "
                   f"failures={failure_threshold}, rate={failure_rate_threshold}%")
    
    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state"""
        return self._state
    
    @property
    def stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics"""
        return self._stats
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpenError: When circuit is open
        """
        async with self._lock:
            await self._update_state()
            
            if self._state == CircuitBreakerState.OPEN:
                logger.warning(f"Circuit breaker '{self.name}' is OPEN, rejecting call")
                if self.fallback_function:
                    logger.info(f"Executing fallback function for '{self.name}'")
                    return await self._execute_fallback(*args, **kwargs)
                else:
                    raise CircuitBreakerOpenError(
                        message=f"Circuit breaker '{self.name}' is open",
                        service=self.name,
                        retry_after=self.recovery_timeout
                    )
        
        # Execute the function
        start_time = time.time()
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            await self._record_success(execution_time)
            return result
            
        except self.expected_exception as e:
            execution_time = time.time() - start_time
            await self._record_failure(e, execution_time)
            raise
    
    async def _update_state(self) -> None:
        """Update circuit breaker state based on current conditions"""
        now = datetime.utcnow()
        
        if self._state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if (self._stats.state_changed_at and 
                now - self._stats.state_changed_at >= timedelta(seconds=self.recovery_timeout)):
                await self._transition_to_half_open()
        
        elif self._state == CircuitBreakerState.CLOSED:
            # Check if we should open the circuit
            if self._should_open_circuit():
                await self._transition_to_open()
        
        elif self._state == CircuitBreakerState.HALF_OPEN:
            # In half-open state, we allow one call through
            # The result will determine if we close or open
            pass
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened"""
        # Check consecutive failures threshold
        if self._stats.consecutive_failures > self.failure_threshold:
            logger.warning(f"Circuit breaker '{self.name}': consecutive failures "
                          f"({self._stats.consecutive_failures}) exceeded threshold "
                          f"({self.failure_threshold})")
            return True
        
        # Check failure rate threshold (only if we have enough data)
        if (self._stats.total_calls >= self.failure_threshold and 
            self._stats.failure_rate >= self.failure_rate_threshold):
            logger.warning(f"Circuit breaker '{self.name}': failure rate "
                          f"({self._stats.failure_rate:.1f}%) exceeded threshold "
                          f"({self.failure_rate_threshold}%)")
            return True
        
        return False
    
    async def _transition_to_open(self) -> None:
        """Transition circuit breaker to OPEN state"""
        self._state = CircuitBreakerState.OPEN
        self._stats.state_changed_at = datetime.utcnow()
        logger.error(f"Circuit breaker '{self.name}' transitioned to OPEN state")
    
    async def _transition_to_half_open(self) -> None:
        """Transition circuit breaker to HALF_OPEN state"""
        self._state = CircuitBreakerState.HALF_OPEN
        self._stats.state_changed_at = datetime.utcnow()
        logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN state")
    
    async def _transition_to_closed(self) -> None:
        """Transition circuit breaker to CLOSED state"""
        self._state = CircuitBreakerState.CLOSED
        self._stats.state_changed_at = datetime.utcnow()
        self._stats.consecutive_failures = 0  # Reset consecutive failures
        logger.info(f"Circuit breaker '{self.name}' transitioned to CLOSED state")
    
    async def _record_success(self, execution_time: float) -> None:
        """Record successful function execution"""
        async with self._lock:
            self._stats.total_calls += 1
            self._stats.successful_calls += 1
            self._stats.consecutive_failures = 0
            self._stats.last_success_time = datetime.utcnow()
            
            # If we're in half-open state and got a success, close the circuit
            if self._state == CircuitBreakerState.HALF_OPEN:
                await self._transition_to_closed()
            
            logger.debug(f"Circuit breaker '{self.name}': success recorded "
                        f"(execution_time={execution_time:.3f}s)")
    
    async def _record_failure(self, exception: Exception, execution_time: float) -> None:
        """Record failed function execution"""
        async with self._lock:
            self._stats.total_calls += 1
            self._stats.failed_calls += 1
            self._stats.consecutive_failures += 1
            self._stats.last_failure_time = datetime.utcnow()
            
            # If we're in half-open state and got a failure, open the circuit
            if self._state == CircuitBreakerState.HALF_OPEN:
                await self._transition_to_open()
            # If we're in closed state, check if we should open
            elif self._state == CircuitBreakerState.CLOSED and self._should_open_circuit():
                await self._transition_to_open()
            
            logger.warning(f"Circuit breaker '{self.name}': failure recorded "
                          f"(execution_time={execution_time:.3f}s, "
                          f"exception={type(exception).__name__}: {exception})")
    
    async def _execute_fallback(self, *args, **kwargs) -> Any:
        """Execute fallback function if available"""
        try:
            if asyncio.iscoroutinefunction(self.fallback_function):
                return await self.fallback_function(*args, **kwargs)
            else:
                return self.fallback_function(*args, **kwargs)
        except Exception as e:
            logger.error(f"Fallback function for '{self.name}' failed: {e}")
            raise
    
    async def is_open(self) -> bool:
        """Check if circuit breaker is open"""
        return self._state == CircuitBreakerState.OPEN
    
    async def reset(self) -> None:
        """Reset circuit breaker to closed state"""
        async with self._lock:
            await self._transition_to_closed()
            # Reset stats but keep historical data
            self._stats.consecutive_failures = 0
            logger.info(f"Circuit breaker '{self.name}' manually reset to CLOSED state")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            'name': self.name,
            'state': self._state.value,
            'total_calls': self._stats.total_calls,
            'successful_calls': self._stats.successful_calls,
            'failed_calls': self._stats.failed_calls,
            'consecutive_failures': self._stats.consecutive_failures,
            'failure_rate': self._stats.failure_rate,
            'success_rate': self._stats.success_rate,
            'last_failure_time': self._stats.last_failure_time.isoformat() if self._stats.last_failure_time else None,
            'last_success_time': self._stats.last_success_time.isoformat() if self._stats.last_success_time else None,
            'state_changed_at': self._stats.state_changed_at.isoformat(),
            'failure_threshold': self.failure_threshold,
            'failure_rate_threshold': self.failure_rate_threshold,
            'recovery_timeout': self.recovery_timeout
        }


class CircuitBreakerManager:
    """
    Manages multiple circuit breakers for different services
    """
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()
    
    async def get_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        failure_rate_threshold: float = 50.0,
        recovery_timeout: int = 60,
        expected_exception: Union[Exception, tuple] = Exception,
        fallback_function: Optional[Callable] = None
    ) -> CircuitBreaker:
        """Get or create a circuit breaker"""
        async with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(
                    name=name,
                    failure_threshold=failure_threshold,
                    failure_rate_threshold=failure_rate_threshold,
                    recovery_timeout=recovery_timeout,
                    expected_exception=expected_exception,
                    fallback_function=fallback_function
                )
                logger.info(f"Created new circuit breaker: {name}")
            
            return self._breakers[name]
    
    async def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers"""
        stats = {}
        for name, breaker in self._breakers.items():
            stats[name] = await breaker.get_stats()
        return stats
    
    async def reset_all(self) -> None:
        """Reset all circuit breakers"""
        for breaker in self._breakers.values():
            await breaker.reset()
        logger.info("All circuit breakers reset")
    
    async def get_open_breakers(self) -> list[str]:
        """Get list of open circuit breaker names"""
        open_breakers = []
        for name, breaker in self._breakers.items():
            if await breaker.is_open():
                open_breakers.append(name)
        return open_breakers


# Global circuit breaker manager instance
circuit_breaker_manager = CircuitBreakerManager()


async def with_circuit_breaker(
    name: str,
    func: Callable,
    *args,
    failure_threshold: int = 5,
    failure_rate_threshold: float = 50.0,
    recovery_timeout: int = 60,
    expected_exception: Union[Exception, tuple] = Exception,
    fallback_function: Optional[Callable] = None,
    **kwargs
) -> Any:
    """
    Convenience function to execute a function with circuit breaker protection
    
    Args:
        name: Circuit breaker name
        func: Function to execute
        *args: Function arguments
        failure_threshold: Number of consecutive failures before opening
        failure_rate_threshold: Failure rate percentage before opening
        recovery_timeout: Seconds to wait before trying again
        expected_exception: Exception types that trigger circuit breaker
        fallback_function: Function to call when circuit is open
        **kwargs: Function keyword arguments
    
    Returns:
        Function result
    """
    breaker = await circuit_breaker_manager.get_breaker(
        name=name,
        failure_threshold=failure_threshold,
        failure_rate_threshold=failure_rate_threshold,
        recovery_timeout=recovery_timeout,
        expected_exception=expected_exception,
        fallback_function=fallback_function
    )
    
    return await breaker.call(func, *args, **kwargs)