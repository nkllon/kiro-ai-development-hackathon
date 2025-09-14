
def _identify_health_issues(self) -> List[str]:
    """Identify health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Internal errors: {self._errors}')
    if not self.project_id:
        issues.append('Missing project ID')
    if not self.title:
        issues.append('Missing project title')
    if not self.description:
        issues.append('Missing project description')
    return issues
