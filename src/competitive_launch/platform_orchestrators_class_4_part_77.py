from src.rm_ddd.core.registry import register_module

def _generate_cost_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
    """Generate cost optimization recommendations."""
    return ['Consider right-sizing instances based on actual usage', 'Implement spot instances for non-critical workloads', 'Optimize scheduling for cost-effective resource utilization']
