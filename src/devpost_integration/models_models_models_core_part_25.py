from src.rm_ddd.core.health import ModuleHealth

def update_configuration(self, config: Dict[str, Any]) -> bool:
    """Update module configuration"""
    try:
        self._update_metrics('update_configuration')
        if 'content_type' in config:
            self.preview_data['content_type'] = config['content_type']
        if 'status' in config:
            self.preview_data['status'] = config['status']
        self.updated_at = datetime.now()
        self._logger.info(f'Preview data {self.preview_id} configuration updated')
        return True
    except Exception as e:
        self._logger.error(f'Configuration update failed: {e}')
        self._metrics['error_count'] += 1
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

