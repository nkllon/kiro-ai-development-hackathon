from src.rm_ddd.core.health import ModuleHealth

def _generate_gke_insights(self, pdca_result: Dict[str, Any], request: ServiceRequest) -> Dict[str, Any]:
    """Generate GKE-specific insights from PDCA execution"""
    return {'gke_integration_opportunities': ['Integrate with GKE CI/CD pipelines', 'Leverage GKE monitoring and logging', 'Optimize for GKE resource constraints'], 'systematic_approach_benefits': ['Reduced deployment failures', 'Improved code quality', 'Faster problem resolution'], 'recommended_next_steps': ['Apply PDCA learnings to similar components', 'Document systematic approach for team adoption', 'Integrate with existing GKE workflows'], 'team_specific_recommendations': self._get_team_specific_recommendations(request.gke_team_id)}

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

