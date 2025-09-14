from src.rm_ddd.core.health import ModuleHealth

    def get_module_status(self) -> Dict[str, Any]:
        """
        Operational visibility - external status reporting for GKE queries
        Required by R6.4 - external systems get accurate operational information
        """
        return self._status_reporter.generate_module_status(
            self._backlog_items,
            self.is_healthy(),
            self._degradation_mode,
            self._health_monitor.get_performance_metrics()
        )
        