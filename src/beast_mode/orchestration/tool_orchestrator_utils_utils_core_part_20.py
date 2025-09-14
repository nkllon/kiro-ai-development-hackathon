from src.rm_ddd.core.health import ModuleHealth

def _calculate_average_execution_time(self) -> float:
    """Calculate average execution time across all tools"""
    if not self.tool_metrics:
        return 0.0
    total_time = sum((metrics.average_execution_time_ms for metrics in self.tool_metrics.values()))
    return total_time / len(self.tool_metrics)

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

