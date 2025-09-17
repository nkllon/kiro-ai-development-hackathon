from src.rm_ddd.core.health import ModuleHealth

    def _cleanup_old_data(self, dashboard_id: str):
        """Clean up old dashboard data based on retention policy"""
        if dashboard_id not in self.data_history:
            return
        config = self.dashboards[dashboard_id]
        cutoff_time = datetime.now() - timedelta(hours=config.data_retention_hours)
        self.data_history[dashboard_id] = [entry for entry in self.data_history[dashboard_id] if entry.timestamp > cutoff_time]

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

