from datetime import datetime
from typing import Dict, List, Any

    def __init__(self, limits: Optional[ResourceLimits]=None):
        self.limits = limits or ResourceLimits()
        self.kill_switch = KillSwitch()
        self.resource_monitor = ResourceMonitor(self.limits)
        self.safety_validator = SafetyValidator()
        self.logger = logging.getLogger('rm_rdi_analysis.safety_manager')
        self.is_safe_mode = True
        self.analysis_allowed = True
        self.emergency_shutdown_triggered = False
        self.kill_switch.register_shutdown_callback(self._emergency_shutdown_callback)
        self.resource_monitor.register_violation_callback(self._resource_violation_callback)
