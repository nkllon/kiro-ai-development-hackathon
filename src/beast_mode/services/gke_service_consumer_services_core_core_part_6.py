from src.rm_ddd.core.health import ModuleHealth

def register_gke_team(self, team_id: str, team_name: str, expertise_level: str, preferred_tools: List[str], project_domains: List[str]) -> Dict[str, Any]:
    """
        Register a GKE team for service consumption
        Implements GKE team onboarding and profiling
        """
    team_profile = GKETeamProfile(team_id=team_id, team_name=team_name, expertise_level=expertise_level, preferred_tools=preferred_tools, project_domains=project_domains)
    self.registered_teams[team_id] = team_profile
    self.team_performance_metrics[team_id] = {'baseline_velocity': 0.0, 'current_velocity': 0.0, 'improvement_percentage': 0.0, 'service_usage_count': 0, 'satisfaction_score': 0.0, 'last_updated': datetime.now()}
    self.logger.info(f'GKE team registered: {team_name} ({team_id}) - {expertise_level} level')
    return {'success': True, 'team_id': team_id, 'registration_time': datetime.now().isoformat(), 'available_services': [svc.value for svc in ServiceType], 'recommended_services': self._recommend_services_for_team(team_profile)}
