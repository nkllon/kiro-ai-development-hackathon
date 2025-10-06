"""Command-line interface for service auto-start management."""

from .commands import (
    install_service,
    verify_service,
    remove_service,
    service_status,
    health_check,
    list_services,
    validate_config,
    show_startup_order,
    emergency_stop,
    emergency_restart
)

__all__ = [
    "install_service",
    "verify_service", 
    "remove_service",
    "service_status",
    "health_check",
    "list_services",
    "validate_config",
    "show_startup_order",
    "emergency_stop",
    "emergency_restart"
]