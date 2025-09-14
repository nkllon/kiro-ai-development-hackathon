
def _apply_moderate_degradation(self, reason: str) -> Dict[str, Any]:
    """Apply moderate degradation - skip non-essential analysis"""
    return {'analysis_depth': 'basic', 'pattern_matching': 'disabled', 'timeout_reduction': '25%', 'comprehensive_analysis': 'disabled', 'reason': reason}
