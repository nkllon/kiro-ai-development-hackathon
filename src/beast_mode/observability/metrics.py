#!/usr/bin/env python3
"""
Observability Metrics - Core metric definitions
==============================================

This module defines core metric classes and types used throughout
the observability system.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Define missing Metric class and related types
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

class MetricType(Enum):
    """Types of metrics supported by the monitoring system."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"

    @dataclass
class Metric:
    """Core metric class for observability system."""

    name: str
    value: Union[float, int]
    metric_type: MetricType
    timestamp: Optional[datetime] = None
    labels: Optional[Dict[str, str]] = None
    description: Optional[str] = None

def __post_init__(self):
    """Initialize default values after dataclass creation."""
if self.timestamp is None:
    self.timestamp = datetime.now()
if self.labels is None:
    self.labels = {}

class PostinitClass:
    """Auto-generated class for functions."""

    def to_dict(self) -> Dict[str, Any]:
    """Convert metric to dictionary representation."""
    return {
    'name': self.name,
    'value': self.value,
    'type': self.metric_type.value,
    'timestamp': self.timestamp.isoformat() if self.timestamp else None,
    'labels': self.labels or {},
    'description': self.description
    }

    def __str__(self) -> str:
    """String representation of metric."""
    return f"Metric(name='{self.name}', value={self.value}, type={self.metric_type.value})"

    @dataclass
    class AlertRule:
    """Alert rule definition."""

    name: str
    metric_name: str
    threshold: Union[float, int]
    comparison: str  # 'greater_than', 'less_than', 'equals'
    severity: str = "warning"
    description: Optional[str] = None
    enabled: bool = True

    @dataclass
    class HealthEndpoint:
    """Health check endpoint definition."""

    name: str
    health_check_function: callable
    check_interval_seconds: int = 60
    last_check_time: Optional[datetime] = None
    last_result: Optional[Dict[str, Any]] = None

    class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    class AlertStatus(Enum):
    """Alert status states."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"

    # Export all classes and enums
    __all__ = [
    'Metric',
    'MetricType',
    'AlertRule',
    'HealthEndpoint',
    'AlertSeverity',
    'AlertStatus'
    ]
