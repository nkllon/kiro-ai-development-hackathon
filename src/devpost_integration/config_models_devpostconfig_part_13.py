from src.rm_ddd.core.health import ModuleHealth

    def _identify_health_issues(self) -> List[str]:
        """Identify health issues."""
        issues = []
        if self._errors > 0:
            issues.append(f'Configuration errors: {self._errors}')
        if not self.config_data:
            issues.append('Missing configuration data')
        return issues
