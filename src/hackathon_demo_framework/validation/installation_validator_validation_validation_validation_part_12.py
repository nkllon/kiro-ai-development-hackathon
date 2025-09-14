from src.rm_ddd.core.health import ModuleHealth

def _test_single_installation(self, temp_dir: Path) -> Dict[str, Any]:
    """Test a single installation attempt in a temporary directory."""
    try:
        project_copy = temp_dir / 'project'
        shutil.copytree(self.project_path, project_copy, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git', 'venv', 'env', '.venv'))
        venv_path = temp_dir / 'venv'
        venv.create(venv_path, with_pip=True)
        if sys.platform == 'win32':
            pip_path = venv_path / 'Scripts' / 'pip'
        else:
            pip_path = venv_path / 'bin' / 'pip'
        if (project_copy / 'requirements.txt').exists():
            try:
                content = (project_copy / 'requirements.txt').read_text()
                lines = [line.strip() for line in content.split('\n') if line.strip() and (not line.startswith('#'))]
                for line in lines:
                    if any((char in line for char in ['!', '@', '#', '$', '%', '^', '&', '*'])):
                        return {'success': False, 'issues': [f'Invalid requirement: {line}']}
            except Exception as e:
                return {'success': False, 'issues': [f'Could not parse requirements: {e}']}
        return {'success': True, 'issues': []}
    except Exception as e:
        return {'success': False, 'issues': [f'Installation test failed: {e}']}

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

