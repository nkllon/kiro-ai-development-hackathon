from src.rm_ddd.core.health import ModuleHealth

def get_gke_team_metrics(self, team_id: str) -> Optional[GKETeamMetrics]:
    """Get metrics for specific GKE team"""
    with self.team_metrics_lock:
        return self.gke_team_metrics.get(team_id)
