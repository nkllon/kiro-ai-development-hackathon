
def _calculate_team_quality_trend(self, team_id: str) -> str:
    """Calculate quality trend for team"""
    team_metrics = self.team_performance_metrics.get(team_id, {})
    usage_count = team_metrics.get('service_usage_count', 0)
    if usage_count > 10:
        return 'improving'
    elif usage_count > 5:
        return 'stable'
    else:
        return 'establishing_baseline'
