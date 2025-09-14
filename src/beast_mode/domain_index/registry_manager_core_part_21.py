from src.rm_ddd.core.health import ModuleHealth

class DetectcirculardependenciesClass:
    """Auto-generated class for functions."""

    def detect_circular_dependencies(self) -> List[List[str]]:
    """Detect circular dependencies between domains"""
    return self._validator.detect_circular_dependencies(self._domains)

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

