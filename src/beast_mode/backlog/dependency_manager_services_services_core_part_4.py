from src.rm_ddd.core.health import ModuleHealth

class GethealthindicatorsClass:
    """Auto-generated class for functions."""

    def get_health_indicators(self) -> Dict[str, Any]:
    """Detailed health metrics for operational visibility"""
    avg_time = self._get_avg_operation_time()
    perf_status = HealthStatus.HEALTHY
    perf_message = 'Performance within acceptable limits'
    if avg_time > 500:
    perf_status = HealthStatus.UNHEALTHY
    perf_message = f'Average operation time {avg_time:.1f}ms exceeds 500ms limit'
    elif avg_time > 300:
    perf_status = HealthStatus.DEGRADED
    perf_message = f'Average operation time {avg_time:.1f}ms approaching limit'
    self._update_health_indicator('performance', perf_status, avg_time, perf_message)
    consistency_healthy = self._validate_internal_consistency()
    self._update_health_indicator('data_consistency', HealthStatus.HEALTHY if consistency_healthy else HealthStatus.UNHEALTHY, consistency_healthy, 'Data consistency validated' if consistency_healthy else 'Data consistency issues detected')
    return {'health_indicators': {name: {'status': indicator.status.value, 'value': indicator.value, 'message': indicator.message, 'timestamp': indicator.timestamp} for name, indicator in self._health_indicators.items()}, 'overall_health': self.is_healthy(), 'performance_metrics': {'avg_operation_time_ms': avg_time, 'dependencies_count': len(self._dependencies), 'cache_hit_ratio': self._calculate_cache_hit_ratio()}}

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

