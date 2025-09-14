"""
Comprehensive Monitoring System Core Core Validation

This module was extracted from comprehensive_monitoring_system_core_core.py
as part of RM-DDD compliance refactoring.
"""

import time
import json
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import statistics
from ..core.reflective_module import ReflectiveModule, HealthStatus
import random
import random
import random
import random
import random
import random
import random
import random
import random
import random
import random
import random

def _check_alert_rules(self, metric: Metric):
    """Check metric against alert rules and trigger alerts if needed"""
    for rule_name, rule in self.alert_rules.items():
        if rule['metric_name'] == metric.name:
            threshold = rule['threshold']
            comparison = rule['comparison']
            alert_triggered = False
            if comparison == 'greater_than' and metric.value > threshold:
                alert_triggered = True
            elif comparison == 'less_than' and metric.value < threshold:
                alert_triggered = True
            elif comparison == 'equals' and metric.value == threshold:
                alert_triggered = True
            if alert_triggered:
                self._trigger_alert(rule_name, rule, metric)
            elif rule_name in self.active_alerts:
                self._clear_alert(rule_name)

def _run_health_checks(self):
    """Run health checks for all registered endpoints"""
    for endpoint_name, endpoint in self.health_endpoints.items():
        try:
            now = datetime.now()
            if endpoint.last_check_time is None or (now - endpoint.last_check_time).total_seconds() >= endpoint.check_interval_seconds:
                health_result = endpoint.health_check_function()
                endpoint.last_check_time = now
                endpoint.last_result = health_result
                self.health_check_results[endpoint_name] = health_result
                health_score = 1.0 if health_result.get('healthy', False) else 0.0
                self.emit_metric(f'health_check_{endpoint_name}', health_score, MetricType.GAUGE)
        except Exception as e:
            self.logger.error(f'Health check failed for {endpoint_name}: {e}')
            error_result = {'healthy': False, 'error': str(e)}
            self.health_check_results[endpoint_name] = error_result
            self.emit_metric(f'health_check_{endpoint_name}', 0.0, MetricType.GAUGE)

def _run_health_checks(self):
    """Run health checks for all registered endpoints"""
    for endpoint_name, endpoint in self.health_endpoints.items():
        try:
            now = datetime.now()
            if endpoint.last_check_time is None or (now - endpoint.last_check_time).total_seconds() >= endpoint.check_interval_seconds:
                health_result = endpoint.health_check_function()
                endpoint.last_check_time = now
                endpoint.last_result = health_result
                self.health_check_results[endpoint_name] = health_result
        except Exception as e:
            error_result = {'healthy': False, 'error': str(e), 'timestamp': datetime.now().isoformat()}
            self.health_check_results[endpoint_name] = error_result
            self.emit_structured_log('error', f'Health check failed for {endpoint_name}: {str(e)}', component='health_monitoring', endpoint_name=endpoint_name)

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

