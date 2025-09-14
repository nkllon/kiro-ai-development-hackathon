from src.rm_ddd.core.health import ModuleHealth

    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for external systems (GKE)"""
        return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'diagnoses_performed': self.diagnosis_count, 'repairs_completed': self.repair_count, 'workarounds_rejected': self.workarounds_rejected, 'repair_principles': self.repair_principles, 'expected_modules': len(self.expected_makefile_modules), 'degradation_active': self._degradation_active}
