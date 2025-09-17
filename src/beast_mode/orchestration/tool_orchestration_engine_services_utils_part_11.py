from src.rm_ddd.core.health import ModuleHealth

def get_registered_tools(self) -> Dict[str, Dict[str, Any]]:
    """
        Get information about all registered tools
        """
    tools_info = {}
    for tool_id, tool_def in self.tools_registry.items():
        health_status = self.tool_health_cache.get(tool_id, ToolStatus.UNKNOWN)
        tools_info[tool_id] = {'name': tool_def.name, 'description': tool_def.description, 'priority': tool_def.priority.value, 'health_status': health_status.value, 'dependencies': tool_def.dependencies, 'fallback_tools': tool_def.fallback_tools}
    return tools_info

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

