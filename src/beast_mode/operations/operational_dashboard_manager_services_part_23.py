from src.rm_ddd.core.health import ModuleHealth

    def _check_data_retention_compliance(self) -> bool:
        """Check if data retention policies are being followed"""
        for dashboard_id, config in self.dashboards.items():
            if dashboard_id in self.data_history:
                cutoff_time = datetime.now() - timedelta(hours=config.data_retention_hours)
                old_entries = [entry for entry in self.data_history[dashboard_id] if entry.timestamp <= cutoff_time]
                if old_entries:
                    return False
        return True
