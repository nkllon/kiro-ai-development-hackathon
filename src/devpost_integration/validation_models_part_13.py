from src.rm_ddd.core.health import ModuleHealth

    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration."""
        return {
            "max_errors": 100,
            "max_warnings": 200,
            "validation_timeout": 30,
            "strict_mode": False
        }

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

    