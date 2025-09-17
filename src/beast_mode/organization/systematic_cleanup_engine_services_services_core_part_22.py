from src.rm_ddd.core.health import ModuleHealth

def _calculate_entropy_reduction(self, cleanup_actions: List[Dict[str, Any]]) -> float:
    """Calculate expected entropy reduction from cleanup actions"""
    high_impact_actions = len([a for a in cleanup_actions if a.get('priority') in ['CRITICAL', 'HIGH']])
    total_actions = len(cleanup_actions)
    return min(0.9, high_impact_actions / total_actions * 0.8) if total_actions > 0 else 0.0

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

