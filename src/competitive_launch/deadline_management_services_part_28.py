from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _identify_risk_factors(self, critical_tasks: List[HackathonTask], time_remaining: float) -> List[str]:
        """Identify risk factors for critical path."""
        risks = []
        if time_remaining < 48:
            risks.append('Critical time shortage')
        high_debt_tasks = [t for t in critical_tasks if t.technical_debt_risk > 0.7]
        if high_debt_tasks:
            risks.append(f'High technical debt risk in {len(high_debt_tasks)} critical tasks')
        blocked_tasks = [t for t in critical_tasks if t.status == TaskStatus.BLOCKED]
        if blocked_tasks:
            risks.append(f'{len(blocked_tasks)} critical tasks are blocked')
        long_tasks = [t for t in critical_tasks if t.estimated_hours > 16]
        if long_tasks:
            risks.append(f'{len(long_tasks)} critical tasks exceed 16 hours')
        return risks
