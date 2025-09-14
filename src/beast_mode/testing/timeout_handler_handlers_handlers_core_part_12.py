from src.rm_ddd.core.health import ModuleHealth

class CleanupoperationtimeoutsClass:
    """Auto-generated class for functions."""

    def _cleanup_operation_timeouts(self, operation_id: str) -> None:
    """Clean up timeout handlers for completed operation"""
    try:
    if operation_id in self.active_timeouts:
    handlers = self.active_timeouts.pop(operation_id)
    for handler_type, timer in handlers.items():
    if timer.is_alive():
    timer.cancel()
    except Exception as e:
    self.logger.error(f'Failed to cleanup timeouts for operation {operation_id}: {e}')

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

