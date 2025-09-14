from src.rm_ddd.core.health import ModuleHealth

def _generate_fallback_report(self, failure: Failure, error_context: ErrorContext) -> FallbackReportData:
    """Generate fallback report for single failure"""
    return FallbackReportData(error_summary=f'RCA analysis failed: {error_context.error_message[:200]}', basic_failure_info=[{'failure_id': failure.failure_id, 'component': failure.component, 'error_message': failure.error_message[:200], 'timestamp': failure.timestamp.isoformat()}], suggested_actions=['Check RCA engine configuration', 'Verify system resources', 'Review error logs for details', 'Retry with simplified parameters'], health_status=self.get_health_indicators(), timestamp=datetime.now(), degradation_level=self.degradation_level)

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

