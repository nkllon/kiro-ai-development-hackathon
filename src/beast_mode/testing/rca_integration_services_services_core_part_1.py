from src.rm_ddd.core.health import ModuleHealth

def __init__(self, rca_engine: Optional[RCAEngine]=None, performance_monitor: Optional[RCAPerformanceMonitor]=None, timeout_handler: Optional[RCATimeoutHandler]=None, test_pattern_library: Optional[TestPatternLibrary]=None, error_handler: Optional[RCAErrorHandler]=None):
    super().__init__('test_rca_integrator')
    self.rca_engine = rca_engine or RCAEngine()
    self.test_pattern_library = test_pattern_library or TestPatternLibrary()
    self.performance_monitor = performance_monitor or RCAPerformanceMonitor(ResourceLimits(max_memory_mb=512, max_cpu_percent=80.0, timeout_seconds=30, warning_threshold_seconds=25, memory_warning_threshold_mb=400))
    self.timeout_handler = timeout_handler or RCATimeoutHandler(TimeoutConfiguration(primary_timeout_seconds=30, warning_timeout_seconds=25, graceful_timeout_seconds=20, hard_timeout_seconds=35, strategy=TimeoutStrategy.GRACEFUL_DEGRADATION, enable_progressive_degradation=True, max_degradation_levels=3))
    self.error_handler = error_handler or RCAErrorHandler()
    self.performance_monitor.start_monitoring()
    self.total_test_failures_processed = 0
    self.successful_rca_analyses = 0
    self.pattern_matches_found = 0
    self.total_analysis_time = 0.0
    self.max_failures_per_group = 10
    self.analysis_timeout_seconds = 30
    self._update_health_indicator('test_rca_integration_readiness', HealthStatus.HEALTHY, 'ready', 'Test RCA integration layer ready for failure analysis')

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

