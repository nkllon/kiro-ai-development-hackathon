from src.rm_ddd.core.health import ModuleHealth

def _validate_setup_py(self, file_path: Path, content: str) -> List[InstallationIssue]:
    """Validate setup.py file."""
    issues = []
    if 'setup(' not in content:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='major', message='setup.py missing setup() call', file_path=str(file_path), suggestion='Add proper setup() function call'))
    if 'install_requires' not in content:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.MISSING_REQUIREMENTS, severity='minor', message='setup.py missing install_requires', file_path=str(file_path), suggestion='Add install_requires list if project has dependencies'))
    return issues

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

