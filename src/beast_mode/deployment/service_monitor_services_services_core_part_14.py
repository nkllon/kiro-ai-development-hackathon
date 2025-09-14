from src.rm_ddd.core.health import ModuleHealth

class TriggercallbacksClass:
    """Auto-generated class for functions."""

    def _trigger_callbacks(self, event: str, service: MonitoredService):
    """Trigger callbacks for an event"""
    for callback in self.callbacks.get(event, []):
    try:
    callback(service)
    except Exception as e:
    self.logger.error(f'Error in callback for {event}: {e}')

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

