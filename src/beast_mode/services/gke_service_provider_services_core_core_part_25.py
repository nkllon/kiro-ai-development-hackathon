from src.rm_ddd.core.health import ModuleHealth

def _generate_prevention_recommendations(self, health_assessment: Dict[str, Any]) -> List[str]:
    """Generate prevention recommendations from health assessment"""
    recommendations = ['Implement regular health monitoring', 'Set up automated tool validation', 'Create systematic maintenance procedures', 'Document tool configuration standards']
    if health_assessment.get('makefile_issues', 0) > 0:
        recommendations.append('Standardize Makefile patterns across projects')
    if health_assessment.get('dependency_issues', 0) > 0:
        recommendations.append('Implement dependency version management')
    if health_assessment.get('configuration_issues', 0) > 0:
        recommendations.append('Create configuration validation checks')
    return recommendations
