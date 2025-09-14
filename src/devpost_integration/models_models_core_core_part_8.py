from src.rm_ddd.core.health import ModuleHealth

def update_configuration(self, config: Dict[str, Any]) -> bool:
    """Update module configuration"""
    try:
        if 'auto_validation_enabled' in config:
            self._logger.info(f"Auto validation enabled: {config['auto_validation_enabled']}")
        if 'metadata_schema_enforced' in config:
            self._logger.info(f"Schema enforcement enabled: {config['metadata_schema_enforced']}")
        return True
    except Exception as e:
        self._logger.error(f'Configuration update failed: {e}')
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

