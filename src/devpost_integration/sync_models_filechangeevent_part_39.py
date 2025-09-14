
def _identify_health_issues(self) -> List[str]:
    """Identify health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Internal errors: {self._errors}')
    if not self.file_path:
        issues.append('Missing file path')
    if self.file_size < 0:
        issues.append(f'Invalid file size: {self.file_size}')
    return issues
