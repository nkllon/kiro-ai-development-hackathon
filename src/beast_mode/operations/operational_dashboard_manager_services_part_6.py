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
