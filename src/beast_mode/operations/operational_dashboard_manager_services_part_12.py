from src.rm_ddd.core.health import ModuleHealth

    def update_dashboard_data(self, dashboard_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update dashboard data
        """
        try:
            if dashboard_id not in self.dashboards:
                return {'error': f'Dashboard {dashboard_id} not found'}
            dashboard_data = DashboardData(dashboard_id=dashboard_id, timestamp=datetime.now(), data=data, metadata={'data_size': len(str(data)), 'update_source': 'system'})
            self.dashboard_data[dashboard_id] = dashboard_data
            self.data_history[dashboard_id].append(dashboard_data)
            self._cleanup_old_data(dashboard_id)
            self.dashboard_metrics['data_points_collected'] += 1
            self.dashboard_metrics['last_update_timestamp'] = datetime.now()
            return {'success': True, 'dashboard_id': dashboard_id, 'timestamp': dashboard_data.timestamp, 'data_points': len(self.data_history[dashboard_id])}
        except Exception as e:
            self.logger.error(f'Dashboard data update failed: {str(e)}')
            return {'error': f'Data update failed: {str(e)}'}

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

