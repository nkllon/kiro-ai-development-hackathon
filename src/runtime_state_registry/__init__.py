"""
Runtime State Registry - Unified Multi-Source System State Management

This package provides comprehensive visibility into system state by bridging
the gap between expected state (Specifications), canonical configuration (CMS),
actual runtime state (Redis), and observability data (Prometheus/Grafana).
"""

from .core.runtime_state_registry import RuntimeStateRegistry
from .core.models import (
    UnifiedServiceState,
    ThreeLayerState,
    DriftDetection,
    ComplianceScore,
    ServiceStatus,
    DriftType,
    DriftSeverity
)

__version__ = "1.0.0"
__all__ = [
    "RuntimeStateRegistry",
    "UnifiedServiceState", 
    "ThreeLayerState",
    "DriftDetection",
    "ComplianceScore",
    "ServiceStatus",
    "DriftType",
    "DriftSeverity"
]