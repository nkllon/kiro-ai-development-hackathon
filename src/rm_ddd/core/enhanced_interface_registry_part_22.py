from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def save_metrics(self):
        """Save interface metrics to storage"""
        metrics_file = self.registry_file.replace('.json', '_metrics.json')
        try:
            data = {
                interface_id: {
                    'interface_id': metrics.interface_id,
                    'usage_count': metrics.usage_count,
                    'last_accessed': metrics.last_accessed.isoformat(),
                    'performance_score': metrics.performance_score,
                    'error_count': metrics.error_count,
                    'success_rate': metrics.success_rate
                }
                for interface_id, metrics in self.metrics.items()
            }
            with open(metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving metrics: {e}")
    