from src.rm_ddd.core.health import ModuleHealth

def get_setting(self, key: str, default: Any=None) -> Any:
    """Get setting value by key."""
    try:
        return self.settings_data.get(key, default)
    except Exception as e:
        logger.error(f'Failed to get setting: {e}')
        self._errors += 1
        return default

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

