from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _calculate_scope_impact(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate impact of scope optimization plan."""
        return {'time_saved_days': plan['total_time_saved'], 'competitive_impact_preserved': plan['competitive_impact_preserved'], 'risk_reduction': min(1.0, plan['total_time_saved'] / 5), 'implementation_effort': 'low' if len(plan['reductions']) <= 2 else 'medium'}
