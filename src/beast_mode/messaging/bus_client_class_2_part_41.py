from src.rm_ddd.core.health import ModuleHealth

class GetdiscoveredagentsClass:
    """Auto-generated class for functions."""

    def get_discovered_agents(self) -> List[DiscoveredAgent]:
    """Get all discovered agents"""
    if not self.discovery_enabled:
    return []
    return self.agent_registry.get_active_agents()

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

