from src.rm_ddd.core.health import ModuleHealth

class GethealthindicatorsClass:
    """Auto-generated class for functions."""

    def get_health_indicators(self) -> Dict[str, Any]:
    """
    Self-reporting - detailed health metrics for operational visibility
    Required by R6.2 - components report health status accurately
    """
    # Update performance health indicator
    metrics = self._health_monitor.get_performance_metrics()
    avg_response_time = metrics["avg_response_time"]

    perf_status = HealthStatus.HEALTHY
    perf_message = "Performance within acceptable limits"

    if avg_response_time > 0.5:
    perf_status = HealthStatus.UNHEALTHY
    perf_message = f"Average response time {avg_response_time:.3f}s exceeds 500ms limit"
    elif avg_response_time > 0.3:
    perf_status = HealthStatus.DEGRADED
    perf_message = f"Average response time {avg_response_time:.3f}s approaching limit"

    self._health_monitor.update_health_indicator(
    "performance", perf_status, avg_response_time, perf_message
    )

    # Update data consistency health indicator
    consistency_healthy = self._health_monitor.validate_data_consistency(self._backlog_items)
    self._health_monitor.update_health_indicator(
    "data_consistency",
    HealthStatus.HEALTHY if consistency_healthy else HealthStatus.UNHEALTHY,
    consistency_healthy,
    "Data consistency validated" if consistency_healthy else "Data consistency issues detected"
    )

    # Update capacity health indicator
    capacity_ratio = len(self._backlog_items) / 10000  # Assume 10k is max capacity
    capacity_status = self._health_monitor.calculate_capacity_status(len(self._backlog_items))

    self._health_monitor.update_health_indicator(
    "capacity", capacity_status, capacity_ratio, f"Using {capacity_ratio:.1%} of estimated capacity"
    )

    health_indicators = self._health_monitor.get_health_indicators()
    return {
    "health_indicators": {
    name: {
    "status": indicator.status.value,
    "value": indicator.value,
    "message": indicator.message,
    "timestamp": indicator.timestamp
    }
    for name, indicator in health_indicators.items()
    },
    "overall_health": self.is_healthy(),
    "degradation_active": self._degradation_mode,
    "metrics": metrics
    }

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

