
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for dashboard manager"""
        return {'dashboard_status': {'total_dashboards': self.dashboard_metrics['total_dashboards'], 'active_dashboards': self.dashboard_metrics['active_dashboards'], 'data_collection_rate': self.dashboard_metrics['data_points_collected'], 'average_refresh_time': self.dashboard_metrics['average_refresh_time_ms']}, 'data_management': {'total_data_points': sum((len(history) for history in self.data_history.values())), 'dashboard_data_size': len(self.dashboard_data), 'oldest_data_age_hours': self._get_oldest_data_age_hours(), 'data_retention_compliance': self._check_data_retention_compliance()}}
