from src.rm_ddd.core.health import ModuleHealth

def _identify_optimization_opportunities(self, performance_analysis: Dict[str, Any], optimization_context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify optimization opportunities"""
    opportunities = []
    execution_times = performance_analysis['execution_times']
    if execution_times:
        avg_time = sum(execution_times.values()) / len(execution_times)
        for tool_id, time_ms in execution_times.items():
            if time_ms > avg_time * 1.5:
                opportunities.append({'tool_id': tool_id, 'optimization_type': 'performance_tuning', 'parameters': {'target_reduction_ms': time_ms - avg_time}, 'systematic_safe': True})
    return opportunities
