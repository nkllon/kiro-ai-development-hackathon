from src.rm_ddd.core.health import ModuleHealth

def _generate_performance_optimizations(self) -> List[str]:
    """Generate suggestions for optimizing tool performance"""
    optimizations = []
    for tool_id, metrics in self.tool_metrics.items():
        if hasattr(metrics, 'success_rate'):
            success_rate = metrics.success_rate
            avg_time = metrics.average_execution_time_ms
        else:
            success_rate = metrics.get('success_rate', 1.0)
            avg_time = metrics.get('average_execution_time_ms', 0)
        if success_rate < 0.9:
            optimizations.append(f'Improve reliability for {tool_id} (current: {success_rate:.1%})')
        if avg_time > 5000:
            optimizations.append(f'Optimize execution time for {tool_id} (current: {avg_time}ms)')
    if len(optimizations) == 0:
        optimizations.extend(['All tools performing within optimal parameters', 'Consider implementing performance caching', 'Monitor for performance regression patterns', 'Implement predictive performance optimization'])
    return optimizations[:5]
