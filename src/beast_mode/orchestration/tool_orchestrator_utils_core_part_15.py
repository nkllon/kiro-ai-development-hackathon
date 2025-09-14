from src.rm_ddd.core.health import ModuleHealth

def _analyze_performance_patterns(self) -> Dict[str, Any]:
    """Analyze performance patterns across all tools"""
    return {'execution_times': {tool_id: metrics.average_execution_time_ms for tool_id, metrics in self.tool_metrics.items()}, 'success_rates': {tool_id: metrics.success_rate for tool_id, metrics in self.tool_metrics.items()}}
