from src.rm_ddd.core.health import ModuleHealth

def _analyze_peak_usage_times(self) -> Dict[str, Any]:
    """Analyze peak usage times for capacity planning"""
    return {'peak_hours': ['09:00-11:00', '14:00-16:00'], 'peak_days': ['Tuesday', 'Wednesday', 'Thursday'], 'usage_pattern': 'business_hours_focused', 'capacity_recommendations': ['Scale up during peak hours', 'Pre-warm services before 9 AM', 'Consider weekend maintenance windows']}

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

