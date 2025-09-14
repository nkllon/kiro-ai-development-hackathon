from src.rm_ddd.core.health import ModuleHealth

def increment_access_count(self) -> bool:
    """Increment preview access count"""
    try:
        self._update_metrics('increment_access_count')
        self.preview_data['access_count'] = self.preview_data.get('access_count', 0) + 1
        self.updated_at = datetime.now()
        self._logger.info(f"Access count incremented for preview {self.preview_id}: {self.preview_data['access_count']}")
        return True
    except Exception as e:
        self._logger.error(f'Failed to increment access count: {e}')
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

