from src.rm_ddd.core.health import ModuleHealth

def _generate_strategic_recommendations(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate strategic recommendations based on opportunities."""
    recommendations = []
    for opp in opportunities:
        if opp['implementation_priority'] == 'high':
            rec = {'action': f"Accelerate development of {opp['name']}", 'rationale': f'High market alignment and impact', 'timeline': 'immediate', 'expected_advantage': opp['competitive_advantage']}
            recommendations.append(rec)
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

