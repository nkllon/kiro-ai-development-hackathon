"""
Monitoring System Clean Validation

This module was extracted from monitoring_system_clean.py
as part of RM-DDD compliance refactoring.
"""

import time
import json
import threading
from .metrics import Metric, MetricType
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import statistics
from ..core.reflective_module import ReflectiveModule, HealthStatus
from src.rm_ddd.core.health import ModuleHealth


class CheckalertrulesClass:
    """Auto-generated class for functions."""

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

