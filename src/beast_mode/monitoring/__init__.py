"""
Beast Mode Monitoring System

Multi-modal monitoring dashboard with scenario-based interfaces:
- Whiskey Mode: Beautiful terminal dashboard for ambient monitoring
- Page Me Mode: Critical alerting system
- War Room Mode: Comprehensive web dashboard
"""

from .whiskey_mode import WhiskeyModeDisplay, WhiskeyModeStatus
from .events import (
    Event, 
    TestResultEvent, 
    HubrisPreventionEvent, 
    SystemHealthEvent,
    FilesystemEvent,
    EventSeverity,
    TestStatus
)

__all__ = [
    'WhiskeyModeDisplay',
    'WhiskeyModeStatus',
    'Event',
    'TestResultEvent',
    'HubrisPreventionEvent',
    'SystemHealthEvent',
    'FilesystemEvent',
    'EventSeverity',
    'TestStatus'
]