
    def _cleanup_old_data(self, dashboard_id: str):
        """Clean up old dashboard data based on retention policy"""
        if dashboard_id not in self.data_history:
            return
        config = self.dashboards[dashboard_id]
        cutoff_time = datetime.now() - timedelta(hours=config.data_retention_hours)
        self.data_history[dashboard_id] = [entry for entry in self.data_history[dashboard_id] if entry.timestamp > cutoff_time]
