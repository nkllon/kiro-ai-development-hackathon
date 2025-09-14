"""
Graceful Degradation Manager Validation

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
