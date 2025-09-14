from src.rm_ddd.core.health import ModuleHealth

def update_configuration(self, config: Dict[str, Any]) -> bool:
    """Update module configuration."""
    try:
        if 'operation_type' in config:
            self.operation_type = config['operation_type']
        return True
    except Exception as e:
        logger.error(f'Failed to update configuration: {e}')
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

