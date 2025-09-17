from src.rm_ddd.core.health import ModuleHealth

def _analyze_reliability_trends(self) -> Dict[str, Any]:
    """Analyze tool reliability trends"""
    return {'overall_reliability_trend': 'stable', 'most_reliable_tools': list(self.tool_metrics.keys())}

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

