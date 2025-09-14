from src.rm_ddd.core.health import ModuleHealth

def _generate_building_recommendations(self, team_id: str, build_result: Dict[str, Any]) -> List[str]:
    """Generate building-specific recommendations"""
    recommendations = ['Follow systematic model-driven approach for consistency', 'Validate GCP compliance before deployment']
    team_profile = self.registered_teams.get(team_id)
    if team_profile and team_profile.expertise_level == 'beginner':
        recommendations.append('Consider GCP best practices training')
    return recommendations
