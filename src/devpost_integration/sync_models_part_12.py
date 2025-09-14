from src.rm_ddd.core.health import ModuleHealth

    def _identify_health_issues(self) -> List[str]:
        """Identify health issues."""
        issues = []
        if self._errors > 0:
            issues.append(f'Internal errors: {self._errors}')
        if not self.success:
            issues.append('Sync operation failed')
        if self.records_failed > 0:
            issues.append(f'Failed records: {self.records_failed}')
        return issues
