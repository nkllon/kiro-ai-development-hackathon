from src.rm_ddd.core.health import ModuleHealth

def get_gke_team_metrics(self, team_id: str) -> Optional[GKETeamMetrics]:
    """Get metrics for specific GKE team"""
    with self.team_metrics_lock:
        return self.gke_team_metrics.get(team_id)

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

