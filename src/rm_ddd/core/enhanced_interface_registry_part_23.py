from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def register_interface(self, interface: InterfaceMetadata) -> bool:
        """Enhanced interface registration with metrics"""
        success = super().register_interface(interface)
        if success:
            # Initialize metrics for new interface
            self.metrics[interface.interface_id] = InterfaceMetrics(
                interface_id=interface.interface_id,
                usage_count=0,
                last_accessed=datetime.now(),
                performance_score=1.0,
                error_count=0,
                success_rate=1.0
            )
            self.save_metrics()
        return success
    