
def _identify_health_issues(self) -> List[str]:
    """Identify health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Internal errors: {self._errors}')
    if not self.member_id:
        issues.append('Missing member ID')
    if not self.name:
        issues.append('Missing member name')
    if not self.email:
        issues.append('Missing email address')
    return issues
