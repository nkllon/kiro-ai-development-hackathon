from src.rm_ddd.core.health import ModuleHealth

class GetdecisionanalyticsClass:
    """Auto-generated class for functions."""

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

