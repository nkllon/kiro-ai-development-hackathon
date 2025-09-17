from src.rm_ddd.core.health import ModuleHealth

def _update_decision_metrics(self, decision_time_ms: int):
    """Update decision framework metrics"""
    current_avg = self.orchestration_metrics['average_decision_time_ms']
    total_executions = self.orchestration_metrics['total_executions']
    if total_executions == 0:
        self.orchestration_metrics['average_decision_time_ms'] = decision_time_ms
    else:
        self.orchestration_metrics['average_decision_time_ms'] = (current_avg * total_executions + decision_time_ms) / (total_executions + 1)

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

