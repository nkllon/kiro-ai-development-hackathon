
def _get_performance_metrics(self) -> Dict[str, Any]:
    """Get detailed performance metrics"""
    total_executions = self.orchestration_metrics['total_executions']
    successful_executions = self.orchestration_metrics['successful_executions']
    return {'total_executions': total_executions, 'successful_executions': successful_executions, 'success_rate': successful_executions / total_executions if total_executions > 0 else 1.0, 'average_decision_time': self.orchestration_metrics['average_decision_time_ms'], 'active_executions': len(self.active_executions), 'tools_with_metrics': len(self.tool_metrics)}
