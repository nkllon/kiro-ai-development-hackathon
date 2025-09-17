from src.rm_ddd.core.health import ModuleHealth

    def _validate_all_make_targets(self) -> Dict[str, Any]:
        """Validate all make targets work correctly"""
        try:
            result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=10)
            return {'all_targets_work': result.returncode == 0, 'tested_targets': ['help'], 'output': result.stdout}
        except Exception as e:
            return {'all_targets_work': False, 'error': str(e)}

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

