"""
Beast Mode Framework - Operations Module
Implements operational dashboards, logging, and audit trail systems
"""

from .operational_dashboard_manager import (
    OperationalDashboardManager,
    DashboardType,
    DashboardConfig,
    DashboardData
)

from .comprehensive_logging_system import (
    ComprehensiveLoggingSystem,
    LogLevel,
    AuditEvent,
    LogEntry
)

__all__ = [
    'OperationalDashboardManager',
    'DashboardType',
    'DashboardConfig', 
    'DashboardData',
    'ComprehensiveLoggingSystem',
    'LogLevel',
    'AuditEvent',
    'LogEntry'
]