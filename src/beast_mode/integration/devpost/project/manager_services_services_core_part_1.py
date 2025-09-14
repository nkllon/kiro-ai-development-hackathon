from src.rm_ddd.core.health import ModuleHealth

class InitClass:
    """Auto-generated class for functions."""

    def __init__(self, project_root: Optional[Path]=None):
    """Initialize project manager.

    Args:
    project_root: Root directory of the project. If None, uses current directory.
    """
    self.project_root = project_root or Path.cwd()
    self.config_manager = DevpostConfigManager(self.project_root)
    self._current_connection: Optional[ProjectConnection] = None
    self._active_project_id: Optional[str] = None
    self._load_current_connection()

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

