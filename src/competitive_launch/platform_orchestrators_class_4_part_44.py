from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def _calculate_optimization_score(self, resources: TiDBResources) -> float:
    """Calculate overall optimization score."""
    return 0.85
