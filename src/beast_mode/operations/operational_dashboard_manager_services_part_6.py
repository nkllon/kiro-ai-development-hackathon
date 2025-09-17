from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, project_root: str='.'):
        super().__init__('operational_dashboard_manager')
        self.project_root = Path(project_root)
        self.dashboards = {}
        self.dashboard_data = {}
        self.data_history = {}
        self.dashboard_metrics = {'total_dashboards': 0, 'active_dashboards': 0, 'data_points_collected': 0, 'average_refresh_time_ms': 0.0, 'last_update_timestamp': None}
        self._initialize_default_dashboards()
        self._update_health_indicator('operational_dashboard_manager', HealthStatus.HEALTHY, 'operational', 'Operational dashboard manager ready for monitoring')

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

