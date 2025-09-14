from src.rm_ddd.core.health import ModuleHealth

    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for external systems (GKE)"""
        return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'diagnoses_performed': self.diagnosis_count, 'repairs_completed': self.repair_count, 'workarounds_rejected': self.workarounds_rejected, 'repair_principles': self.repair_principles, 'expected_modules': len(self.expected_makefile_modules), 'degradation_active': self._degradation_active}

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

