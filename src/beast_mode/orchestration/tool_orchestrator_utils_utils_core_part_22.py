from src.rm_ddd.core.health import ModuleHealth

def _analyze_criteria_effectiveness(self) -> Dict[str, Any]:
    """Analyze effectiveness of decision criteria"""
    return {'systematic_compliance_effectiveness': self.orchestration_metrics['systematic_compliance_rate'], 'overall_criteria_effectiveness': self._calculate_decision_accuracy()}
