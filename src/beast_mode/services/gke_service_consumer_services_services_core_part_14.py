
def _calculate_velocity_improvement(self, team_id: str) -> Dict[str, float]:
    """Calculate velocity improvement for team"""
    if team_id not in self.team_performance_metrics:
        return {'improvement_percentage': 0.0, 'baseline_velocity': 0.0, 'current_velocity': 0.0}
    metrics = self.team_performance_metrics[team_id]
    return {'improvement_percentage': metrics['improvement_percentage'], 'baseline_velocity': metrics['baseline_velocity'], 'current_velocity': metrics['current_velocity']}
