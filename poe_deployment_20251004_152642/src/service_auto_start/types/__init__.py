"""Type definitions and data models for service auto-start."""

from .models import (
    ServiceDefinition,
    ServiceRegistration,
    HealthCheckConfig,
    PlatformConfig,
    AutoStartResult
)

from .enums import (
    Platform,
    ServiceStatus,
    HealthCheckTool,
    RestartPolicy
)

__all__ = [
    "ServiceDefinition",
    "ServiceRegistration", 
    "HealthCheckConfig",
    "PlatformConfig",
    "AutoStartResult",
    "Platform",
    "ServiceStatus",
    "HealthCheckTool",
    "RestartPolicy"
]