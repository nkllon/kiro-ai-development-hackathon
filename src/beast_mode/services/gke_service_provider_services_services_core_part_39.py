from src.rm_ddd.core.health import ModuleHealth

def _identify_improvement_areas(self, quality_assessment: Dict[str, Any]) -> List[str]:
    """Identify areas needing improvement"""
    areas = []
    if quality_assessment.get('maintainability_index', 0) < 75:
        areas.append('Code maintainability')
    if quality_assessment.get('security_score', 0) < 90:
        areas.append('Security practices')
    if quality_assessment.get('performance_score', 0) < 80:
        areas.append('Performance optimization')
    if quality_assessment.get('gke_compliance_score', 0) < 85:
        areas.append('GKE compliance')
    return areas

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

