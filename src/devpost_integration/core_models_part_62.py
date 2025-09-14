
def _identify_health_issues(self) -> List[str]:
    """Identify health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Metadata errors: {self._errors}')
    return issues
