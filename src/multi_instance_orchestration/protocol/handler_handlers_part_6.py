from src.rm_ddd.core.health import ModuleHealth

class InitClass:
    """Auto-generated class for functions."""

    def __init__(self, instance_id: str):
    super().__init__('TextProtocolHandler', '1.0.0')
    self.instance_id = instance_id
    self.command_patterns: dict[str, CommandPattern] = {}
    self.action_handlers: dict[str, Callable[[StructuredAction], ActionResult]] = {}
    self.command_history: list[StructuredAction] = []
    self.execution_stats = {'total_commands': 0, 'successful_commands': 0, 'failed_commands': 0, 'average_execution_time': 0.0}
    self._register_default_patterns()

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

