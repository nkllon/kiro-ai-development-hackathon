
def _update_decision_metrics(self, decision_time_ms: int):
    """Update decision framework metrics"""
    current_avg = self.orchestration_metrics['average_decision_time_ms']
    total_executions = self.orchestration_metrics['total_executions']
    if total_executions == 0:
        self.orchestration_metrics['average_decision_time_ms'] = decision_time_ms
    else:
        self.orchestration_metrics['average_decision_time_ms'] = (current_avg * total_executions + decision_time_ms) / (total_executions + 1)
