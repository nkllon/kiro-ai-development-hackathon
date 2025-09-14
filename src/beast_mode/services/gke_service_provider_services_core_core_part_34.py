from src.rm_ddd.core.health import ModuleHealth

def _estimate_resource_requirements(self, component_type: str, requirements: List[str]) -> Dict[str, Any]:
    """Estimate GCP resource requirements"""
    base_requirements = {'cpu': '2 vCPUs', 'memory': '4 GB', 'storage': '20 GB', 'network': 'Standard'}
    if 'high_performance' in requirements:
        base_requirements['cpu'] = '4 vCPUs'
        base_requirements['memory'] = '8 GB'
    if 'large_data' in requirements:
        base_requirements['storage'] = '100 GB'
    return base_requirements
