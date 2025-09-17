from src.rm_ddd.core.health import ModuleHealth

def _get_performance_metrics(self) -> Dict[str, Any]:
    """Get detailed performance metrics"""
    total_executions = self.orchestration_metrics['total_executions']
    successful_executions = self.orchestration_metrics['successful_executions']
    return {'total_executions': total_executions, 'successful_executions': successful_executions, 'success_rate': successful_executions / total_executions if total_executions > 0 else 1.0, 'average_decision_time': self.orchestration_metrics['average_decision_time_ms'], 'active_executions': len(self.active_executions), 'tools_with_metrics': len(self.tool_metrics)}

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

