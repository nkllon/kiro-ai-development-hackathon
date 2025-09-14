from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def _calculate_coverage_score(self, coverage: Dict[str, Any]) -> float:
    """Calculate feature coverage score."""
    return coverage.get('coverage_percentage', 0.0)
