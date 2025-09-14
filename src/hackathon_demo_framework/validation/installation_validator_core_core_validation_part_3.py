
def _validate_configuration_files(self) -> Dict[str, Any]:
    """Validate presence and quality of configuration files."""
    issues = []
    score = 100
    config_files_found = []
    for config_file in self.config_files:
        if (self.project_path / config_file).exists():
            config_files_found.append(config_file)
    if not config_files_found:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.MISSING_REQUIREMENTS, severity='critical', message='No dependency configuration files found', suggestion='Add requirements.txt, pyproject.toml, or setup.py'))
        score = 0
    else:
        for config_file in config_files_found:
            file_path = self.project_path / config_file
            file_issues = self._validate_config_file(file_path)
            issues.extend(file_issues)
            if file_issues:
                score -= len(file_issues) * 10
    return {'score': max(0, score), 'issues': issues}
