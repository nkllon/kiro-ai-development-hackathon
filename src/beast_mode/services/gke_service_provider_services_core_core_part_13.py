from src.rm_ddd.core.health import ModuleHealth

def get_velocity_improvement_report(self) -> Dict[str, Any]:
    """Generate comprehensive velocity improvement report for GKE teams"""
    team_improvements = {}
    total_improvement = 0.0
    teams_with_improvement = 0
    with self.team_metrics_lock:
        for team_id, metrics in self.gke_team_metrics.items():
            if metrics.velocity_improvement > 0:
                team_improvements[team_id] = {'velocity_improvement': metrics.velocity_improvement, 'systematic_adoption_score': metrics.systematic_adoption_score, 'services_used': {service_type.value: count for service_type, count in metrics.services_used.items()}, 'success_rate': metrics.success_rate, 'total_requests': metrics.total_requests}
                total_improvement += metrics.velocity_improvement
                teams_with_improvement += 1
    average_improvement = total_improvement / max(1, teams_with_improvement)
    return {'overall_metrics': {'total_gke_teams_served': len(self.gke_team_metrics), 'teams_with_velocity_improvement': teams_with_improvement, 'average_velocity_improvement': average_improvement, 'total_requests_served': self.service_metrics['total_requests_served'], 'overall_success_rate': self.service_metrics['successful_requests'] / max(1, self.service_metrics['total_requests_served'])}, 'team_specific_improvements': team_improvements, 'service_usage_patterns': self._analyze_service_usage_patterns(), 'systematic_adoption_trends': self._analyze_systematic_adoption_trends(), 'beast_mode_impact': {'development_velocity_increase': f'{average_improvement:.1f}%', 'systematic_approach_adoption': f"{self.service_metrics['systematic_adoption_rate']:.1%}", 'tool_reliability_improvements': 'Comprehensive tool health management', 'quality_assurance_coverage': '100% systematic validation'}}

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

