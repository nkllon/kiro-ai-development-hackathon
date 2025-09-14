
def _recommend_services_for_team(self, team_profile: GKETeamProfile) -> List[str]:
    """Recommend services based on team profile"""
    recommendations = []
    if team_profile.expertise_level == 'beginner':
        recommendations.extend(['pdca_cycle', 'tool_health_management'])
    elif team_profile.expertise_level == 'intermediate':
        recommendations.extend(['model_driven_building', 'quality_assurance'])
    else:
        recommendations.extend(['pdca_cycle', 'model_driven_building', 'quality_assurance'])
    if 'gcp' in team_profile.project_domains:
        recommendations.append('model_driven_building')
    if 'testing' in team_profile.preferred_tools:
        recommendations.append('quality_assurance')
    return list(set(recommendations))
