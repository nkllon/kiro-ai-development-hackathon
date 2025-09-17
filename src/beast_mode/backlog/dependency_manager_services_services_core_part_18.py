from src.rm_ddd.core.health import ModuleHealth

def _generate_cycle_resolution_suggestions(self, cycles: List[List[str]]) -> List[str]:
    """Generate suggestions for resolving circular dependencies"""
    suggestions = []
    for i, cycle in enumerate(cycles):
        suggestions.append(f"Cycle {i + 1}: {' -> '.join(cycle)}")
        suggestions.append(f'  - Consider removing dependency between {cycle[-2]} and {cycle[-1]}')
        suggestions.append(f'  - Or restructure to eliminate circular relationship')
    if not cycles:
        suggestions.append('No circular dependencies detected')
    return suggestions

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

