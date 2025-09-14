
def _generate_prevention_recommendations(self, health_assessment: Dict[str, Any]) -> List[str]:
    """Generate prevention recommendations from health assessment"""
    recommendations = ['Implement systematic tool validation in CI/CD pipeline', 'Regular health checks to prevent tool degradation']
    if health_assessment.get('makefile_issues', 0) > 0:
        recommendations.append('Consider Makefile best practices training')
    return recommendations
