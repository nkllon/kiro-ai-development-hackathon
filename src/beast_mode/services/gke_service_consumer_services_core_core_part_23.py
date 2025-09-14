
def _generate_qa_recommendations(self, team_id: str, qa_results: Dict[str, Any]) -> List[str]:
    """Generate QA-specific recommendations"""
    recommendations = ['Maintain systematic approach to quality assurance', 'Integrate quality gates in development workflow']
    if qa_results.get('coverage_percentage', 1.0) < 0.9:
        recommendations.append('Increase test coverage to meet 90% threshold')
    team_profile = self.registered_teams.get(team_id)
    if team_profile and team_profile.expertise_level == 'beginner':
        recommendations.append('Consider systematic testing methodology training')
    return recommendations
