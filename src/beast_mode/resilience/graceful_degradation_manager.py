"""
Beast Mode Framework - Graceful Degradation Manager
Implements UC-12: Graceful degradation management for operational reliability
Provides circuit breakers, fallback mechanisms, and automatic recovery
"""

import time
import threading
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from contextlib import contextmanager

from ..core.reflective_module import ReflectiveModule, HealthStatus

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit breaker triggered
    HALF_OPEN = "half_open"  # Testing recovery

class DegradationLevel(Enum):
    NONE = "none"          # Full functionality
    MINIMAL = "minimal"    # Minor features disabled
    MODERATE = "moderate"  # Significant features disabled
    SEVERE = "severe"      # Core functionality only
    CRITICAL = "critical"  # Emergency mode

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    success_threshold: int = 3  # for half-open state
    timeout: float = 30.0  # operation timeout

@dataclass
class ServiceHealth:
    service_name: str
    is_healthy: bool
    last_check: datetime
    failure_count: int
    success_count: int
    circuit_state: CircuitState
    degradation_level: DegradationLevel
    error_messages: List[str] = field(default_factory=list)

@dataclass
class FallbackResult:
    success: bool
    data: Any
    fallback_used: str
    degradation_applied: DegradationLevel
    message: str

class GracefulDegradationManager(ReflectiveModule):
    """
    Manages graceful degradation across all Beast Mode services
    Implements circuit breakers, fallbacks, and automatic recovery
    """
    
    def __init__(self):
        super().__init__("graceful_degradation_manager")
        
        # Circuit breaker management
        self.circuit_breakers = {}
        self.service_health = {}
        self.fallback_handlers = {}
        
        # Configuration
        self.default_config = CircuitBreakerConfig()
        self.recovery_check_interval = 30  # seconds
        
        # Degradation state
        self.current_degradation = DegradationLevel.NONE
        self.degradation_history = []
        
        # Recovery management
        self.recovery_active = True
        self.recovery_thread = None
        
        # Metrics
        self.degradation_metrics = {
            'total_failures': 0,
            'total_recoveries': 0,
            'fallback_activations': 0,
            'circuit_breaker_trips': 0,
            'average_recovery_time': 0.0
        }
        
        # Initialize core service monitoring
        self._initialize_core_services()
        
        # Start recovery monitoring
        self._start_recovery_monitoring()
        
        self._update_health_indicator(
            "graceful_degradation_manager",
            HealthStatus.HEALTHY,
            "operational",
            "Graceful degradation manager ready for resilience management"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Get graceful degradation manager status"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "current_degradation_level": self.current_degradation.value,
            "active_circuit_breakers": len([cb for cb in self.circuit_breakers.values() if cb != CircuitState.CLOSED]),
            "monitored_services": len(self.service_health),
            "recovery_active": self.recovery_active,
            "total_failures": self.degradation_metrics['total_failures'],
            "total_recoveries": self.degradation_metrics['total_recoveries']
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for degradation manager"""
        # Manager is healthy if it can operate and degradation is not critical
        return (
            self.current_degradation != DegradationLevel.CRITICAL and
            self.recovery_active and
            not self._degradation_active
        )
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for degradation manager"""
        return {
            "degradation_status": {
                "current_level": self.current_degradation.value,
                "services_degraded": len([s for s in self.service_health.values() if not s.is_healthy]),
                "circuit_breakers_open": len([cb for cb in self.circuit_breakers.values() if cb == CircuitState.OPEN])
            },
            "service_health": {
                service_name: {
                    "healthy": health.is_healthy,
                    "circuit_state": health.circuit_state.value,
                    "degradation_level": health.degradation_level.value,
                    "failure_count": health.failure_count
                }
                for service_name, health in self.service_health.items()
            },
            "recovery_metrics": {
                "recovery_active": self.recovery_active,
                "total_recoveries": self.degradation_metrics['total_recoveries'],
                "average_recovery_time": self.degradation_metrics['average_recovery_time']
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: graceful degradation and resilience management"""
        return "graceful_degradation_and_resilience_management" 
   def register_service(self, service_name: str, 
                        health_check: Callable[[], bool],
                        fallback_handler: Optional[Callable] = None,
                        config: Optional[CircuitBreakerConfig] = None) -> Dict[str, Any]:
        """
        Register a service for graceful degradation monitoring
        """
        service_config = config or self.default_config
        
        # Initialize service health
        self.service_health[service_name] = ServiceHealth(
            service_name=service_name,
            is_healthy=True,
            last_check=datetime.now(),
            failure_count=0,
            success_count=0,
            circuit_state=CircuitState.CLOSED,
            degradation_level=DegradationLevel.NONE
        )
        
        # Initialize circuit breaker
        self.circuit_breakers[service_name] = CircuitState.CLOSED
        
        # Register fallback handler
        if fallback_handler:
            self.fallback_handlers[service_name] = fallback_handler
            
        self.logger.info(f"Service registered for degradation management: {service_name}")
        
        return {
            "success": True,
            "service_name": service_name,
            "circuit_state": CircuitState.CLOSED.value,
            "degradation_level": DegradationLevel.NONE.value
        }

    @contextmanager
    def circuit_breaker(self, service_name: str, operation_name: str = "default"):
        """
        Circuit breaker context manager for service operations
        Implements UC-12: Circuit breaker pattern for graceful degradation
        """
        if service_name not in self.service_health:
            raise ValueError(f"Service {service_name} not registered")
            
        service_health = self.service_health[service_name]
        circuit_state = self.circuit_breakers[service_name]
        
        # Check circuit breaker state
        if circuit_state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self._should_attempt_recovery(service_name):
                self.circuit_breakers[service_name] = CircuitState.HALF_OPEN
                self.logger.info(f"Circuit breaker for {service_name} moved to HALF_OPEN")
            else:
                # Circuit is open, use fallback
                fallback_result = self._execute_fallback(service_name, operation_name)
                yield fallback_result
                return
                
        # Execute operation with monitoring
        start_time = time.time()
        try:
            yield self._create_operation_context(service_name, operation_name)
            
            # Operation succeeded
            self._record_success(service_name)
            
            # If we were in half-open state, check if we can close the circuit
            if circuit_state == CircuitState.HALF_OPEN:
                if service_health.success_count >= self.default_config.success_threshold:
                    self._close_circuit(service_name)
                    
        except Exception as e:
            # Operation failed
            execution_time = time.time() - start_time
            self._record_failure(service_name, str(e), execution_time)
            
            # Check if we should open the circuit
            if service_health.failure_count >= self.default_config.failure_threshold:
                self._open_circuit(service_name)
                
            # Execute fallback
            fallback_result = self._execute_fallback(service_name, operation_name, str(e))
            yield fallback_result

    def execute_with_degradation(self, service_name: str, operation: Callable, 
                               *args, **kwargs) -> FallbackResult:
        """
        Execute operation with automatic degradation handling
        """
        try:
            with self.circuit_breaker(service_name, operation.__name__):
                result = operation(*args, **kwargs)
                return FallbackResult(
                    success=True,
                    data=result,
                    fallback_used="none",
                    degradation_applied=DegradationLevel.NONE,
                    message="Operation completed successfully"
                )
        except Exception as e:
            return self._execute_fallback(service_name, operation.__name__, str(e))

    def get_system_degradation_level(self) -> DegradationLevel:
        """Get current system-wide degradation level"""
        return self.current_degradation

    def force_degradation(self, level: DegradationLevel, reason: str) -> Dict[str, Any]:
        """
        Force system degradation to specified level
        Used for maintenance or emergency situations
        """
        previous_level = self.current_degradation
        self.current_degradation = level
        
        # Record degradation event
        degradation_event = {
            "timestamp": datetime.now(),
            "previous_level": previous_level.value,
            "new_level": level.value,
            "reason": reason,
            "forced": True
        }
        self.degradation_history.append(degradation_event)
        
        # Apply degradation to all services
        self._apply_system_degradation(level)
        
        self.logger.warning(f"System degradation forced to {level.value}: {reason}")
        
        return {
            "success": True,
            "previous_level": previous_level.value,
            "new_level": level.value,
            "reason": reason,
            "affected_services": list(self.service_health.keys())
        }

    def recover_from_degradation(self) -> Dict[str, Any]:
        """
        Attempt to recover from current degradation level
        """
        if self.current_degradation == DegradationLevel.NONE:
            return {"message": "System is not degraded", "success": True}
            
        recovery_start = time.time()
        
        # Check service health
        healthy_services = []
        failed_services = []
        
        for service_name in self.service_health.keys():
            if self._check_service_health(service_name):
                healthy_services.append(service_name)
                self._recover_service(service_name)
            else:
                failed_services.append(service_name)
                
        # Determine new degradation level
        new_level = self._calculate_degradation_level(healthy_services, failed_services)
        
        if new_level != self.current_degradation:
            previous_level = self.current_degradation
            self.current_degradation = new_level
            
            recovery_time = time.time() - recovery_start
            self._update_recovery_metrics(recovery_time)
            
            # Record recovery event
            recovery_event = {
                "timestamp": datetime.now(),
                "previous_level": previous_level.value,
                "new_level": new_level.value,
                "recovery_time": recovery_time,
                "healthy_services": healthy_services,
                "failed_services": failed_services
            }
            self.degradation_history.append(recovery_event)
            
            self.logger.info(f"System recovered from {previous_level.value} to {new_level.value}")
            
        return {
            "success": True,
            "previous_level": previous_level.value if 'previous_level' in locals() else self.current_degradation.value,
            "new_level": self.current_degradation.value,
            "recovery_time": recovery_time if 'recovery_time' in locals() else 0,
            "healthy_services": healthy_services,
            "failed_services": failed_services
        }

    def get_degradation_analytics(self) -> Dict[str, Any]:
        """
        Get comprehensive degradation analytics and insights
        """
        return {
            "current_status": {
                "degradation_level": self.current_degradation.value,
                "services_monitored": len(self.service_health),
                "services_healthy": len([s for s in self.service_health.values() if s.is_healthy]),
                "circuit_breakers_open": len([cb for cb in self.circuit_breakers.values() if cb == CircuitState.OPEN])
            },
            "degradation_metrics": self.degradation_metrics,
            "service_health_summary": {
                service_name: {
                    "healthy": health.is_healthy,
                    "circuit_state": health.circuit_state.value,
                    "failure_count": health.failure_count,
                    "success_count": health.success_count,
                    "last_check": health.last_check.isoformat()
                }
                for service_name, health in self.service_health.items()
            },
            "degradation_history": [
                {
                    "timestamp": event["timestamp"].isoformat(),
                    "previous_level": event.get("previous_level"),
                    "new_level": event.get("new_level"),
                    "reason": event.get("reason", "automatic"),
                    "recovery_time": event.get("recovery_time", 0)
                }
                for event in self.degradation_history[-10:]  # Last 10 events
            ],
            "recovery_recommendations": self._generate_recovery_recommendations()
        }    # H
elper methods for graceful degradation implementation
    
    def _initialize_core_services(self):
        """Initialize monitoring for core Beast Mode services"""
        core_services = [
            "reflective_module_system",
            "health_monitoring",
            "metrics_collection",
            "rca_engine",
            "tool_orchestrator",
            "gke_service_interface"
        ]
        
        for service in core_services:
            self.service_health[service] = ServiceHealth(
                service_name=service,
                is_healthy=True,
                last_check=datetime.now(),
                failure_count=0,
                success_count=0,
                circuit_state=CircuitState.CLOSED,
                degradation_level=DegradationLevel.NONE
            )
            self.circuit_breakers[service] = CircuitState.CLOSED
            
    def _start_recovery_monitoring(self):
        """Start background thread for recovery monitoring"""
        def recovery_loop():
            while self.recovery_active:
                try:
                    self._check_all_services()
                    self._attempt_automatic_recovery()
                    time.sleep(self.recovery_check_interval)
                except Exception as e:
                    self.logger.error(f"Recovery monitoring error: {str(e)}")
                    time.sleep(60)  # Wait before retrying
                    
        self.recovery_thread = threading.Thread(target=recovery_loop, daemon=True)
        self.recovery_thread.start()
        
    def _should_attempt_recovery(self, service_name: str) -> bool:
        """Check if circuit breaker should attempt recovery"""
        service_health = self.service_health[service_name]
        time_since_failure = datetime.now() - service_health.last_check
        return time_since_failure.total_seconds() >= self.default_config.recovery_timeout
        
    def _create_operation_context(self, service_name: str, operation_name: str) -> Dict[str, Any]:
        """Create context for operation execution"""
        return {
            "service_name": service_name,
            "operation_name": operation_name,
            "start_time": time.time(),
            "circuit_state": self.circuit_breakers[service_name].value
        }
        
    def _record_success(self, service_name: str):
        """Record successful operation"""
        service_health = self.service_health[service_name]
        service_health.success_count += 1
        service_health.failure_count = max(0, service_health.failure_count - 1)  # Gradual recovery
        service_health.is_healthy = True
        service_health.last_check = datetime.now()
        
        # Clear old error messages on success
        if service_health.success_count >= 3:
            service_health.error_messages = []
            
    def _record_failure(self, service_name: str, error_message: str, execution_time: float):
        """Record failed operation"""
        service_health = self.service_health[service_name]
        service_health.failure_count += 1
        service_health.success_count = 0
        service_health.is_healthy = False
        service_health.last_check = datetime.now()
        
        # Track error messages (keep last 5)
        service_health.error_messages.append(f"{datetime.now().isoformat()}: {error_message}")
        service_health.error_messages = service_health.error_messages[-5:]
        
        # Update metrics
        self.degradation_metrics['total_failures'] += 1
        
    def _open_circuit(self, service_name: str):
        """Open circuit breaker for service"""
        self.circuit_breakers[service_name] = CircuitState.OPEN
        service_health = self.service_health[service_name]
        service_health.circuit_state = CircuitState.OPEN
        
        # Determine degradation level for this service
        service_health.degradation_level = self._determine_service_degradation(service_name)
        
        # Update system degradation level
        self._update_system_degradation()
        
        # Update metrics
        self.degradation_metrics['circuit_breaker_trips'] += 1
        
        self.logger.warning(f"Circuit breaker OPENED for service: {service_name}")
        
    def _close_circuit(self, service_name: str):
        """Close circuit breaker for service"""
        self.circuit_breakers[service_name] = CircuitState.CLOSED
        service_health = self.service_health[service_name]
        service_health.circuit_state = CircuitState.CLOSED
        service_health.degradation_level = DegradationLevel.NONE
        
        # Update system degradation level
        self._update_system_degradation()
        
        # Update metrics
        self.degradation_metrics['total_recoveries'] += 1
        
        self.logger.info(f"Circuit breaker CLOSED for service: {service_name}")
        
    def _execute_fallback(self, service_name: str, operation_name: str, error: str = "") -> FallbackResult:
        """Execute fallback mechanism for failed service"""
        self.degradation_metrics['fallback_activations'] += 1
        
        # Check if custom fallback handler exists
        if service_name in self.fallback_handlers:
            try:
                fallback_data = self.fallback_handlers[service_name](operation_name, error)
                return FallbackResult(
                    success=True,
                    data=fallback_data,
                    fallback_used=f"custom_handler_{service_name}",
                    degradation_applied=self.service_health[service_name].degradation_level,
                    message=f"Custom fallback executed for {service_name}"
                )
            except Exception as e:
                self.logger.error(f"Custom fallback failed for {service_name}: {str(e)}")
                
        # Use default fallback strategies
        return self._default_fallback(service_name, operation_name, error)
        
    def _default_fallback(self, service_name: str, operation_name: str, error: str) -> FallbackResult:
        """Default fallback strategies"""
        service_health = self.service_health[service_name]
        
        # Determine fallback strategy based on service type
        if "health" in service_name.lower():
            # Health services: return cached status
            return FallbackResult(
                success=True,
                data={"status": "unknown", "message": "Health service unavailable"},
                fallback_used="cached_health_status",
                degradation_applied=DegradationLevel.MINIMAL,
                message="Using cached health status"
            )
        elif "metrics" in service_name.lower():
            # Metrics services: return empty metrics
            return FallbackResult(
                success=True,
                data={"metrics": {}, "timestamp": datetime.now().isoformat()},
                fallback_used="empty_metrics",
                degradation_applied=DegradationLevel.MINIMAL,
                message="Metrics collection temporarily unavailable"
            )
        elif "orchestrator" in service_name.lower():
            # Orchestration services: return manual mode
            return FallbackResult(
                success=False,
                data={"mode": "manual", "message": "Automatic orchestration unavailable"},
                fallback_used="manual_mode",
                degradation_applied=DegradationLevel.MODERATE,
                message="Switched to manual operation mode"
            )
        else:
            # Generic fallback: return error with guidance
            return FallbackResult(
                success=False,
                data={"error": error, "service": service_name},
                fallback_used="error_response",
                degradation_applied=DegradationLevel.SEVERE,
                message=f"Service {service_name} unavailable, manual intervention required"
            )
            
    def _determine_service_degradation(self, service_name: str) -> DegradationLevel:
        """Determine degradation level for specific service"""
        service_health = self.service_health[service_name]
        
        # Critical services cause higher degradation
        critical_services = ["reflective_module_system", "health_monitoring"]
        if service_name in critical_services:
            if service_health.failure_count >= 10:
                return DegradationLevel.CRITICAL
            elif service_health.failure_count >= 5:
                return DegradationLevel.SEVERE
            else:
                return DegradationLevel.MODERATE
        else:
            # Non-critical services
            if service_health.failure_count >= 15:
                return DegradationLevel.MODERATE
            elif service_health.failure_count >= 8:
                return DegradationLevel.MINIMAL
            else:
                return DegradationLevel.NONE
                
    def _update_system_degradation(self):
        """Update system-wide degradation level based on service states"""
        service_degradations = [health.degradation_level for health in self.service_health.values()]
        
        # System degradation is the highest individual service degradation
        if DegradationLevel.CRITICAL in service_degradations:
            new_level = DegradationLevel.CRITICAL
        elif DegradationLevel.SEVERE in service_degradations:
            new_level = DegradationLevel.SEVERE
        elif DegradationLevel.MODERATE in service_degradations:
            new_level = DegradationLevel.MODERATE
        elif DegradationLevel.MINIMAL in service_degradations:
            new_level = DegradationLevel.MINIMAL
        else:
            new_level = DegradationLevel.NONE
            
        if new_level != self.current_degradation:
            previous_level = self.current_degradation
            self.current_degradation = new_level
            
            # Record automatic degradation change
            degradation_event = {
                "timestamp": datetime.now(),
                "previous_level": previous_level.value,
                "new_level": new_level.value,
                "reason": "automatic_service_health_change",
                "forced": False
            }
            self.degradation_history.append(degradation_event)
            
            self.logger.info(f"System degradation changed from {previous_level.value} to {new_level.value}")
            
    def _apply_system_degradation(self, level: DegradationLevel):
        """Apply degradation settings to all services"""
        for service_name, service_health in self.service_health.items():
            if level == DegradationLevel.CRITICAL:
                # Only core health monitoring remains
                if service_name not in ["reflective_module_system", "health_monitoring"]:
                    service_health.degradation_level = DegradationLevel.CRITICAL
            elif level == DegradationLevel.SEVERE:
                # Only essential services remain
                essential_services = ["reflective_module_system", "health_monitoring", "metrics_collection"]
                if service_name not in essential_services:
                    service_health.degradation_level = DegradationLevel.SEVERE
            elif level == DegradationLevel.MODERATE:
                # Reduce non-critical functionality
                service_health.degradation_level = min(service_health.degradation_level, DegradationLevel.MODERATE)
                
    def _check_all_services(self):
        """Check health of all registered services"""
        for service_name in self.service_health.keys():
            self._check_service_health(service_name)
            
    def _check_service_health(self, service_name: str) -> bool:
        """Check health of specific service"""
        try:
            # Simulate health check (in real implementation, would call actual health endpoints)
            service_health = self.service_health[service_name]
            
            # Simple health simulation based on current state
            if service_health.circuit_state == CircuitState.OPEN:
                # Service is down, check if it might be recovering
                recovery_probability = max(0.1, 1.0 - (service_health.failure_count / 20))
                is_healthy = time.time() % 10 < recovery_probability * 10  # Simulate gradual recovery
            else:
                # Service is up, small chance of failure
                failure_probability = min(0.1, service_health.failure_count / 100)
                is_healthy = time.time() % 10 >= failure_probability * 10
                
            service_health.is_healthy = is_healthy
            service_health.last_check = datetime.now()
            
            return is_healthy
            
        except Exception as e:
            self.logger.error(f"Health check failed for {service_name}: {str(e)}")
            return False
            
    def _attempt_automatic_recovery(self):
        """Attempt automatic recovery for failed services"""
        for service_name, circuit_state in self.circuit_breakers.items():
            if circuit_state == CircuitState.OPEN:
                if self._should_attempt_recovery(service_name):
                    self.logger.info(f"Attempting automatic recovery for {service_name}")
                    if self._check_service_health(service_name):
                        self._recover_service(service_name)
                        
    def _recover_service(self, service_name: str):
        """Recover service from failure state"""
        service_health = self.service_health[service_name]
        
        # Reset failure count and move to half-open state
        service_health.failure_count = 0
        service_health.success_count = 0
        service_health.circuit_state = CircuitState.HALF_OPEN
        self.circuit_breakers[service_name] = CircuitState.HALF_OPEN
        
        self.logger.info(f"Service {service_name} moved to recovery state (HALF_OPEN)")
        
    def _calculate_degradation_level(self, healthy_services: List[str], failed_services: List[str]) -> DegradationLevel:
        """Calculate system degradation level based on service health"""
        total_services = len(healthy_services) + len(failed_services)
        if total_services == 0:
            return DegradationLevel.NONE
            
        health_ratio = len(healthy_services) / total_services
        
        # Check for critical service failures
        critical_services = ["reflective_module_system", "health_monitoring"]
        critical_failed = any(service in failed_services for service in critical_services)
        
        if critical_failed or health_ratio < 0.3:
            return DegradationLevel.CRITICAL
        elif health_ratio < 0.5:
            return DegradationLevel.SEVERE
        elif health_ratio < 0.7:
            return DegradationLevel.MODERATE
        elif health_ratio < 0.9:
            return DegradationLevel.MINIMAL
        else:
            return DegradationLevel.NONE
            
    def _update_recovery_metrics(self, recovery_time: float):
        """Update recovery performance metrics"""
        current_avg = self.degradation_metrics['average_recovery_time']
        total_recoveries = self.degradation_metrics['total_recoveries']
        
        if total_recoveries == 0:
            self.degradation_metrics['average_recovery_time'] = recovery_time
        else:
            self.degradation_metrics['average_recovery_time'] = (
                (current_avg * total_recoveries + recovery_time) / (total_recoveries + 1)
            )
            
    def _generate_recovery_recommendations(self) -> List[str]:
        """Generate recommendations for system recovery"""
        recommendations = []
        
        # Check for persistent failures
        persistent_failures = [
            service_name for service_name, health in self.service_health.items()
            if health.failure_count > 10
        ]
        
        if persistent_failures:
            recommendations.append(f"Investigate persistent failures in: {', '.join(persistent_failures)}")
            
        # Check for frequent circuit breaker trips
        frequent_trips = [
            service_name for service_name, health in self.service_health.items()
            if health.failure_count > 5 and health.circuit_state == CircuitState.OPEN
        ]
        
        if frequent_trips:
            recommendations.append(f"Review circuit breaker thresholds for: {', '.join(frequent_trips)}")
            
        # Check degradation level
        if self.current_degradation == DegradationLevel.CRITICAL:
            recommendations.append("System in critical state - immediate manual intervention required")
        elif self.current_degradation == DegradationLevel.SEVERE:
            recommendations.append("System severely degraded - prioritize core service recovery")
            
        if not recommendations:
            recommendations.append("System operating within normal parameters")
            
        return recommendations