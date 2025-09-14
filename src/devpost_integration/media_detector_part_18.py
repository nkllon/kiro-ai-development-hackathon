from src.rm_ddd.core.health import ModuleHealth

class GetmetricsClass:
    """Auto-generated class for functions."""

    def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    uptime = (datetime.now() - self._start_time).total_seconds()
    stats = self.get_media_statistics()

    return {
    'uptime_seconds': uptime,
    'uptime_hours': uptime / 3600,
    'files_processed': stats['files_processed'],
    'files_detected': stats['files_detected'],
    'detection_rate': stats['detection_rate'],
    'errors': stats['errors'],
    'error_rate': stats['error_rate'],
    'supported_formats': stats['supported_formats'],
    'last_check': datetime.now().isoformat()
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

