from src.rm_ddd.core.health import ModuleHealth

def _calculate_performance_score(self) -> float:
    """Calculate overall performance score for all tools"""
    if not self.tool_metrics:
        return 0.8
    total_performance = 0.0
    for tool_id, metrics in self.tool_metrics.items():
        if hasattr(metrics, 'success_rate'):
            success_rate = metrics.success_rate
            avg_time = metrics.average_execution_time_ms
        else:
            success_rate = metrics.get('success_rate', 0.8)
            avg_time = metrics.get('average_execution_time_ms', 1000)
        time_score = max(0.1, 1.0 - avg_time / 10000)
        performance = success_rate * 0.7 + time_score * 0.3
        total_performance += performance
    return total_performance / len(self.tool_metrics) if self.tool_metrics else 0.8

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

