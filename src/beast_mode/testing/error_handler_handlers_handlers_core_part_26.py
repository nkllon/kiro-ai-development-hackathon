from src.rm_ddd.core.health import ModuleHealth

class GetoverallcomponenthealthClass:
    """Auto-generated class for functions."""

    def _get_overall_component_health(self) -> float:
    """Calculate overall component health score"""
    if not self.component_health:
    return 1.0
    healthy_count = sum((1 for metrics in self.component_health.values() if metrics.is_healthy))
    return healthy_count / len(self.component_health)

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

