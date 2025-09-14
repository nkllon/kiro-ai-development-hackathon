from src.rm_ddd.core.health import ModuleHealth

class ValidatedocumentationClass:
    """Auto-generated class for functions."""

    def _validate_documentation(self) -> Dict[str, Any]:
    """Validate installation documentation quality."""
    issues = []
    score = 100
    readme_path = None
    for readme_name in ['README.md', 'README.rst', 'README.txt']:
    if (self.project_path / readme_name).exists():
    readme_path = self.project_path / readme_name
    break
    if not readme_path:
    issues.append(InstallationIssue(issue_type=InstallationIssueType.DOCUMENTATION, severity='critical', message='No README file found', suggestion='Add README.md with project description and setup instructions'))
    score = 0
    else:
    try:
    with open(readme_path, 'r', encoding='utf-8') as f:
    content = f.read()
    if len(content.strip()) < 100:
    issues.append(InstallationIssue(issue_type=InstallationIssueType.DOCUMENTATION, severity='major', message='README too short', file_path=str(readme_path), suggestion='Expand README with detailed project information'))
    score -= 30
    essential_sections = ['installation', 'usage', 'setup']
    missing_sections = []
    for section in essential_sections:
    if section not in content.lower():
    missing_sections.append(section)
    if missing_sections:
    issues.append(InstallationIssue(issue_type=InstallationIssueType.DOCUMENTATION, severity='major', message=f"README missing sections: {', '.join(missing_sections)}", file_path=str(readme_path), suggestion='Add missing sections to README'))
    score -= len(missing_sections) * 15
    except Exception as e:
    issues.append(InstallationIssue(issue_type=InstallationIssueType.DOCUMENTATION, severity='major', message=f'Cannot read README: {e}', file_path=str(readme_path), suggestion='Fix README file encoding or permissions'))
    score -= 20
    return {'score': max(0, score), 'issues': issues}

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

