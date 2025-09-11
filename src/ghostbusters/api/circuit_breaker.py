"""
Circuit Breaker for Ghostbusters API

Implements circuit breaker pattern for resilient service delivery
and graceful degradation under failure conditions.
"""

import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker implementation for service resilience.
    
    Monitors service failures and automatically opens circuit
    to prevent cascading failures and enable graceful degradation.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 3,
        timeout_seconds: float = 30.0
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout  # seconds
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        
        # Circuit state per service operation
        self._circuits: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Circuit breaker initialized")
    
    def can_execute(self, operation: str) -> bool:
        """
        Check if operation can be executed based on circuit state.
        
        Args:
            operation: Name of operation to check
            
        Returns:
            True if operation can execute, False if circuit is open
        """
        circuit = self._get_circuit(operation)
        
        if circuit["state"] == CircuitState.CLOSED:
            return True
        
        if circuit["state"] == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if datetime.utcnow() >= circuit["next_attempt"]:
                self._transition_to_half_open(operation)
                return True
            return False
        
        if circuit["state"] == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def record_success(self, operation: str) -> None:
        """
        Record successful operation execution.
        
        Args:
            operation: Name of operation that succeeded
        """
        circuit = self._get_circuit(operation)
        
        circuit["success_count"] += 1
        circuit["last_success"] = datetime.utcnow()
        
        if circuit["state"] == CircuitState.HALF_OPEN:
            if circuit["success_count"] >= self.success_threshold:
                self._transition_to_closed(operation)
        elif circuit["state"] == CircuitState.CLOSED:
            # Reset failure count on success
            circuit["failure_count"] = 0
        
        logger.debug(f"Recorded success for {operation}")
    
    def record_failure(self, operation: str) -> None:
        """
        Record failed operation execution.
        
        Args:
            operation: Name of operation that failed
        """
        circuit = self._get_circuit(operation)
        
        circuit["failure_count"] += 1
        circuit["last_failure"] = datetime.utcnow()
        
        if circuit["state"] == CircuitState.CLOSED:
            if circuit["failure_count"] >= self.failure_threshold:
                self._transition_to_open(operation)
        elif circuit["state"] == CircuitState.HALF_OPEN:
            # Failure during half-open means service still not recovered
            self._transition_to_open(operation)
        
        logger.warning(f"Recorded failure for {operation} (count: {circuit['failure_count']})")
    
    def record_timeout(self, operation: str) -> None:
        """
        Record operation timeout (treated as failure).
        
        Args:
            operation: Name of operation that timed out
        """
        circuit = self._get_circuit(operation)
        circuit["timeout_count"] += 1
        self.record_failure(operation)
        logger.warning(f"Recorded timeout for {operation}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get status of all circuits.
        
        Returns:
            Dictionary with circuit status information
        """
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "circuits": {}
        }
        
        for operation, circuit in self._circuits.items():
            status["circuits"][operation] = {
                "state": circuit["state"].value,
                "failure_count": circuit["failure_count"],
                "success_count": circuit["success_count"],
                "timeout_count": circuit["timeout_count"],
                "last_failure": circuit["last_failure"].isoformat() if circuit["last_failure"] else None,
                "last_success": circuit["last_success"].isoformat() if circuit["last_success"] else None,
                "next_attempt": circuit["next_attempt"].isoformat() if circuit["next_attempt"] else None
            }
        
        return status
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get circuit breaker metrics.
        
        Returns:
            Dictionary with metrics information
        """
        total_failures = sum(c["failure_count"] for c in self._circuits.values())
        total_successes = sum(c["success_count"] for c in self._circuits.values())
        total_timeouts = sum(c["timeout_count"] for c in self._circuits.values())
        
        open_circuits = sum(1 for c in self._circuits.values() if c["state"] == CircuitState.OPEN)
        half_open_circuits = sum(1 for c in self._circuits.values() if c["state"] == CircuitState.HALF_OPEN)
        
        return {
            "total_circuits": len(self._circuits),
            "open_circuits": open_circuits,
            "half_open_circuits": half_open_circuits,
            "total_failures": total_failures,
            "total_successes": total_successes,
            "total_timeouts": total_timeouts,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "success_threshold": self.success_threshold
        }
    
    def reset_circuit(self, operation: str) -> None:
        """
        Manually reset circuit to closed state.
        
        Args:
            operation: Name of operation circuit to reset
        """
        if operation in self._circuits:
            self._transition_to_closed(operation)
            logger.info(f"Manually reset circuit for {operation}")
    
    def reset_all_circuits(self) -> None:
        """Reset all circuits to closed state"""
        for operation in list(self._circuits.keys()):
            self.reset_circuit(operation)
        logger.info("Reset all circuits")
    
    def _get_circuit(self, operation: str) -> Dict[str, Any]:
        """Get or create circuit for operation"""
        if operation not in self._circuits:
            self._circuits[operation] = {
                "state": CircuitState.CLOSED,
                "failure_count": 0,
                "success_count": 0,
                "timeout_count": 0,
                "last_failure": None,
                "last_success": None,
                "next_attempt": None
            }
        
        return self._circuits[operation]
    
    def _transition_to_open(self, operation: str) -> None:
        """Transition circuit to open state"""
        circuit = self._get_circuit(operation)
        circuit["state"] = CircuitState.OPEN
        circuit["next_attempt"] = datetime.utcnow() + timedelta(seconds=self.recovery_timeout)
        
        logger.warning(f"Circuit opened for {operation} (failures: {circuit['failure_count']})")
    
    def _transition_to_half_open(self, operation: str) -> None:
        """Transition circuit to half-open state"""
        circuit = self._get_circuit(operation)
        circuit["state"] = CircuitState.HALF_OPEN
        circuit["success_count"] = 0  # Reset success count for testing
        
        logger.info(f"Circuit half-opened for {operation} (testing recovery)")
    
    def _transition_to_closed(self, operation: str) -> None:
        """Transition circuit to closed state"""
        circuit = self._get_circuit(operation)
        circuit["state"] = CircuitState.CLOSED
        circuit["failure_count"] = 0
        circuit["success_count"] = 0
        circuit["next_attempt"] = None
        
        logger.info(f"Circuit closed for {operation} (service recovered)")


class CircuitBreakerDecorator:
    """
    Decorator for applying circuit breaker to async functions.
    """
    
    def __init__(self, circuit_breaker: CircuitBreaker, operation_name: str):
        self.circuit_breaker = circuit_breaker
        self.operation_name = operation_name
    
    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            if not self.circuit_breaker.can_execute(self.operation_name):
                raise Exception(f"Circuit breaker open for {self.operation_name}")
            
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.circuit_breaker.timeout_seconds
                )
                self.circuit_breaker.record_success(self.operation_name)
                return result
                
            except asyncio.TimeoutError:
                self.circuit_breaker.record_timeout(self.operation_name)
                raise Exception(f"Operation {self.operation_name} timed out")
                
            except Exception as e:
                self.circuit_breaker.record_failure(self.operation_name)
                raise e
        
        return wrapper


def circuit_breaker(operation_name: str, breaker: CircuitBreaker = None):
    """
    Decorator factory for circuit breaker functionality.
    
    Args:
        operation_name: Name of operation for circuit tracking
        breaker: Optional circuit breaker instance (uses default if None)
    
    Returns:
        Decorator function
    """
    if breaker is None:
        breaker = CircuitBreaker()
    
    return CircuitBreakerDecorator(breaker, operation_name)