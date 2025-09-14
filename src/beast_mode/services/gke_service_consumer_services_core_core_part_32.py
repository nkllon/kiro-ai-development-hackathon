
def _estimate_implementation_effort(self, component_spec: Dict[str, Any], gcp_requirements: Dict[str, Any]) -> float:
    """Estimate implementation effort in hours"""
    base_effort = 2.0
    complexity_factor = len(gcp_requirements.get('services', [])) * 0.5
    component_complexity = len(component_spec.get('features', [])) * 0.3
    return base_effort + complexity_factor + component_complexity
