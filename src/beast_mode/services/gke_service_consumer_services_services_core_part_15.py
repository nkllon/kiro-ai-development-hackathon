from src.rm_ddd.core.health import ModuleHealth

def _generate_next_recommendations(self, pdca_result: Dict[str, Any]) -> List[str]:
    """Generate next step recommendations based on PDCA result"""
    recommendations = []
    if pdca_result.get('success', False):
        recommendations.append('Consider applying systematic approach to similar tasks')
        recommendations.append('Document patterns learned for team knowledge sharing')
    else:
        recommendations.append('Review systematic constraints and retry with refined approach')
        recommendations.append('Consider tool health check if implementation issues occurred')
    return recommendations
