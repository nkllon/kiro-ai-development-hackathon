from src.rm_ddd.core.health import ModuleHealth

def _update_orchestration_metrics(self, status: str, execution_time_ms: int, systematic_compliance: bool):
    """Update overall orchestration metrics"""
    self.orchestration_metrics['total_executions'] += 1
    if status == 'success':
        self.orchestration_metrics['successful_executions'] += 1
    else:
        self.orchestration_metrics['failed_executions'] += 1
    total_executions = self.orchestration_metrics['total_executions']
    current_compliance = self.orchestration_metrics['systematic_compliance_rate']
    new_compliance = 1.0 if systematic_compliance else 0.0
    self.orchestration_metrics['systematic_compliance_rate'] = (current_compliance * (total_executions - 1) + new_compliance) / total_executions
