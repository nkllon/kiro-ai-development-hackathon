from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def emergency_shutdown(self, reason: str='Operator request') -> None:
        """Trigger emergency shutdown"""
        self.emergency_shutdown_triggered = True
        self.analysis_allowed = False
        self.kill_switch.emergency_shutdown(reason)
