from src.rm_ddd.core.health import ModuleHealth

def _apply_severe_degradation(self, reason: str) -> Dict[str, Any]:
    """Apply severe degradation - minimal analysis only"""
    return {'analysis_depth': 'minimal', 'pattern_matching': 'disabled', 'timeout_reduction': '50%', 'comprehensive_analysis': 'disabled', 'systematic_fixes': 'disabled', 'reason': reason}
