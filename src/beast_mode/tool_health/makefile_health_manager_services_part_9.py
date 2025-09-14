
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for operational visibility"""
        return {'diagnostic_capability': {'status': 'healthy' if not self._degradation_active else 'degraded', 'diagnoses_completed': self.diagnosis_count, 'repair_success_rate': self.repair_count / max(1, self.diagnosis_count)}, 'systematic_compliance': {'status': 'healthy', 'workarounds_rejected': self.workarounds_rejected, 'root_cause_focus': self.repair_principles['root_cause_only']}}
