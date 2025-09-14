from src.rm_ddd.core.health import ModuleHealth

    def _identify_health_issues(self) -> List[str]:
        """Identify health issues."""
        issues = []
        if self._errors > 0:
            issues.append(f'Internal errors: {self._errors}')
        if not self.channels:
            issues.append('No notification channels')
        if self.enabled and (not self.channels):
            issues.append('Enabled but no channels')
        return issues
