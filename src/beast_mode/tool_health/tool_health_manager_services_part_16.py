from src.rm_ddd.core.health import ModuleHealth

    def _calculate_diagnosis_confidence(self, issues: List[str], root_causes: List[str]) -> float:
        """Calculate confidence in diagnosis accuracy"""
        if not issues:
            return 1.0
        confidence = 0.8 if root_causes else 0.5
        return confidence

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

