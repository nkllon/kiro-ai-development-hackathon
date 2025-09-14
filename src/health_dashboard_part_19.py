from datetime import datetime
from typing import Dict, List, Any

    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        healthy_count = 0
        degraded_count = 0
        unhealthy_count = 0
        total_modules = len(self.modules)
        
        for module_id, health_data in self.modules.items():
            status = health_data.get('status', 'unknown')
            if status == 'HEALTHY':
                healthy_count += 1
            elif status == 'DEGRADED':
                degraded_count += 1
            elif status == 'UNHEALTHY':
                unhealthy_count += 1
        
        return {
            'total_modules': total_modules,
            'healthy': healthy_count,
            'degraded': degraded_count,
            'unhealthy': unhealthy_count,
            'health_percentage': (healthy_count / total_modules * 100) if total_modules > 0 else 0,
            'last_update': self.last_update
        }
    