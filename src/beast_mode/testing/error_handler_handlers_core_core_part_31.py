from src.rm_ddd.core.health import ModuleHealth

def _assess_component_health(self, health_metrics: HealthMonitoringMetrics) -> bool:
    """Assess if component is healthy based on metrics"""
    return health_metrics.success_rate_last_hour > 0.7 and health_metrics.error_count_last_hour < 10 and (health_metrics.average_response_time_ms < 5000)

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

