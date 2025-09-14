from src.rm_ddd.core.health import ModuleHealth

def _apply_minimal_degradation(self, reason: str) -> Dict[str, Any]:
    """Apply minimal degradation - reduce analysis depth"""
    return {'analysis_depth': 'reduced', 'pattern_matching': 'fast_only', 'timeout_reduction': '10%', 'reason': reason}
