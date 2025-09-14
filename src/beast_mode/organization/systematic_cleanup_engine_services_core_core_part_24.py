from src.rm_ddd.core.health import ModuleHealth

def _assess_systematic_impact(self, entropy_reduction: float) -> str:
    """Assess systematic impact of cleanup plan"""
    if entropy_reduction > 0.8:
        return 'TRANSFORMATIONAL: Major systematic improvement expected'
    elif entropy_reduction > 0.6:
        return 'SIGNIFICANT: Substantial organizational improvement'
    elif entropy_reduction > 0.4:
        return 'MODERATE: Meaningful systematic enhancement'
    else:
        return 'INCREMENTAL: Gradual organizational improvement'
