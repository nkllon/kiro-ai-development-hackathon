
def _validate_pyproject_toml(self, file_path: Path, content: str) -> List[InstallationIssue]:
    """Validate pyproject.toml file."""
    issues = []
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='minor', message='Cannot validate pyproject.toml - TOML parser not available', file_path=str(file_path), suggestion='Install tomli or use Python 3.11+'))
            return issues
    try:
        data = tomllib.loads(content)
        if 'project' not in data and 'tool' not in data:
            issues.append(InstallationIssue(issue_type=InstallationIssueType.MISSING_REQUIREMENTS, severity='major', message='pyproject.toml missing project or tool sections', file_path=str(file_path), suggestion='Add [project] section with dependencies'))
        if 'project' in data:
            project = data['project']
            if 'dependencies' not in project and 'requires' not in project:
                issues.append(InstallationIssue(issue_type=InstallationIssueType.MISSING_REQUIREMENTS, severity='minor', message='No dependencies specified in pyproject.toml', file_path=str(file_path), suggestion='Add dependencies list if project has requirements'))
    except Exception as e:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='major', message=f'Invalid pyproject.toml format: {e}', file_path=str(file_path), suggestion='Fix TOML syntax errors'))
    return issues
