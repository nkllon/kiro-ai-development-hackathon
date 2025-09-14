from src.rm_ddd.core.health import ModuleHealth

    def _identify_health_issues(self) -> List[str]:
        """Identify health issues."""
        issues = []
        if self._errors > 0:
            issues.append(f'Internal errors: {self._errors}')
        if not self.message_id:
            issues.append('Missing message ID')
        if not self.title:
            issues.append('Missing message title')
        if not self.content:
            issues.append('Missing message content')
        if not self.recipients:
            issues.append('Missing recipients')
        return issues
