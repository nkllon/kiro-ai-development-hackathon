
def _update_error_metrics(self, health_metrics: HealthMonitoringMetrics, current_time: datetime) -> None:
    """Update error metrics for component"""
    health_metrics.error_count_last_hour += 1
    health_metrics.error_count_last_day += 1
    health_metrics.success_rate_last_hour *= 0.95
    health_metrics.success_rate_last_day *= 0.99
