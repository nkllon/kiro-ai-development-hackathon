from src.rm_ddd.core.health import ModuleHealth

def _identify_health_issues(self) -> List[str]:
    """Identify specific health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Operation errors: {self._errors}')
    if self.status == 'failed':
        issues.append('Operation failed')
    if self.progress < 0 or self.progress > 1:
        issues.append(f'Invalid progress: {self.progress}')
    return issues
