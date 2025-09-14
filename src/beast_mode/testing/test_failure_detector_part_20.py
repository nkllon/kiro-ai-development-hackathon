from src.rm_ddd.core.health import ModuleHealth

    def _get_pytest_version(self) -> str:
        """Get pytest version for context"""
        try:
            result = subprocess.run(['python3', '-m', 'pytest', '--version'], capture_output=True, text=True, timeout=10)
            return result.stdout.strip() if result.returncode == 0 else 'unknown'
        except:
            return 'unknown'

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

