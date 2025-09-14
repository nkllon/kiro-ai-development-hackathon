from src.rm_ddd.core.health import ModuleHealth

def _generate_strategic_recommendations(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate strategic recommendations based on opportunities."""
    recommendations = []
    for opp in opportunities:
        if opp['implementation_priority'] == 'high':
            rec = {'action': f"Accelerate development of {opp['name']}", 'rationale': f'High market alignment and impact', 'timeline': 'immediate', 'expected_advantage': opp['competitive_advantage']}
            recommendations.append(rec)
    return recommendations
