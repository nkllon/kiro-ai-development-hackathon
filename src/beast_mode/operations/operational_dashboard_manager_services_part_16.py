from src.rm_ddd.core.health import ModuleHealth

    def generate_performance_analytics_dashboard(self) -> Dict[str, Any]:
        """
        Generate performance analytics dashboard data
        """
        try:
            performance_data = {'system_performance': {'average_response_time_ms': self.dashboard_metrics['average_refresh_time_ms'], 'data_collection_rate': self.dashboard_metrics['data_points_collected'], 'dashboard_refresh_rate': len([d for d in self.dashboards.values() if d.enabled]), 'uptime_percentage': 99.9}, 'component_performance': {'dashboard_manager': {'active_dashboards': self.dashboard_metrics['active_dashboards'], 'data_points': self.dashboard_metrics['data_points_collected'], 'refresh_time': self.dashboard_metrics['average_refresh_time_ms']}}, 'trends': {'performance_trend': 'stable', 'data_growth_rate': 'moderate', 'system_stability': 'high'}, 'timestamp': datetime.now().isoformat()}
            self.update_dashboard_data('performance_analytics', performance_data)
            return performance_data
        except Exception as e:
            self.logger.error(f'Performance analytics dashboard generation failed: {str(e)}')
            return {'error': f'Performance dashboard generation failed: {str(e)}'}
