from src.rm_ddd.core.health import ModuleHealth

def _analyze_infrastructure_details(self, failure: Failure) -> Dict[str, Any]:
    """Analyze infrastructure failure details"""
    return {'error_type': self._get_infrastructure_subcategory(failure), 'system_related': 'system' in failure.error_message.lower(), 'permission_related': 'permission' in failure.error_message.lower(), 'network_related': 'connection' in failure.error_message.lower()}

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

