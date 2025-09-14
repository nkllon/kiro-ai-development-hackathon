from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class PrioritizebycompetitiveimpactClass:
    """Auto-generated class for functions."""

    def _prioritize_by_competitive_impact(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prioritize scope reduction opportunities by competitive impact."""
    return sorted(opportunities, key=lambda x: x['competitive_impact'])
