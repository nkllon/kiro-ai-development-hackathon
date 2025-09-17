from src.rm_ddd.core.health import ModuleHealth

def _analyze_test_dependencies(self, failure: Failure) -> Dict[str, Any]:
    """Analyze test-specific dependency issues"""
    dep_analysis = {}
    try:
        dep_analysis['requirements_exists'] = Path('requirements.txt').exists()
        dep_analysis['pyproject_exists'] = Path('pyproject.toml').exists()
        dep_analysis['setup_py_exists'] = Path('setup.py').exists()
        result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
        dep_analysis['pip_list_available'] = result.returncode == 0
    except Exception as e:
        dep_analysis['analysis_error'] = str(e)
    return dep_analysis

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

