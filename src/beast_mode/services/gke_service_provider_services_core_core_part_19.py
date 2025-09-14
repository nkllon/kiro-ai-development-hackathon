from src.rm_ddd.core.health import ModuleHealth

def _calculate_pdca_velocity_improvement(self, pdca_result: Dict[str, Any]) -> float:
    """Calculate velocity improvement from PDCA execution"""
    base_improvement = 25.0
    if pdca_result.get('plan_phase_success', False):
        base_improvement += 10.0
    if pdca_result.get('do_phase_success', False):
        base_improvement += 15.0
    if pdca_result.get('check_phase_success', False):
        base_improvement += 10.0
    if pdca_result.get('act_phase_success', False):
        base_improvement += 5.0
    return min(base_improvement, 80.0)
