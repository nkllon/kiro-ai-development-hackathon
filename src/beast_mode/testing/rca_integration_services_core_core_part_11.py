from src.rm_ddd.core.health import ModuleHealth

class GetperformancereportClass:
    """Auto-generated class for functions."""

    def get_performance_report(self) -> Dict[str, Any]:
    """
    Get comprehensive performance report for RCA operations
    Requirements: 4.2 - Performance monitoring and metrics collection
    """
    try:
    performance_report = self.performance_monitor.get_performance_report()
    timeout_status = self.timeout_handler.get_module_status()
    return {'rca_integration_performance': {'total_operations': performance_report.total_operations, 'successful_operations': performance_report.successful_operations, 'timeout_operations': performance_report.timeout_operations, 'degraded_operations': performance_report.degraded_operations, 'average_duration_seconds': performance_report.average_duration_seconds, 'average_memory_usage_mb': performance_report.average_memory_usage_mb, 'peak_memory_usage_mb': performance_report.peak_memory_usage_mb, 'timeout_rate': performance_report.timeout_rate, 'degradation_rate': performance_report.degradation_rate, 'performance_trend': performance_report.performance_trend}, 'timeout_management': {'timeout_compliance_rate': 1.0 - timeout_status.get('hard_timeout_rate', 0.0), 'graceful_degradation_success_rate': timeout_status.get('successful_degradation_rate', 0.0), 'primary_timeout_seconds': timeout_status.get('primary_timeout_seconds', 30), 'timeout_strategy': timeout_status.get('timeout_strategy', 'graceful_degradation')}, 'integration_metrics': {'test_failures_processed': self.total_test_failures_processed, 'successful_rca_analyses': self.successful_rca_analyses, 'pattern_matches_found': self.pattern_matches_found, 'rca_success_rate': self.successful_rca_analyses / max(1, self.total_test_failures_processed), 'pattern_match_rate': self.pattern_matches_found / max(1, self.successful_rca_analyses)}}
    except Exception as e:
    self.logger.error(f'Failed to generate performance report: {e}')
    return {'error': str(e), 'timestamp': datetime.now().isoformat()}

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

