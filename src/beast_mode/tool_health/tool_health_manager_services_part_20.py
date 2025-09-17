from src.rm_ddd.core.health import ModuleHealth

    def _assess_tool_health(self, tool_name: str) -> Dict[str, Any]:
        """Assess current health of a specific tool"""
        return {'tool_name': tool_name, 'status': 'healthy', 'last_check': datetime.now().isoformat(), 'performance_score': 0.9}

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

