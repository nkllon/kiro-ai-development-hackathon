
def get_gke_development_velocity_metrics(self, team_id: Optional[str]=None) -> Dict[str, Any]:
    """
        Get GKE development velocity improvement metrics
        Measures and tracks velocity improvements from Beast Mode services
        """
    if team_id and team_id in self.team_performance_metrics:
        team_metrics = self.team_performance_metrics[team_id]
        team_profile = self.registered_teams[team_id]
        return {'team_id': team_id, 'team_name': team_profile.team_name, 'baseline_velocity': team_metrics['baseline_velocity'], 'current_velocity': team_metrics['current_velocity'], 'improvement_percentage': team_metrics['improvement_percentage'], 'service_usage_count': team_metrics['service_usage_count'], 'satisfaction_score': team_metrics['satisfaction_score'], 'expertise_level': team_profile.expertise_level, 'preferred_services': self._get_team_preferred_services(team_id), 'last_updated': team_metrics['last_updated'].isoformat()}
    else:
        total_teams = len(self.registered_teams)
        if total_teams == 0:
            return {'message': 'No teams registered yet'}
        aggregate_improvement = sum((metrics['improvement_percentage'] for metrics in self.team_performance_metrics.values())) / total_teams
        total_service_usage = sum((metrics['service_usage_count'] for metrics in self.team_performance_metrics.values()))
        average_satisfaction = sum((metrics['satisfaction_score'] for metrics in self.team_performance_metrics.values())) / total_teams
        return {'total_registered_teams': total_teams, 'aggregate_velocity_improvement': round(aggregate_improvement, 2), 'total_service_usage': total_service_usage, 'average_satisfaction_score': round(average_satisfaction, 2), 'service_success_rate': self._calculate_success_rate(), 'most_popular_service': self._get_most_popular_service(), 'average_response_time_ms': self.service_metrics['average_response_time_ms'], 'measurement_timestamp': datetime.now().isoformat()}
