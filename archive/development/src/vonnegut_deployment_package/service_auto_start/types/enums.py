#!/usr/bin/env python3
"""
Enumerations for service auto-start framework.
"""

from enum import Enum, auto


class Platform(Enum):
    """Supported platforms for auto-start configuration."""
    MACOS = "macos"
    LINUX = "linux"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    WINDOWS = "windows"
    UNKNOWN = "unknown"


class ServiceStatus(Enum):
    """Service registration and runtime status."""
    REGISTERED = "registered"
    CONFIGURED = "configured"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UNKNOWN = "unknown"


class HealthCheckTool(Enum):
    """Available health check tools."""
    WGET = "wget"
    CURL = "curl"
    NC = "nc"
    PYTHON = "python"
    PYTHON3 = "python3"
    NODE = "node"
    BASH = "bash"
    SH = "sh"


class RestartPolicy(Enum):
    """Service restart policies."""
    ALWAYS = "always"
    UNLESS_STOPPED = "unless-stopped"
    ON_FAILURE = "on-failure"
    NO = "no"


class ConfigurationResult(Enum):
    """Results of configuration operations."""
    SUCCESS = auto()
    FAILED = auto()
    PARTIAL = auto()
    SKIPPED = auto()


class ValidationResult(Enum):
    """Results of validation operations."""
    PASSED = auto()
    FAILED = auto()
    WARNING = auto()
    SKIPPED = auto()