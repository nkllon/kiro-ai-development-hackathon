
def _get_team_preferred_services(self, team_id: str) -> List[str]:
    """Get team's most used services"""
    team_profile = self.registered_teams.get(team_id)
    if not team_profile or not team_profile.service_usage_history:
        return []
    service_counts = {}
    for usage in team_profile.service_usage_history:
        service = usage.get('service_type')
        service_counts[service] = service_counts.get(service, 0) + 1
    return sorted(service_counts.keys(), key=lambda x: service_counts[x], reverse=True)[:3]
