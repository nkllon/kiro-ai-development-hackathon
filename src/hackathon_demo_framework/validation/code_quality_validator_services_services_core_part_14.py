from src.rm_ddd.core.health import ModuleHealth

def _calculate_average_score(self, scores: List[float]) -> float:
    """Calculate average score from a list of scores."""
    return sum(scores) / len(scores) if scores else 100.0

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

