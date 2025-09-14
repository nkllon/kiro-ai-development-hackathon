from src.rm_ddd.core.health import ModuleHealth

def _assess_component_health(self, health_metrics: HealthMonitoringMetrics) -> bool:
    """Assess if component is healthy based on metrics"""
    return health_metrics.success_rate_last_hour > 0.7 and health_metrics.error_count_last_hour < 10 and (health_metrics.average_response_time_ms < 5000)
