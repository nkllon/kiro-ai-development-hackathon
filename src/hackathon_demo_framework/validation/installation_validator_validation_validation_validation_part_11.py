
def _test_installation_process(self) -> Dict[str, Any]:
    """Test the actual installation process in a clean environment."""
    issues = []
    score = 100
    try:
        if (self.project_path / 'src').exists():
            import importlib.util
from src.rm_ddd.core.health import ModuleHealth

            init_file = self.project_path / 'src' / '__init__.py'
            if init_file.exists():
                spec = importlib.util.spec_from_file_location('test_module', init_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
    except ImportError as e:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='major', message=f'Import test failed: {e}', suggestion='Fix import issues or missing dependencies'))
        score -= 30
    except Exception as e:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.INSTALLATION_FAILURE, severity='minor', message=f'Installation test error: {e}', suggestion='Review project structure and dependencies'))
        score -= 10
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

