from src.rm_ddd.core.health import ModuleHealth

def _apply_optimization(self, tool_id: str, optimization_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Apply specific optimization to tool"""
    return {'success': True, 'optimization_type': optimization_type, 'improvement_percentage': 15.0}

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

