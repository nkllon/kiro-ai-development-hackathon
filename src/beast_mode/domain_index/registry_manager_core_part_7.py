from src.rm_ddd.core.health import ModuleHealth

def _apply_filters(self, domain: Domain, filters: Dict[str, Any]) -> bool:
    """Apply filters to a domain"""
    for filter_key, filter_value in filters.items():
        if filter_key == 'category':
            if domain.metadata.demo_role != filter_value:
                return False
        elif filter_key == 'status':
            if domain.metadata.status != filter_value:
                return False
        elif filter_key == 'has_pattern':
            if not any((filter_value in pattern for pattern in domain.patterns)):
                return False
    return True

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

