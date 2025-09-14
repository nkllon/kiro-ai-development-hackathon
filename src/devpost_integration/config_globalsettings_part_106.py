
def _identify_health_issues(self) -> List[str]:
    """Identify health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Settings errors: {self._errors}')
    if not self.settings_data:
        issues.append('Missing settings data')
    return issues
