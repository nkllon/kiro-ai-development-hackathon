from src.rm_ddd.core.health import ModuleHealth

def _analyze_systematic_adoption_trends(self) -> Dict[str, Any]:
    """Analyze systematic approach adoption trends"""
    if not self.gke_team_metrics:
        return {'status': 'insufficient_data'}
    adoption_scores = [metrics.systematic_adoption_score for metrics in self.gke_team_metrics.values()]
    return {'average_adoption_score': sum(adoption_scores) / len(adoption_scores), 'high_adoption_teams': sum((1 for score in adoption_scores if score >= 0.8)), 'medium_adoption_teams': sum((1 for score in adoption_scores if 0.5 <= score < 0.8)), 'low_adoption_teams': sum((1 for score in adoption_scores if score < 0.5)), 'adoption_trend': 'increasing' if len(adoption_scores) > 0 else 'stable'}
