from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def is_target_achieved(self) -> bool:
        """Check if compliance target is achieved"""
        if not self.metrics_history:
            return False
        
        latest = self.metrics_history[-1]
        return latest.compliance_percentage >= self.compliance_threshold
    