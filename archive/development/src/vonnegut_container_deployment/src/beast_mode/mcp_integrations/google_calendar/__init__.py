"""Google Calendar MCP Integration Package.

This package provides Google Calendar functionality through the Model Context Protocol (MCP),
enabling AI assistants to interact with Google Calendar data within the Kiro environment.
"""

from .server import GoogleCalendarMCPServer
from .auth_manager import GoogleAuthManager
from .operations_handler import CalendarOperationsHandler
from .models import CalendarEvent, AuthResult, MCPRequest, MCPResponse
from .profiling import PerformanceProfiler, get_profiler, profile
from .request_router import MCPRequestRouter
from .base import ReflectiveModule
from .interfaces import (
    MCPServerInterface,
    AuthManagerInterface,
    CalendarOperationsInterface,
    ErrorHandlerInterface,
    ConfigManagerInterface
)

__all__ = [
    "GoogleCalendarMCPServer",
    "GoogleAuthManager", 
    "CalendarOperationsHandler",
    "CalendarEvent",
    "AuthResult",
    "MCPRequest",
    "MCPResponse",
    "PerformanceProfiler",
    "get_profiler",
    "profile",
    "MCPRequestRouter",
    "ReflectiveModule",
    "MCPServerInterface",
    "AuthManagerInterface",
    "CalendarOperationsInterface",
    "ErrorHandlerInterface",
    "ConfigManagerInterface"
]