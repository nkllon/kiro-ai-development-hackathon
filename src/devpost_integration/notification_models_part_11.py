
    def check_health(self) -> ModuleHealth:
        """Check module health."""
        issues = []
        health_score = self._calculate_health_score()
        if self._errors > 0:
            issues.append(f'{self._errors} internal errors occurred')
        if not self.channels:
            issues.append('No notification channels configured')
        if self.enabled and (not self.channels):
            issues.append('Notifications enabled but no channels available')
        status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
        return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())
