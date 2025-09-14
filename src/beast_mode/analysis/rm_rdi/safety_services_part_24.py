from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _emergency_shutdown_callback(self) -> None:
        """Callback for emergency shutdown"""
        self.emergency_shutdown_triggered = True
        self.analysis_allowed = False
        self.logger.critical('Emergency shutdown callback executed')
