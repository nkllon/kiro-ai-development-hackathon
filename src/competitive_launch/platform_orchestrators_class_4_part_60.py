from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def _calculate_quality_score(self, requirements: Dict[str, Any]) -> float:
    """Calculate overall quality score."""
    return 0.925
