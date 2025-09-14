
def _calculate_decision_accuracy(self) -> float:
    """Calculate decision framework accuracy"""
    success_rate = self._calculate_success_rate()
    compliance_rate = self.orchestration_metrics['systematic_compliance_rate']
    return success_rate * 0.6 + compliance_rate * 0.4
