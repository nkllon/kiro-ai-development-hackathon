from src.rm_ddd.core.health import ModuleHealth

def get_health_indicators(self) -> Dict[str, Any]:
    """Get health indicators for the cleanup engine"""
    return {'cleanup_plans_created': len(self.cleanup_history), 'entropy_metrics_tracked': len(self.entropy_metrics), 'last_cleanup_timestamp': self.cleanup_history[-1].plan_id if self.cleanup_history else None, 'engine_status': 'active'}

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

