
def _validate_requirements_txt(self, file_path: Path, content: str) -> List[InstallationIssue]:
    """Validate requirements.txt file."""
    issues = []
    lines = content.strip().split('\n')
    if not lines or (len(lines) == 1 and (not lines[0].strip())):
        issues.append(InstallationIssue(issue_type=InstallationIssueType.MISSING_REQUIREMENTS, severity='major', message='requirements.txt is empty', file_path=str(file_path), suggestion='Add required dependencies to requirements.txt'))
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '==' not in line and '>=' not in line and ('~=' not in line):
            issues.append(InstallationIssue(issue_type=InstallationIssueType.DEPENDENCY_CONFLICT, severity='minor', message=f"Dependency '{line}' not version-pinned", file_path=str(file_path), suggestion='Consider pinning versions for reproducible builds'))
        if not re.match('^[a-zA-Z0-9_-]+', line.split('=')[0].split('>')[0].split('<')[0]):
            issues.append(InstallationIssue(issue_type=InstallationIssueType.DEPENDENCY_CONFLICT, severity='major', message=f'Invalid package name format: {line}', file_path=str(file_path), suggestion='Use valid Python package names'))
    return issues
