from src.rm_ddd.core.health import ModuleHealth

    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Get comprehensive dashboard analytics"""
        return {'dashboard_metrics': self.dashboard_metrics.copy(), 'dashboard_summary': self.get_all_dashboards(), 'data_statistics': {'total_data_points': sum((len(history) for history in self.data_history.values())), 'oldest_data_age_hours': self._get_oldest_data_age_hours(), 'retention_compliance': self._check_data_retention_compliance()}, 'system_health': {'manager_healthy': self.is_healthy(), 'active_dashboards': self.dashboard_metrics['active_dashboards'], 'data_collection_active': self.dashboard_metrics['data_points_collected'] > 0}}
