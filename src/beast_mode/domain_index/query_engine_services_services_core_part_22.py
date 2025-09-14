from src.rm_ddd.core.health import ModuleHealth

def _get_popular_query_templates(self) -> List[str]:
    """Get popular query templates for empty queries"""
    templates = ['find domains with testing capabilities', 'show all core domains', 'domains that depend on core_domain', 'domains with *.py patterns', 'analyze domain relationships', 'healthy domains', 'domains suitable for extraction', 'domains with high complexity', 'similar domains to test_domain', 'domains in infrastructure category']
    return templates[:self.suggestion_limit]

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

