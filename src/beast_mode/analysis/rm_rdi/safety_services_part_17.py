from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


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

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

