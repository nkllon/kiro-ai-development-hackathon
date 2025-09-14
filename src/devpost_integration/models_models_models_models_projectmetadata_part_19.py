from src.rm_ddd.core.health import ModuleHealth

    def update_metadata(self, updates: Dict[str, Any]) -> bool:
        """Update multiple metadata values"""
        try:
            self._update_metrics('update_metadata')
            self.metadata.update(updates)
            self.updated_at = datetime.now()
            self._metrics['metadata_updates'] += len(updates)
            self._logger.info(f'Metadata updated with {len(updates)} values')
            return True
        except Exception as e:
            self._logger.error(f'Failed to update metadata: {e}')
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

