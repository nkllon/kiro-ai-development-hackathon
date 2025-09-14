from src.rm_ddd.core.health import ModuleHealth

class LoadcurrentconnectionClass:
    """Auto-generated class for functions."""

    def _load_current_connection(self) -> None:
    """Load current project connection if it exists."""
    try:
    self._current_connection = self.config_manager.load_connection(self.project_root)
    except Exception:
    self._current_connection = None

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

