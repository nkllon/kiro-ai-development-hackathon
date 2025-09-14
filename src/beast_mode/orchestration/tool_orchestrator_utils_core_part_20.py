from src.rm_ddd.core.health import ModuleHealth

def _calculate_average_execution_time(self) -> float:
    """Calculate average execution time across all tools"""
    if not self.tool_metrics:
        return 0.0
    total_time = sum((metrics.average_execution_time_ms for metrics in self.tool_metrics.values()))
    return total_time / len(self.tool_metrics)
