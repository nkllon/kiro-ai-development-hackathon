from src.rm_ddd.core.health import ModuleHealth

class SetexpirationClass:
    """Auto-generated class for functions."""

    def set_expiration(self, expires_at: datetime) -> bool:
    """Set preview expiration time"""
    try:
    self._update_metrics('set_expiration')
    self.preview_data['expires_at'] = expires_at.isoformat()
    self.updated_at = datetime.now()
    self._logger.info(f'Expiration set for preview {self.preview_id}: {expires_at}')
    return True
    except Exception as e:
    self._logger.error(f'Failed to set expiration: {e}')
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

