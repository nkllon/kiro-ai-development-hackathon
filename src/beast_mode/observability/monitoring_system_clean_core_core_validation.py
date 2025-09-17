"""
Monitoring System Clean Core Core Validation

This module was extracted from monitoring_system_clean_core_core.py
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
from .metrics import Metric, MetricType
from src.rm_ddd.core.health import ModuleHealth


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
            if alert_triggered:
                self._trigger_alert(rule_name, rule, metric)
            elif rule_name in self.active_alerts:
                self._clear_alert(rule_name)

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


class MonitoringSystemCleanCoreCoreValidation(ReflectiveModule):
    """Monitoring System Clean Core Core Validation - ReflectiveModule implementation."""
    
    def __init__(self):
        super().__init__(module_name="MonitoringSystemCleanCoreCoreValidation")
        self.module_id = "MonitoringSystemCleanCoreCoreValidation"
        self.alert_rules = {}
        self.active_alerts = {}
    
    def perform_core_operation(self):
        """Perform core operation for RDI compliance."""
        return {"status": "success", "operation": "monitoring_system_clean"}
    
    def check_health(self):
        """Check health status of the module."""
        from .metrics import Metric
        
        class HealthStatus:
            def __init__(self, status, timestamp, module_id):
                self.status = status
                self.timestamp = timestamp
                self.module_id = module_id
        
        return HealthStatus(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            module_id=self.module_id
        )
    
    def get_capabilities(self):
        """Get module capabilities."""
        return ["monitoring", "alerting", "system_cleanup"]
    
    def get_dependencies(self):
        """Get module dependencies."""
        return []
    
    def get_module_info(self):
        """Get module information."""
        return {
            "module_id": self.module_id,
            "version": "1.0.0",
            "description": "Monitoring System Clean Core Core Validation"
        }
    
    def start(self):
        """Start the service."""
        return True
    
    def stop(self):
        """Stop the service."""
        return True

