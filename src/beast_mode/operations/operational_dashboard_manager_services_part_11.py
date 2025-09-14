from src.rm_ddd.core.health import ModuleHealth

    def create_dashboard(self, config: DashboardConfig) -> Dict[str, Any]:
        """
        Create new operational dashboard
        """
        try:
            if not self._validate_dashboard_config(config):
                return {'error': 'Invalid dashboard configuration'}
            self.dashboards[config.dashboard_id] = config
            self.dashboard_data[config.dashboard_id] = None
            self.data_history[config.dashboard_id] = []
            self.dashboard_metrics['total_dashboards'] += 1
            if config.enabled:
                self.dashboard_metrics['active_dashboards'] += 1
            self.logger.info(f'Dashboard created: {config.title} ({config.dashboard_id})')
            return {'success': True, 'dashboard_id': config.dashboard_id, 'title': config.title, 'type': config.dashboard_type.value}
        except Exception as e:
            self.logger.error(f'Dashboard creation failed: {str(e)}')
            return {'error': f'Dashboard creation failed: {str(e)}'}
