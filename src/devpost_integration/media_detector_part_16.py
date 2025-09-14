from src.rm_ddd.core.health import ModuleHealth

    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={
                'supported_formats': self.get_supported_formats(),
                'recursive_scan': True
            },
            required_parameters=[],
            optional_parameters=['recursive_scan'],
            validation_rules={
                'recursive_scan': [True, False]
            },
            last_updated=datetime.now()
        )

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

    