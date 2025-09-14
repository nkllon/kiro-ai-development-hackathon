
def _validate_config_file(self, file_path: Path) -> List[InstallationIssue]:
    """Validate a specific configuration file."""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if file_path.name == 'requirements.txt':
            issues.extend(self._validate_requirements_txt(file_path, content))
        elif file_path.name == 'pyproject.toml':
            issues.extend(self._validate_pyproject_toml(file_path, content))
        elif file_path.name == 'setup.py':
            issues.extend(self._validate_setup_py(file_path, content))
    except Exception as e:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='major', message=f'Cannot read {file_path.name}: {e}', file_path=str(file_path), suggestion='Fix file encoding or permissions'))
    return issues
