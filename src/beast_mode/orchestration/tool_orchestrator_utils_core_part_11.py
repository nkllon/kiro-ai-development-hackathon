
def _calculate_success_rate(self) -> float:
    """Calculate overall success rate"""
    total = self.orchestration_metrics['total_executions']
    if total == 0:
        return 1.0
    return self.orchestration_metrics['successful_executions'] / total
