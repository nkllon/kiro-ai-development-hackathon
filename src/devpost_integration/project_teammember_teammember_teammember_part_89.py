from src.rm_ddd.core.health import ModuleHealth

def _calculate_health_score(self) -> float:
    """Calculate health score."""
    score = 1.0
    if self._errors > 0:
        score -= min(0.5, self._errors * 0.1)
    if not self.project_id:
        score -= 0.3
    if not self.title:
        score -= 0.2
    if not self.description:
        score -= 0.2
    return max(0.0, score)

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

