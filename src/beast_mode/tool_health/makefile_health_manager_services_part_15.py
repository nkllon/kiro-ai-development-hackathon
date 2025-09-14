from src.rm_ddd.core.health import ModuleHealth

    def _generic_systematic_repair(self, diagnosis: MakefileDiagnosisResult) -> str:
        """Generic systematic repair for unknown issues"""
        return f'Systematic analysis and repair of: {diagnosis.root_cause}'

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

