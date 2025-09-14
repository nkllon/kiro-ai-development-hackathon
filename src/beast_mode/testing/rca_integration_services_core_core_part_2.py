from src.rm_ddd.core.health import ModuleHealth

def get_module_status(self) -> Dict[str, Any]:
    """Operational visibility for external systems"""
    return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'test_failures_processed': self.total_test_failures_processed, 'successful_rca_analyses': self.successful_rca_analyses, 'pattern_matches_found': self.pattern_matches_found, 'average_analysis_time': self.total_analysis_time / max(1, self.successful_rca_analyses), 'rca_engine_status': self.rca_engine.get_module_status() if self.rca_engine else 'unavailable', 'test_pattern_library_status': self.test_pattern_library.get_module_status(), 'performance_monitor_status': self.performance_monitor.get_module_status(), 'timeout_handler_status': self.timeout_handler.get_module_status(), 'degradation_active': self._degradation_active}

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

