
    def check_health(self) -> ModuleHealth:
        """Check module health."""
        issues = []
        health_score = 1.0
        if self._errors > 0:
            issues.append(f'{self._errors} errors occurred')
            health_score -= 0.2
        if not self.connected:
            issues.append('Not connected to project')
            health_score -= 0.3
        status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
        return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())
