
def _apply_emergency_degradation(self, reason: str) -> Dict[str, Any]:
    """Apply emergency degradation - fallback mode only"""
    return {'analysis_depth': 'none', 'fallback_mode': 'enabled', 'all_advanced_features': 'disabled', 'basic_reporting_only': True, 'reason': reason}
