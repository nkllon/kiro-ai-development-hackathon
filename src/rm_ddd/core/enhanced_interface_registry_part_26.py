from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def optimize_interface_cache(self):
        """Optimize interface cache based on usage patterns"""
        # Clear cache for unused interfaces
        current_time = datetime.now()
        for interface_id, metrics in self.metrics.items():
            # Remove from cache if not used in last 24 hours
            time_diff = (current_time - metrics.last_accessed).total_seconds()
            if time_diff > 86400 and interface_id in self.cache:
                del self.cache[interface_id]
        
        # Pre-load cache for frequently used interfaces
        for interface_id, metrics in self.metrics.items():
            if metrics.usage_count > 10 and interface_id not in self.cache:
                if interface_id in self.interfaces:
                    self.cache[interface_id] = self.interfaces[interface_id]
    