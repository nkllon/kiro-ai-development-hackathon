
def get_decision_analytics(self) -> Dict[str, Any]:
    """
        Get analytics about decision making patterns
        """
    if not self.decision_history:
        return {'message': 'No decision history available'}
    total_decisions = len(self.decision_history)
    confidence_distribution = self.orchestration_metrics['decision_confidence_distribution']
    success_by_confidence = {'high': 0, 'medium': 0, 'low': 0}
    confidence_counts = {'high': 0, 'medium': 0, 'low': 0}
    for decision in self.decision_history:
        confidence = decision['confidence_level']
        confidence_counts[confidence] += 1
        if decision['success']:
            success_by_confidence[confidence] += 1
    success_rates = {}
    for level in ['high', 'medium', 'low']:
        if confidence_counts[level] > 0:
            success_rates[level] = success_by_confidence[level] / confidence_counts[level]
        else:
            success_rates[level] = 0.0
    return {'total_decisions': total_decisions, 'confidence_distribution': confidence_distribution, 'success_rates_by_confidence': success_rates, 'average_execution_time_ms': self.orchestration_metrics['average_execution_time_ms'], 'tools_repaired': self.orchestration_metrics['tools_repaired'], 'fallbacks_used': self.orchestration_metrics['fallbacks_used'], 'overall_success_rate': self._calculate_success_rate()}
