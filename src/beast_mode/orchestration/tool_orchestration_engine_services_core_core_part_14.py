from src.rm_ddd.core.health import ModuleHealth

def _update_orchestration_metrics(self, result: OrchestrationResult):
    """
        Update orchestration metrics with result data
        """
    self.orchestration_metrics['total_orchestrations'] += 1
    if result.success:
        self.orchestration_metrics['successful_orchestrations'] += 1
    else:
        self.orchestration_metrics['failed_orchestrations'] += 1
    confidence_key = result.decision_confidence.value
    self.orchestration_metrics['decision_confidence_distribution'][confidence_key] += 1
    current_avg = self.orchestration_metrics['average_execution_time_ms']
    total_ops = self.orchestration_metrics['total_orchestrations']
    new_avg = (current_avg * (total_ops - 1) + result.total_execution_time_ms) / total_ops
    self.orchestration_metrics['average_execution_time_ms'] = new_avg
    if result.fallback_results:
        self.orchestration_metrics['fallbacks_used'] += len(result.fallback_results)

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

