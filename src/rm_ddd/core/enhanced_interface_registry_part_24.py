from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def track_interface_usage(self, interface_id: str, success: bool = True):
        """Track interface usage for metrics"""
        if interface_id in self.metrics:
            metrics = self.metrics[interface_id]
            metrics.usage_count += 1
            metrics.last_accessed = datetime.now()
            
            if success:
                metrics.success_rate = (metrics.success_rate * (metrics.usage_count - 1) + 1.0) / metrics.usage_count
            else:
                metrics.error_count += 1
                metrics.success_rate = (metrics.success_rate * (metrics.usage_count - 1) + 0.0) / metrics.usage_count
            
            self.save_metrics()
    