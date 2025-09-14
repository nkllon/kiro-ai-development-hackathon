from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_compliance_trend(self) -> str:
        """Get compliance trend"""
        if len(self.metrics_history) < 2:
            return 'insufficient_data'
        
        current = self.metrics_history[-1].compliance_percentage
        previous = self.metrics_history[-2].compliance_percentage
        
        if current > previous:
            return 'improving'
        elif current < previous:
            return 'declining'
        else:
            return 'stable'
    