from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, error_handler: Optional[RCAErrorHandler]=None):
        super().__init__('test_failure_detector')
        self.error_handler = error_handler or RCAErrorHandler()
        self.total_test_runs_monitored = 0
        self.total_failures_detected = 0
        self.parsing_success_rate = 0.0
        self.pytest_output_patterns = {'failure_header': '^FAILURES\\s*$', 'test_failure_start': '^_{20,}\\s+(.+?)\\s+_{20,}$', 'test_node_id': '^(.+?)::\\s*(.+?)(?:\\s+FAILED)?$', 'error_line': '^E\\s+(.+)$', 'traceback_line': '^>\\s+(.+)$', 'assertion_error': '^>?\\s*assert\\s+(.+)$', 'import_error': 'ImportError:\\s*(.+)$', 'file_not_found': 'FileNotFoundError:\\s*(.+)$'}
        self._update_health_indicator('test_failure_detection_readiness', HealthStatus.HEALTHY, 'ready', 'Test failure detector ready for pytest monitoring')
