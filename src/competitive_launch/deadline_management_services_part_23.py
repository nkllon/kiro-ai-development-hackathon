from datetime import datetime
from typing import Dict, List, Any

    def optimize_scope_for_deadline(self) -> Dict[str, Any]:
        """Optimize project scope to meet deadline."""
        logger.info('Optimizing scope for deadline')
        try:
            status = self.get_deadline_status()
            if not status.scope_optimization_needed:
                return {'optimization_needed': False, 'message': 'Current scope is manageable'}
            tasks_to_remove = []
            tasks_to_defer = []
            tasks_to_simplify = []
            for task in self.tasks:
                if task.status == TaskStatus.COMPLETED:
                    continue
                if task.priority in [TaskPriority.LOW, TaskPriority.OPTIONAL] and task.competitive_impact < 0.3:
                    tasks_to_remove.append(task.task_id)
                elif task.priority == TaskPriority.MEDIUM and task.technical_debt_risk > 0.7:
                    tasks_to_defer.append(task.task_id)
                elif task.priority in [TaskPriority.CRITICAL, TaskPriority.HIGH] and task.estimated_hours > 20:
                    tasks_to_simplify.append(task.task_id)
            optimization_actions = []
            for task_id in tasks_to_remove:
                self.update_task_status(task_id, TaskStatus.CANCELLED)
                optimization_actions.append(f'Removed task: {task_id}')
            for task_id in tasks_to_defer:
                task = self._find_task(task_id)
                if task:
                    task.deadline = self.hackathon_deadline + timedelta(days=7)
                    optimization_actions.append(f'Deferred task: {task_id}')
            for task_id in tasks_to_simplify:
                task = self._find_task(task_id)
                if task:
                    task.estimated_hours *= 0.7
                    optimization_actions.append(f'Simplified task: {task_id}')
            self.critical_path = self.calculate_critical_path()
            optimization_result = {'optimization_completed': True, 'tasks_removed': len(tasks_to_remove), 'tasks_deferred': len(tasks_to_defer), 'tasks_simplified': len(tasks_to_simplify), 'actions_taken': optimization_actions, 'new_critical_path_hours': self.critical_path.total_duration_hours, 'optimized_at': datetime.now().isoformat()}
            logger.info(f'Scope optimization completed: {len(optimization_actions)} actions taken')
            return optimization_result
        except Exception as e:
            logger.error(f'Failed to optimize scope: {e}')
            return {'optimization_completed': False, 'error': str(e)}
