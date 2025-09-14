
    def check_health(self) -> ModuleHealth:
        """Check module health with comprehensive monitoring."""
        issues = []
        health_score = self._calculate_health_score()
        if self._errors > 0:
            issues.append(f'{self._errors} errors occurred')
        if self.status == 'failed' and (not self.error_message):
            issues.append('Failed operation without error message')
        if self.progress < 0 or self.progress > 1:
            issues.append('Invalid progress value')
        if health_score >= 0.9:
            status = ModuleStatus.HEALTHY
        elif health_score >= 0.7:
            status = ModuleStatus.WARNING
        else:
            status = ModuleStatus.ERROR
        return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())
