from src.rm_ddd.core.health import ModuleHealth

    def get_all_dashboards(self) -> Dict[str, Any]:
        """Get information about all dashboards"""
        return {dashboard_id: {'title': config.title, 'type': config.dashboard_type.value, 'enabled': config.enabled, 'refresh_interval': config.refresh_interval_seconds, 'last_update': self.dashboard_data[dashboard_id].timestamp if dashboard_id in self.dashboard_data and self.dashboard_data[dashboard_id] else None, 'data_points': len(self.data_history.get(dashboard_id, []))} for dashboard_id, config in self.dashboards.items()}

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

