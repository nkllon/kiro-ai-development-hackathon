from src.rm_ddd.core.health import ModuleHealth

def get_all_gke_team_metrics(self) -> Dict[str, GKETeamMetrics]:
    """Get metrics for all GKE teams"""
    with self.team_metrics_lock:
        return self.gke_team_metrics.copy()
