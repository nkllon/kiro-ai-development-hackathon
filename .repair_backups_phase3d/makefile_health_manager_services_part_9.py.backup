from src.rm_ddd.core.health import ModuleHealth

    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for operational visibility"""
        return {'diagnostic_capability': {'status': 'healthy' if not self._degradation_active else 'degraded', 'diagnoses_completed': self.diagnosis_count, 'repair_success_rate': self.repair_count / max(1, self.diagnosis_count)}, 'systematic_compliance': {'status': 'healthy', 'workarounds_rejected': self.workarounds_rejected, 'root_cause_focus': self.repair_principles['root_cause_only']}}

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

