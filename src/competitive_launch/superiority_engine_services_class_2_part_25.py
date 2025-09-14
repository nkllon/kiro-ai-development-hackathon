from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class CalculatecompetitiveadvantagelevelClass:
    """Auto-generated class for functions."""

    def _calculate_competitive_advantage_level(self) -> str:
    """Calculate overall competitive advantage level."""
    if not self.metrics:
    return 'Unknown'
    avg_improvement = sum((m.improvement_percentage for m in self.metrics)) / len(self.metrics)
    if avg_improvement > 50:
    return 'Exceptional'
    elif avg_improvement > 30:
    return 'Significant'
    elif avg_improvement > 15:
    return 'Moderate'
    else:
    return 'Minimal'

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

