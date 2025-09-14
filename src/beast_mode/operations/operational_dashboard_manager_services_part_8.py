
    def is_healthy(self) -> bool:
        """Health assessment for dashboard manager"""
        return self.project_root.exists() and len(self.dashboards) > 0 and (not self._degradation_active)
