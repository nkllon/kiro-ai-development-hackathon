from src.rm_ddd.core.registry import register_module

def _calculate_coverage_score(self, coverage: Dict[str, Any]) -> float:
    """Calculate feature coverage score."""
    return coverage.get('coverage_percentage', 0.0)
