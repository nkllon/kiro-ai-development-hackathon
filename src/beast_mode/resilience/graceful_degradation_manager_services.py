"""
Graceful Degradation Manager Services

This module was extracted from graceful_degradation_manager.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import threading
import time
from ..core.reflective_module import ReflectiveModule

class ServiceState(Enum):
    """Service operational states."""
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    FAILING = 'failing'
    CIRCUIT_OPEN = 'circuit_open'

class GracefulDegradationManager(ReflectiveModule):
    """
    Manages graceful degradation of services under stress.
    
    Implements circuit breaker patterns, fallback mechanisms, and systematic
    resilience to maintain system stability when components fail.
    """

    def __init__(self):
        """Initialize graceful degradation manager."""
        super().__init__()
        self.services: Dict[str, Dict[str, Any]] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.degradation_history: List[DegradationEvent] = []
        self.default_config = CircuitBreakerConfig()
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()

    def _get_module_name(self) -> str:
        """Module identification for RM compliance."""
        return 'graceful_degradation_manager'

    def _get_primary_responsibility(self) -> str:
        """Single responsibility: graceful degradation and resilience management."""
        return 'graceful_degradation_and_resilience_management'

    def register_service(self, service_name: str, health_check: Callable[[], bool], fallback_handler: Optional[Callable]=None, config: Optional[CircuitBreakerConfig]=None) -> Dict[str, Any]:
        """
        Register a service for graceful degradation monitoring.
        
        Args:
            service_name: Unique service identifier
            health_check: Function to check service health
            fallback_handler: Optional fallback function
            config: Circuit breaker configuration
            
        Returns:
            Service registration details
        """
        service_config = config or self.default_config
        with self._lock:
            self.services[service_name] = {'health_check': health_check, 'fallback_handler': fallback_handler, 'config': service_config, 'state': ServiceState.HEALTHY, 'failure_count': 0, 'last_failure': None, 'last_success': datetime.now(), 'circuit_open_time': None}
            self.circuit_breakers[service_name] = {'state': 'closed', 'failure_count': 0, 'last_failure_time': None, 'half_open_calls': 0, 'success_count': 0}
        self.logger.info(f'Registered service for graceful degradation: {service_name}')
        return {'service_name': service_name, 'status': 'registered', 'config': service_config, 'timestamp': datetime.now()}

    def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Check service health and manage circuit breaker state.
        
        Args:
            service_name: Service to check
            
        Returns:
            Health status and recommendations
        """
        if service_name not in self.services:
            return {'status': 'unknown', 'error': 'Service not registered'}
        service = self.services[service_name]
        circuit = self.circuit_breakers[service_name]
        if circuit['state'] == 'open':
            if self._should_attempt_recovery(service_name):
                circuit['state'] = 'half_open'
                circuit['half_open_calls'] = 0
                circuit['success_count'] = 0
            else:
                return {'status': 'circuit_open', 'service_state': ServiceState.CIRCUIT_OPEN, 'message': 'Circuit breaker is open, using fallback'}
        try:
            is_healthy = service['health_check']()
            if is_healthy:
                self._handle_success(service_name)
                return {'status': 'healthy', 'service_state': ServiceState.HEALTHY, 'last_success': service['last_success']}
            else:
                self._handle_failure(service_name, 'Health check failed')
                return {'status': 'unhealthy', 'service_state': service['state'], 'failure_count': service['failure_count']}
        except Exception as e:
            self._handle_failure(service_name, f'Health check exception: {str(e)}')
            return {'status': 'error', 'service_state': service['state'], 'error': str(e)}

    def execute_with_fallback(self, service_name: str, primary_function: Callable, *args, **kwargs) -> Any:
        """
        Execute function with automatic fallback on failure.
        
        Args:
            service_name: Service identifier
            primary_function: Primary function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Function result or fallback result
        """
        if service_name not in self.services:
            raise ValueError(f'Service {service_name} not registered')
        service = self.services[service_name]
        circuit = self.circuit_breakers[service_name]
        if circuit['state'] == 'open':
            return self._execute_fallback(service_name, *args, **kwargs)
        try:
            result = primary_function(*args, **kwargs)
            self._handle_success(service_name)
            return result
        except Exception as e:
            self._handle_failure(service_name, f'Execution failed: {str(e)}')
            return self._execute_fallback(service_name, *args, **kwargs)

    def get_system_resilience_status(self) -> Dict[str, Any]:
        """
        Get overall system resilience status.
        
        Returns:
            Comprehensive resilience report
        """
        healthy_services = sum((1 for service in self.services.values() if service['state'] == ServiceState.HEALTHY))
        total_services = len(self.services)
        resilience_score = healthy_services / total_services * 100 if total_services > 0 else 100
        return {'resilience_score': resilience_score, 'healthy_services': healthy_services, 'total_services': total_services, 'degraded_services': [name for name, service in self.services.items() if service['state'] != ServiceState.HEALTHY], 'recent_events': [{'timestamp': event.timestamp.isoformat(), 'service': event.service_name, 'type': event.event_type, 'severity': event.severity} for event in self.degradation_history[-10:]], 'recovery_recommendations': self._generate_recovery_recommendations()}

    def _handle_success(self, service_name: str):
        """Handle successful service operation."""
        with self._lock:
            service = self.services[service_name]
            circuit = self.circuit_breakers[service_name]
            service['last_success'] = datetime.now()
            service['failure_count'] = 0
            service['state'] = ServiceState.HEALTHY
            if circuit['state'] == 'half_open':
                circuit['success_count'] += 1
                if circuit['success_count'] >= service['config'].success_threshold:
                    circuit['state'] = 'closed'
                    circuit['failure_count'] = 0
                    self.logger.info(f'Circuit breaker closed for {service_name}')

    def _handle_failure(self, service_name: str, error_message: str):
        """Handle service failure."""
        with self._lock:
            service = self.services[service_name]
            circuit = self.circuit_breakers[service_name]
            service['failure_count'] += 1
            service['last_failure'] = datetime.now()
            if service['failure_count'] >= service['config'].failure_threshold:
                service['state'] = ServiceState.FAILING
                circuit['state'] = 'open'
                circuit['failure_count'] = service['failure_count']
                circuit['last_failure_time'] = datetime.now()
                service['circuit_open_time'] = datetime.now()
                self.logger.warning(f'Circuit breaker opened for {service_name}')
            else:
                service['state'] = ServiceState.DEGRADED
            event = DegradationEvent(timestamp=datetime.now(), service_name=service_name, event_type='failure', severity='warning' if service['state'] == ServiceState.DEGRADED else 'error', details={'error_message': error_message, 'failure_count': service['failure_count']})
            self.degradation_history.append(event)

    def _should_attempt_recovery(self, service_name: str) -> bool:
        """Check if circuit breaker should attempt recovery."""
        service = self.services[service_name]
        if service['circuit_open_time'] is None:
            return False
        recovery_timeout = timedelta(seconds=service['config'].recovery_timeout)
        return datetime.now() - service['circuit_open_time'] > recovery_timeout

    def _execute_fallback(self, service_name: str, *args, **kwargs) -> Any:
        """Execute fallback handler for service."""
        service = self.services[service_name]
        if service['fallback_handler']:
            try:
                return service['fallback_handler'](*args, **kwargs)
            except Exception as e:
                self.logger.error(f'Fallback failed for {service_name}: {str(e)}')
                return None
        else:
            self.logger.warning(f'No fallback handler for {service_name}')
            return None

    def _generate_recovery_recommendations(self) -> List[str]:
        """Generate recovery recommendations based on current state."""
        recommendations = []
        for service_name, service in self.services.items():
            if service['state'] != ServiceState.HEALTHY:
                recommendations.append(f"Service {service_name} requires attention: {service['state'].value}")
        if len(recommendations) == 0:
            recommendations.append('All services are healthy')
        return recommendations

    def get_health_status(self) -> Dict[str, Any]:
        """Get module health status for RM compliance."""
        return {'module_name': self._get_module_name(), 'status': 'healthy' if len(self.services) > 0 else 'idle', 'registered_services': len(self.services), 'healthy_services': sum((1 for service in self.services.values() if service['state'] == ServiceState.HEALTHY)), 'last_check': datetime.now().isoformat()}
