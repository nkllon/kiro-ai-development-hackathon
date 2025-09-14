from src.rm_ddd.core.health import ModuleHealth

def get_health_indicators(self) -> Dict[str, Any]:
    """Detailed health metrics for operational visibility"""
    return {'integration_capability': {'status': 'healthy' if not self._degradation_active else 'degraded', 'failures_processed': self.total_test_failures_processed, 'success_rate': self.successful_rca_analyses / max(1, self.total_test_failures_processed)}, 'rca_engine_integration': {'status': 'healthy' if self.rca_engine and self.rca_engine.is_healthy() else 'degraded', 'engine_available': self.rca_engine is not None, 'pattern_match_rate': self.pattern_matches_found / max(1, self.successful_rca_analyses)}, 'performance': {'status': 'healthy' if self.total_analysis_time / max(1, self.successful_rca_analyses) < 30 else 'degraded', 'average_analysis_time': self.total_analysis_time / max(1, self.successful_rca_analyses), 'timeout_compliance': 'within_30_seconds'}}

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

