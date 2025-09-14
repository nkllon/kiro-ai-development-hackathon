from src.rm_ddd.core.health import ModuleHealth

    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for operational visibility"""
        return {'detection_capability': {'status': 'healthy' if not self._degradation_active else 'degraded', 'runs_monitored': self.total_test_runs_monitored, 'failures_detected': self.total_failures_detected}, 'parsing_performance': {'status': 'healthy' if self.parsing_success_rate > 0.8 else 'degraded', 'success_rate': self.parsing_success_rate, 'pattern_matching': 'operational'}}

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

