from src.rm_ddd.core.health import ModuleHealth

    def _complete_makefile_modules(self, missing_files: List[str]) -> str:
        """Complete missing Makefile modules"""
        return self._create_modular_makefile_system()

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

