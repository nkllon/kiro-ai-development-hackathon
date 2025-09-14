
def get_module_status(self) -> Dict[str, Any]:
    """Tool orchestrator operational status"""
    return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'registered_tools': len(self.registered_tools), 'active_executions': len(self.active_executions), 'total_executions': self.orchestration_metrics['total_executions'], 'success_rate': self._calculate_success_rate(), 'systematic_compliance_rate': self.orchestration_metrics['systematic_compliance_rate']}
