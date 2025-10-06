"""Interface definitions for Google Calendar MCP integration.

This package contains all interface definitions organized by domain responsibility,
following the principle of separation of concerns.
"""

from .server_interfaces import MCPServerInterface
from .auth_interfaces import AuthManagerInterface
from .calendar_interfaces import CalendarOperationsInterface
from .error_interfaces import ErrorHandlerInterface
from .config_interfaces import ConfigManagerInterface

__all__ = [
    "MCPServerInterface",
    "AuthManagerInterface", 
    "CalendarOperationsInterface",
    "ErrorHandlerInterface",
    "ConfigManagerInterface"
]