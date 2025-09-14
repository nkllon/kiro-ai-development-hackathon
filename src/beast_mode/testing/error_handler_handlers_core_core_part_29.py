from src.rm_ddd.core.health import ModuleHealth

def _update_success_metrics(self, health_metrics: HealthMonitoringMetrics) -> None:
    """Update success metrics for component"""
    health_metrics.success_rate_last_hour = min(1.0, health_metrics.success_rate_last_hour * 1.01)
    health_metrics.success_rate_last_day = min(1.0, health_metrics.success_rate_last_day * 1.001)
