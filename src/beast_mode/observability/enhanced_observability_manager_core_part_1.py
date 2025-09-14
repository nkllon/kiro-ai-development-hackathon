from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.rm_ddd.core.health import ModuleHealth, ModuleStatus
from src.rm_ddd.core.registry import register_module

class AlertSeverity(Enum, ReflectiveModule):
    ModuleHealth = ModuleHealth.HEALTHY
    ModuleStatus = ModuleStatus.ACTIVE

    def check_health(self):
        return {
            'status': self.ModuleStatus,
            'health': self.ModuleHealth
        }
    def __init__(self):
        register_module('AlertSeverity', self)