from src.rm_ddd.core.health import ModuleHealth


def import_configuration(self, config_export: Dict[str, Any]) -> bool:
    """Import configuration from backup."""
    try:
        if 'config_data' in config_export:
            self.config_data = config_export['config_data'].copy()
            self._operation_count += 1
            return True
        return False
    except Exception as e:
        logger.error(f'Failed to import configuration: {e}')
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

