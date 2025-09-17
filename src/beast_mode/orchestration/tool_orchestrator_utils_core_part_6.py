from src.rm_ddd.core.health import ModuleHealth

def get_orchestration_analytics(self) -> Dict[str, Any]:
    """Get comprehensive orchestration analytics"""
    return {'execution_analytics': {'total_executions': self.orchestration_metrics['total_executions'], 'success_rate': self._calculate_success_rate(), 'average_execution_time': self._calculate_average_execution_time(), 'systematic_compliance_rate': self.orchestration_metrics['systematic_compliance_rate']}, 'decision_framework_effectiveness': {'average_decision_time': self.orchestration_metrics['average_decision_time_ms'], 'decision_accuracy': self._calculate_decision_accuracy(), 'criteria_effectiveness': self._analyze_criteria_effectiveness()}, 'tool_usage_patterns': {'most_used_tools': self._get_most_used_tools(), 'tool_performance_ranking': self._rank_tools_by_performance(), 'usage_trends': self._analyze_usage_trends()}, 'optimization_impact': {'performance_improvements': self.orchestration_metrics['tool_optimization_improvements'], 'systematic_constraint_adherence': self._calculate_constraint_adherence(), 'optimization_roi': self._calculate_optimization_roi()}, 'health_monitoring_insights': {'tool_reliability_trends': self._analyze_reliability_trends(), 'failure_pattern_analysis': self._analyze_failure_patterns(), 'preventive_maintenance_recommendations': self._generate_maintenance_recommendations()}}

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

