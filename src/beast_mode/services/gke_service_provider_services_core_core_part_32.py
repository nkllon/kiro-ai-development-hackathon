from src.rm_ddd.core.health import ModuleHealth

def _determine_deployment_strategy(self, gcp_constraints: List[str]) -> str:
    """Determine optimal deployment strategy"""
    if 'high_availability' in gcp_constraints:
        return 'multi_region'
    elif 'cost_optimization' in gcp_constraints:
        return 'single_region'
    else:
        return 'regional'
