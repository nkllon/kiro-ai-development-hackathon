from datetime import datetime
from typing import Dict, List, Any

    def generate_health_report(self) -> str:
        """Generate a comprehensive health report."""
        overall = self.get_overall_health()
        
        report = f"""
🏥 BEAST MODE FRAMEWORK HEALTH DASHBOARD
========================================

Overall Health: {overall['health_percentage']:.1f}%
Total Modules: {overall['total_modules']}
Healthy: {overall['healthy']}
Degraded: {overall['degraded']}
Unhealthy: {overall['unhealthy']}

Last Update: {overall['last_update']}

Module Details:
"""
        
        for module_id, health_data in self.modules.items():
            report += f"""
  {module_id}:
    Status: {health_data.get('status', 'unknown')}
    Errors: {health_data.get('errors', 0)}
    Operations: {health_data.get('operation_count', 0)}
    Uptime: {health_data.get('uptime_seconds', 0):.2f}s
    Memory: {health_data.get('memory_usage_mb', 0):.2f}MB
    CPU: {health_data.get('cpu_usage_percent', 0):.2f}%
"""
        
        return report
