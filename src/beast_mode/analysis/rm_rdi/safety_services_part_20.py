from datetime import datetime
from typing import Dict, List, Any

    def get_safety_status(self) -> SafetyStatus:
        """Get current safety status"""
        violations = self.resource_monitor.check_limits()
        usage = self.resource_monitor.get_current_usage()
        return SafetyStatus(is_safe=len(violations) == 0 and (not self.emergency_shutdown_triggered), resource_usage=usage, violations=violations, last_check=datetime.now(), kill_switch_armed=self.kill_switch.is_armed)
