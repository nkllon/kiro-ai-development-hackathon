"""
Observability-based patch detection module.

This module provides automated patch detection through observability signals
including Jaeger distributed tracing and Prometheus metrics analysis.
"""

from .patch_detector import (
    ObservabilityPatchDetector,
    PerformanceAnomaly,
    MetricsAnomaly,
    TraceCorrelation,
    SuspiciousPattern,
    WorkaroundCandidate
)

__all__ = [
    'ObservabilityPatchDetector',
    'PerformanceAnomaly', 
    'MetricsAnomaly',
    'TraceCorrelation',
    'SuspiciousPattern',
    'WorkaroundCandidate'
]