"""
Service Auto-Start Governance Framework

Systematic service auto-start management across all platforms.
"""

__version__ = "1.0.0"
__author__ = "Beast Mode Framework"

from .core.service_auto_starter import ServiceAutoStarter
from .registry.service_registry import ServiceRegistry
from .health.health_check_validator import HealthCheckValidator

__all__ = [
    "ServiceAutoStarter",
    "ServiceRegistry", 
    "HealthCheckValidator"
]