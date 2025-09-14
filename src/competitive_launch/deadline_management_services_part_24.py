from datetime import datetime
from typing import Dict, List, Any

    def get_progress_report(self) -> Dict[str, Any]:
        """Get comprehensive progress report."""
        try:
            status = self.get_deadline_status()
            critical_path = self.calculate_critical_path()
            task_breakdown = {}
            for task_status in TaskStatus:
                count = len([t for t in self.tasks if t.status == task_status])
                task_breakdown[task_status.value] = count
            priority_breakdown = {}
            for priority in TaskPriority:
                count = len([t for t in self.tasks if t.priority == priority])
                priority_breakdown[priority.value] = count
            high_impact_tasks = [t for t in self.tasks if t.competitive_impact > 0.7]
            medium_impact_tasks = [t for t in self.tasks if 0.3 <= t.competitive_impact <= 0.7]
            low_impact_tasks = [t for t in self.tasks if t.competitive_impact < 0.3]
            return {'deadline_status': {'days_remaining': status.days_remaining, 'hours_remaining': status.hours_remaining, 'completion_percentage': status.completion_percentage, 'risk_level': status.risk_level, 'acceleration_required': status.acceleration_required, 'scope_optimization_needed': status.scope_optimization_needed}, 'critical_path': {'total_tasks': len(critical_path.path_tasks), 'total_duration_hours': critical_path.total_duration_hours, 'slack_time_hours': critical_path.slack_time_hours, 'risk_factors': critical_path.risk_factors, 'acceleration_opportunities': critical_path.acceleration_opportunities}, 'task_breakdown': task_breakdown, 'priority_breakdown': priority_breakdown, 'competitive_impact': {'high_impact_tasks': len(high_impact_tasks), 'medium_impact_tasks': len(medium_impact_tasks), 'low_impact_tasks': len(low_impact_tasks)}, 'emergency_protocols': {'active': self.emergency_protocols_active, 'hackathon_deadline': self.hackathon_deadline.isoformat()}}
        except Exception as e:
            logger.error(f'Failed to generate progress report: {e}')
            return {'error': str(e)}
