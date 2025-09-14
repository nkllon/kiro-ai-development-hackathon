from src.rm_ddd.core.health import ModuleHealth

def _estimate_development_time(self, component_design: Dict[str, Any]) -> Dict[str, int]:
    """Estimate development time for component"""
    base_hours = 20
    architecture = component_design.get('architecture', {})
    gcp_services = len(architecture.get('gcp_services', []))
    complexity_multiplier = 1.0 + gcp_services * 0.2
    estimated_hours = int(base_hours * complexity_multiplier)
    return {'total_hours': estimated_hours, 'systematic_approach_time_savings': int(estimated_hours * 0.25), 'breakdown': {'design': int(estimated_hours * 0.2), 'implementation': int(estimated_hours * 0.5), 'testing': int(estimated_hours * 0.2), 'documentation': int(estimated_hours * 0.1)}}

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

