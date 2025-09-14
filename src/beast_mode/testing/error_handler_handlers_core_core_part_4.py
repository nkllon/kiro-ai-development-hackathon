from src.rm_ddd.core.health import ModuleHealth

class GethealthindicatorsClass:
    """Auto-generated class for functions."""

    def get_health_indicators(self) -> Dict[str, Any]:
    """Detailed health metrics for operational visibility"""
    return {'error_handling_capability': {'status': 'healthy' if not self._degradation_active else 'degraded', 'errors_handled': self.total_errors_handled, 'recovery_rate': self.successful_recoveries / max(1, self.total_errors_handled)}, 'component_monitoring': {'status': 'healthy' if self._get_overall_component_health() > 0.7 else 'degraded', 'monitored_components': len(self.monitored_components), 'healthy_components': len([c for c in self.component_health.values() if c.is_healthy]), 'overall_health_score': self._get_overall_component_health()}, 'degradation_management': {'status': 'healthy' if self.degradation_level.value <= DegradationLevel.MINIMAL.value else 'degraded', 'current_level': self.degradation_level.value, 'fallback_reports': self.fallback_reports_generated, 'graceful_degradation': 'active' if self.degradation_level.value > 0 else 'inactive'}}

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

