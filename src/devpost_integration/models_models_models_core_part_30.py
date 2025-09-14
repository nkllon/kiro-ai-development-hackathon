from src.rm_ddd.core.health import ModuleHealth

def set_preview_url(self, preview_url: str) -> bool:
    """Set preview URL"""
    try:
        self._update_metrics('set_preview_url')
        self.preview_data['preview_url'] = preview_url
        self.updated_at = datetime.now()
        self._logger.info(f'Preview URL set for {self.preview_id}: {preview_url}')
        return True
    except Exception as e:
        self._logger.error(f'Failed to set preview URL: {e}')
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

