from src.rm_ddd.core.health import ModuleHealth

def _get_team_specific_recommendations(self, team_id: str) -> List[str]:
    """Get recommendations specific to GKE team"""
    return [f'Integrate systematic approach into {team_id} workflows', 'Establish regular PDCA cycle reviews', 'Implement team-specific quality gates', 'Create systematic documentation standards']
