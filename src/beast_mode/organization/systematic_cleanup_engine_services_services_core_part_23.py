from src.rm_ddd.core.health import ModuleHealth

def _estimate_cleanup_time(self, cleanup_actions: List[Dict[str, Any]]) -> str:
    """Estimate time required for systematic cleanup"""
    action_count = len(cleanup_actions)
    if action_count > 20:
        return '2-3 hours'
    elif action_count > 10:
        return '1-2 hours'
    elif action_count > 5:
        return '30-60 minutes'
    else:
        return '15-30 minutes'

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

