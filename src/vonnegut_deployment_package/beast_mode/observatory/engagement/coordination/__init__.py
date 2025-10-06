"""
Engagement Coordination System

Provides unified coordination and event management for all engagement subsystems.
"""

from .event_coordinator import (
    EngagementEventCoordinator,
    EngagementEvent,
    EngagementEventType,
    EngagementEventPriority
)

__all__ = [
    "EngagementEventCoordinator",
    "EngagementEvent", 
    "EngagementEventType",
    "EngagementEventPriority"
]