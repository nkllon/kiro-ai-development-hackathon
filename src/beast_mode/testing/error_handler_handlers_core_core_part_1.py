
def __init__(self, retry_config: Optional[RetryConfiguration]=None):
    super().__init__('rca_error_handler')
    self.retry_config = retry_config or RetryConfiguration()
    self.error_history: List[ErrorContext] = []
    self.component_health: Dict[str, HealthMonitoringMetrics] = {}
    self.degradation_level = DegradationLevel.NONE
    self.total_errors_handled = 0
    self.successful_recoveries = 0
    self.fallback_reports_generated = 0
    self.retry_attempts_made = 0
    self.successful_retries = 0
    self.health_check_interval_seconds = 60
    self.last_health_check = datetime.now()
    self.monitored_components = ['rca_engine', 'test_failure_detector', 'rca_integration_engine', 'report_generator', 'pattern_library']
    self._initialize_component_health()
    self._update_health_indicator('rca_error_handler_readiness', HealthStatus.HEALTHY, 'ready', 'RCA error handler ready for comprehensive error management')

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

