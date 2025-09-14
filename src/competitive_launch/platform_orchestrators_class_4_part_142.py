from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def _calculate_acceleration_factor(self, resources: KiroResources) -> float:
    """Calculate development acceleration factor."""
    return 3.5
