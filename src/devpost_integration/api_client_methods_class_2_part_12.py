from src.rm_ddd.core.health import ModuleHealth

    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration"""
        try:
            if hasattr(config, 'api_key'):
                self.api_key = config.api_key
            if hasattr(config, 'base_url'):
                self.base_url = config.base_url
            return True
        except Exception as e:
            logger.error(f"Configuration update failed: {e}")
            return False

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

    