from src.rm_ddd.core.health import ModuleHealth

def __init__(self):
    super().__init__('tool_orchestrator')
    self.registered_tools = {}
    self.tool_status = {}
    self.active_executions = {}
    self.decision_criteria = {'systematic_compliance': 0.4, 'performance': 0.3, 'reliability': 0.2, 'availability': 0.1}
    self.tool_metrics = {}
    self.orchestration_metrics = {'total_executions': 0, 'successful_executions': 0, 'failed_executions': 0, 'average_decision_time_ms': 0, 'systematic_compliance_rate': 0.0, 'tool_optimization_improvements': {}}
    self._initialize_default_tools()
    self._update_health_indicator('tool_orchestrator', HealthStatus.HEALTHY, 'ready', 'Tool orchestrator ready for intelligent tool management')
