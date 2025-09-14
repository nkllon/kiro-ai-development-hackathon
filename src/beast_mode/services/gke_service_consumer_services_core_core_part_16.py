from src.rm_ddd.core.health import ModuleHealth

def _generate_pdca_recommendations(self, team_id: str, pdca_result: Dict[str, Any]) -> List[str]:
    """Generate PDCA-specific recommendations for team"""
    team_profile = self.registered_teams.get(team_id)
    recommendations = []
    if team_profile and team_profile.expertise_level == 'beginner':
        recommendations.append('Consider systematic approach training for better PDCA adoption')
    if pdca_result.get('execution_time_minutes', 0) > 90:
        recommendations.append('Break down complex tasks into smaller PDCA cycles')
    recommendations.append('Track systematic vs ad-hoc approach performance for continuous improvement')
    return recommendations
