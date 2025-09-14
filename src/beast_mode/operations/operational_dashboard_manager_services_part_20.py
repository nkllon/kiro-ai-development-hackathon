
    def _validate_dashboard_config(self, config: DashboardConfig) -> bool:
        """Validate dashboard configuration"""
        if not config.dashboard_id or not config.title:
            return False
        if config.refresh_interval_seconds <= 0:
            return False
        if config.data_retention_hours <= 0:
            return False
        return True
