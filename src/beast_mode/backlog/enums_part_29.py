from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth, ModuleStatus
from src.rm_ddd.core.registry import register_module

class StakeholderType(Enum, ReflectiveModule):
    """Types of stakeholders in the system"""
    MPM = "mpm"
    BEAST = "beast"
    STAKEHOLDER = "stakeholder"
    ADMIN = "admin"
    DEVELOPER = "developer"
    OPERATIONS = "operations"
    SECURITY = "security"
    ModuleHealth = ModuleHealth.HEALTHY
    ModuleStatus = ModuleStatus.ACTIVE

    def check_health(self):
        return {
            'status': self.ModuleStatus,
            'health': self.ModuleHealth
        }
    def __init__(self):
        register_module('StakeholderType', self)