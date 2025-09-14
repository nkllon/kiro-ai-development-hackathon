from src.rm_ddd.core.health import ModuleHealth

    def get_module_status(self) -> Dict[str, Any]:
        """Dashboard manager operational status"""
        return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'total_dashboards': self.dashboard_metrics['total_dashboards'], 'active_dashboards': self.dashboard_metrics['active_dashboards'], 'data_points_collected': self.dashboard_metrics['data_points_collected'], 'last_update': self.dashboard_metrics['last_update_timestamp']}
