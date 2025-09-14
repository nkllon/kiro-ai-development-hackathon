from src.rm_ddd.core.health import ModuleHealth

class GetmediastatisticsClass:
    """Auto-generated class for functions."""

    def get_media_statistics(self) -> Dict[str, Any]:
    """Get media detection statistics"""
    return {
    'files_processed': self._files_processed,
    'files_detected': self._files_detected,
    'detection_rate': (self._files_detected / self._files_processed) if self._files_processed > 0 else 0.0,
    'errors': self._errors,
    'error_rate': (self._errors / self._files_processed) if self._files_processed > 0 else 0.0,
    'supported_formats': len(self.format_registry.get_all_extensions())
    }


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

    # ReflectiveModule interface implementation