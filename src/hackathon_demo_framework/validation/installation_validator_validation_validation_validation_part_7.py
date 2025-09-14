from src.rm_ddd.core.health import ModuleHealth

def _validate_setup_py(self, file_path: Path, content: str) -> List[InstallationIssue]:
    """Validate setup.py file."""
    issues = []
    if 'setup(' not in content:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='major', message='setup.py missing setup() call', file_path=str(file_path), suggestion='Add proper setup() function call'))
    if 'install_requires' not in content:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.MISSING_REQUIREMENTS, severity='minor', message='setup.py missing install_requires', file_path=str(file_path), suggestion='Add install_requires list if project has dependencies'))
    return issues
