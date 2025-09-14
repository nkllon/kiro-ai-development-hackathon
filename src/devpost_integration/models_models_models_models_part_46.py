from src.rm_ddd.core.health import ModuleHealth

    def is_expired(self) -> bool:
        """Check if preview is expired"""
        try:
            self._update_metrics('is_expired')
            if not self.preview_data.get('expires_at'):
                return False
            expires_at = datetime.fromisoformat(self.preview_data['expires_at'])
            return datetime.now() > expires_at
        except Exception as e:
            self._logger.error(f'Failed to check expiration: {e}')
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

