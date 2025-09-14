
    def _initialize_default_dashboards(self):
        """Initialize default operational dashboards"""
        default_dashboards = [DashboardConfig(dashboard_id='health_monitoring', dashboard_type=DashboardType.HEALTH_MONITORING, title='Beast Mode Health Monitoring', description='Real-time health monitoring for all Beast Mode components', refresh_interval_seconds=30), DashboardConfig(dashboard_id='superiority_metrics', dashboard_type=DashboardType.SUPERIORITY_METRICS, title='Systematic Superiority Metrics', description='Concrete evidence of Beast Mode superiority over ad-hoc approaches', refresh_interval_seconds=60), DashboardConfig(dashboard_id='performance_analytics', dashboard_type=DashboardType.PERFORMANCE_ANALYTICS, title='Performance Analytics', description='System performance metrics and analytics', refresh_interval_seconds=45), DashboardConfig(dashboard_id='unknown_risks', dashboard_type=DashboardType.UNKNOWN_RISKS, title='Unknown Risk Mitigation', description='Status of unknown risk mitigation strategies', refresh_interval_seconds=120)]
        for config in default_dashboards:
            self.create_dashboard(config)
