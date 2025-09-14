from src.rm_ddd.core.health import ModuleHealth

def _analyze_resource_availability(self, failure: Failure) -> Dict[str, Any]:
    """Analyze resource availability"""
    resource_analysis = {}
    if 'MemoryError' in failure.error_message or 'resource' in failure.error_message.lower():
        resource_analysis['has_resource_issue'] = True
        resource_analysis['resource_details'] = failure.error_message
    else:
        resource_analysis['has_resource_issue'] = False
    return resource_analysis

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

