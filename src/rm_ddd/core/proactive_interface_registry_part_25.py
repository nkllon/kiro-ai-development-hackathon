from datetime import datetime
from typing import Dict, List, Any

    def save_health_checks(self):
        """Save interface health checks to storage"""
        health_file = self.registry_file.replace('.json', '_health.json')
        try:
            data = {
                interface_id: {
                    'interface_id': health.interface_id,
                    'status': health.status,
                    'last_checked': health.last_checked.isoformat(),
                    'issues': health.issues,
                    'recommendations': health.recommendations,
                    'health_score': health.health_score
                }
                for interface_id, health in self.health_checks.items()
            }
            with open(health_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving health checks: {e}")
    