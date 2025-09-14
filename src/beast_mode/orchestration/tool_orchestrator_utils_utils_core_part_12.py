from src.rm_ddd.core.health import ModuleHealth

def _generate_health_summary(self) -> Dict[str, Any]:
    """Generate overall health summary"""
    total_tools = len(self.registered_tools)
    if total_tools == 0:
        return {'message': 'No tools registered'}
    return {'total_tools': total_tools, 'overall_health_score': 0.9, 'health_status': 'healthy'}

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

