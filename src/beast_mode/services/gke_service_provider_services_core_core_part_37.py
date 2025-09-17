from src.rm_ddd.core.health import ModuleHealth

def _generate_maintenance_schedule(self) -> Dict[str, str]:
    """Generate recommended maintenance schedule"""
    return {'daily': 'Automated health checks', 'weekly': 'Tool validation and updates', 'monthly': 'Comprehensive system review', 'quarterly': 'Systematic approach optimization'}

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

