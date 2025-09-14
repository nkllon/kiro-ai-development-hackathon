
    def _update_refresh_metrics(self, refresh_time_ms: int):
        """Update dashboard refresh metrics"""
        current_avg = self.dashboard_metrics['average_refresh_time_ms']
        total_refreshes = self.dashboard_metrics.get('total_refreshes', 0) + 1
        new_avg = (current_avg * (total_refreshes - 1) + refresh_time_ms) / total_refreshes
        self.dashboard_metrics['average_refresh_time_ms'] = new_avg
        self.dashboard_metrics['total_refreshes'] = total_refreshes
