from src.rm_ddd.core.health import ModuleHealth

def set_config_value(self, key: str, value: Any) -> bool:
    """Set configuration value by key."""
    try:
        self.config_data[key] = value
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to set config value: {e}')
        self._errors += 1
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

