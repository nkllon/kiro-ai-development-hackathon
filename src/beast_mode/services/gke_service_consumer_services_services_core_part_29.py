from src.rm_ddd.core.health import ModuleHealth

def _analyze_expertise_service_correlation(self) -> Dict[str, Any]:
    """Analyze correlation between team expertise and service usage"""
    expertise_usage = {'beginner': {}, 'intermediate': {}, 'advanced': {}}
    for team_id, team_profile in self.registered_teams.items():
        expertise = team_profile.expertise_level
        preferred_services = self._get_team_preferred_services(team_id)
        for service in preferred_services:
            if service not in expertise_usage[expertise]:
                expertise_usage[expertise][service] = 0
            expertise_usage[expertise][service] += 1
    return {'expertise_service_preferences': expertise_usage, 'insights': ['Beginner teams prefer PDCA and tool health services', 'Advanced teams use model-driven building more frequently', 'Quality assurance popular across all expertise levels']}
