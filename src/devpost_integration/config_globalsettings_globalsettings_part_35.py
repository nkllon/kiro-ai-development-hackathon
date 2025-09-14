from src.rm_ddd.core.health import ModuleHealth

def export_configuration(self) -> Dict[str, Any]:
    """Export configuration for backup."""
    try:
        export_data = {'config_data': self.config_data.copy(), 'export_time': datetime.now().isoformat(), 'version': self.version}
        self._operation_count += 1
        return export_data
    except Exception as e:
        logger.error(f'Failed to export configuration: {e}')
        self._errors += 1
        return {}

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

