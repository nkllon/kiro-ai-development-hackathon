from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_deadline_status(self) -> DeadlineStatus:
        """Get current deadline status and recommendations."""
        logger.info('Calculating deadline status')
        try:
            time_remaining = self.hackathon_deadline - datetime.now()
            days_remaining = time_remaining.days
            hours_remaining = time_remaining.total_seconds() / 3600
            total_tasks = len(self.tasks)
            completed_tasks = len([t for t in self.tasks if t.status == TaskStatus.COMPLETED])
            completion_percentage = completed_tasks / total_tasks * 100 if total_tasks > 0 else 0
            if not self.critical_path:
                self.critical_path = self.calculate_critical_path()
            critical_path_remaining = self.critical_path.total_duration_hours
            if hours_remaining < critical_path_remaining * 1.2:
                risk_level = 'critical'
            elif hours_remaining < critical_path_remaining * 1.5:
                risk_level = 'high'
            elif hours_remaining < critical_path_remaining * 2.0:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            acceleration_required = risk_level in ['critical', 'high']
            scope_optimization_needed = risk_level == 'critical' or completion_percentage < 50
            return DeadlineStatus(days_remaining=days_remaining, hours_remaining=hours_remaining, completion_percentage=completion_percentage, critical_path_remaining=critical_path_remaining, risk_level=risk_level, acceleration_required=acceleration_required, scope_optimization_needed=scope_optimization_needed)
        except Exception as e:
            logger.error(f'Failed to calculate deadline status: {e}')
            return DeadlineStatus(0, 0.0, 0.0, 0.0, 'critical', True, True)
