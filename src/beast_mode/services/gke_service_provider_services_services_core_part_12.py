from src.rm_ddd.core.health import ModuleHealth

class GetallgketeammetricsClass:
    """Auto-generated class for functions."""

    def get_all_gke_team_metrics(self) -> Dict[str, GKETeamMetrics]:
    """Get metrics for all GKE teams"""
    with self.team_metrics_lock:
    return self.gke_team_metrics.copy()

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

