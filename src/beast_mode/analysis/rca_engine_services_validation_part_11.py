from src.rm_ddd.core.health import ModuleHealth

def _analyze_test_environment(self, failure: Failure) -> Dict[str, Any]:
    """Analyze test environment factors"""
    env_analysis = {}
    try:
        env_analysis['python_available'] = subprocess.run(['python3', '--version'], capture_output=True).returncode == 0
        env_analysis['pytest_available'] = subprocess.run(['python3', '-m', 'pytest', '--version'], capture_output=True).returncode == 0
        env_analysis['venv_active'] = 'VIRTUAL_ENV' in os.environ
        env_analysis['tests_dir_exists'] = Path('tests').exists()
        env_analysis['conftest_exists'] = Path('tests/conftest.py').exists()
    except Exception as e:
        env_analysis['analysis_error'] = str(e)
    return env_analysis

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

