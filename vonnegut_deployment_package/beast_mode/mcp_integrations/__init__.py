"""Beast Mode MCP Integrations Package.

This package contains Model Context Protocol (MCP) integrations for various external services,
following the Beast Mode framework's ReflectiveModule pattern for systematic monitoring and health management.
"""

from .google_calendar import GoogleCalendarMCPServer

__all__ = ["GoogleCalendarMCPServer"]