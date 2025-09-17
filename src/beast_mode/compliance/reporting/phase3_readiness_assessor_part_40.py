from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _evaluate_task_completion_metric(self, task_status) -> ReadinessMetric:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Evaluate task completion readiness metric."""
        current_score = task_status.reconciliation_score
        required_score = self.readiness_thresholds[ReadinessCriteria.TASK_COMPLETION]
        if current_score >= required_score:
            status = ReadinessStatus.READY
        elif current_score >= required_score * 0.85:
            status = ReadinessStatus.CONDITIONALLY_READY
        else:
            status = ReadinessStatus.NOT_READY
        blocking_issues = []
        recommendations = []
        if len(task_status.missing_implementations) > 0:
            blocking_issues.append(f'{len(task_status.missing_implementations)} incomplete tasks')
            recommendations.append('Complete all claimed tasks before Phase 3')
        missing_tasks = task_status.missing_implementations[:3]
        if missing_tasks:
            recommendations.extend([f'Complete task: {task}' for task in missing_tasks])
        return ReadinessMetric(criteria=ReadinessCriteria.TASK_COMPLETION, current_value=current_score, required_value=required_score, weight=self.criteria_weights[ReadinessCriteria.TASK_COMPLETION], status=status, description=f'Task completion reconciliation: {current_score:.1f}% (required: {required_score:.1f}%)', blocking_issues=blocking_issues, recommendations=recommendations)

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

