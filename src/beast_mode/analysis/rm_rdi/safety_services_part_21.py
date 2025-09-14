from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def is_operation_safe(self, operation_name: str) -> bool:
        """Check if an operation is safe to perform"""
        if self.emergency_shutdown_triggered:
            self.logger.warning(f'Operation {operation_name} blocked - emergency shutdown active')
            return False
        if not self.analysis_allowed:
            self.logger.warning(f'Operation {operation_name} blocked - analysis disabled')
            return False
        violations = self.resource_monitor.check_limits()
        if violations:
            self.logger.warning(f'Operation {operation_name} blocked - resource violations: {violations}')
            return False
        return True
