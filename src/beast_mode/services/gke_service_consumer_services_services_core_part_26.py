from src.rm_ddd.core.health import ModuleHealth

class GetteampreferredservicesClass:
    """Auto-generated class for functions."""

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

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

