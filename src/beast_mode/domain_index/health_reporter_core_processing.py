"""
Health Reporter Core Processing

This module was extracted from health_reporter_core.py
as part of RM-DDD compliance refactoring.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
from .base import DomainSystemComponent
from .models import Domain, HealthStatus, HealthStatusType, HealthIssue, HealthMetrics, IssueSeverity, IssueCategory, HealthStatusCollection
from .exceptions import HealthReportError, AlertingError
from .config import get_config
from ..utils.enum_serialization import SerializationHandler
from ..utils.enum_serialization import make_enum_json_serializable
from ..utils.enum_serialization import make_enum_json_serializable
from src.rm_ddd.core.health import ModuleHealth


class ProcessalertsClass:
    """Auto-generated class for functions."""

    def _process_alerts(self, alerts: List[Alert]):
    """Process generated alerts through configured channels"""
    for alert in alerts:
    rule = next((r for r in self.alert_manager.alert_rules if r.name == alert.rule_name), None)
    if not rule:
    continue
    for channel in rule.channels:
    try:
    if channel == AlertChannel.LOG:
    self.logger.warning(f'ALERT [{alert.severity.value.upper()}]: {alert.title} - {alert.description}')
    elif channel == AlertChannel.CONSOLE:
    print(f'🚨 HEALTH ALERT: {alert.title}')
    print(f'   Severity: {alert.severity.value.upper()}')
    print(f'   Domain: {alert.domain_name}')
    print(f'   Description: {alert.description}')
    print(f'   Time: {alert.created_at}')
    except Exception as e:
    self.logger.error(f'Failed to send alert via {channel.value}: {e}')

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

