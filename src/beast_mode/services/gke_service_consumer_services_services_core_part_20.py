from src.rm_ddd.core.health import ModuleHealth

def _generate_prevention_recommendations(self, health_assessment: Dict[str, Any]) -> List[str]:
    """Generate prevention recommendations from health assessment"""
    recommendations = ['Implement systematic tool validation in CI/CD pipeline', 'Regular health checks to prevent tool degradation']
    if health_assessment.get('makefile_issues', 0) > 0:
        recommendations.append('Consider Makefile best practices training')
    return recommendations

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

