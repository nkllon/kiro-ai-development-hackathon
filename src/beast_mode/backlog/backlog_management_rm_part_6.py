
    def __init__(self):
        super().__init__("BacklogManagementRM")
        self._backlog_items: Dict[str, BacklogItem] = {}
        self._degradation_mode = False
        self._initialization_time = time.time()
        
        # Initialize helper components
        self._health_monitor = BacklogHealthMonitor()
        self._status_reporter = BacklogOperationalStatus("BacklogManagementRM", self._initialization_time)
        self._core_operations = BacklogCoreOperations(
            self.logger, 
            self._health_monitor, 
            lambda: self._degradation_mode
        )
        
        # Initialize health indicators
        self._health_monitor.update_health_indicator(
            "initialization", 
            HealthStatus.HEALTHY, 
            True, 
            "BacklogManagementRM initialized successfully"
        )
        