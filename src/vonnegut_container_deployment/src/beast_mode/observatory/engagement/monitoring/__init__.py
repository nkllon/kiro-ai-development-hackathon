"""
Engagement Monitoring Integration

Comprehensive monitoring integration for the engagement system with Observatory's
existing Prometheus metrics collection and health monitoring infrastructure.
"""

from .engagement_metrics import EngagementMetricsCollector, EngagementMetric, AttentionSession, InteractionEvent
from .prometheus_integration import (
    EngagementPrometheusIntegration,
    create_engagement_prometheus_integration,
    inject_engagement_metrics_into_observatory,
    get_engagement_prometheus_metrics
)
from .health_integration import (
    EngagementHealthMonitor,
    EngagementHealthStatus,
    EngagementHealthCheck,
    create_engagement_health_monitor,
    inject_engagement_health_into_observatory
)

__all__ = [
    # Core metrics
    "EngagementMetricsCollector",
    "EngagementMetric",
    "AttentionSession", 
    "InteractionEvent",
    
    # Prometheus integration
    "EngagementPrometheusIntegration",
    "create_engagement_prometheus_integration",
    "inject_engagement_metrics_into_observatory",
    "get_engagement_prometheus_metrics",
    
    # Health monitoring
    "EngagementHealthMonitor",
    "EngagementHealthStatus",
    "EngagementHealthCheck",
    "create_engagement_health_monitor",
    "inject_engagement_health_into_observatory"
]