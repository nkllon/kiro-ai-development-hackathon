
def _consider_degradation(self, component_name: str, health_metrics: HealthMonitoringMetrics) -> None:
    """Consider applying degradation based on component health"""
    if health_metrics.error_count_last_hour > 20:
        self.apply_graceful_degradation(DegradationLevel.SEVERE, f'Component {component_name} has {health_metrics.error_count_last_hour} errors in last hour')
    elif health_metrics.success_rate_last_hour < 0.5:
        self.apply_graceful_degradation(DegradationLevel.MODERATE, f'Component {component_name} success rate: {health_metrics.success_rate_last_hour:.1%}')
