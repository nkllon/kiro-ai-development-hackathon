"""Data models for Google Calendar MCP integration.

This module defines the core data structures used throughout the Google Calendar MCP integration,
including calendar events, authentication results, and MCP protocol messages.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class EventStatus(Enum):
    """Calendar event status enumeration."""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class AttendeeStatus(Enum):
    """Attendee response status enumeration."""
    NEEDS_ACTION = "needsAction"
    DECLINED = "declined"
    TENTATIVE = "tentative"
    ACCEPTED = "accepted"


@dataclass
class Attendee:
    """Calendar event attendee information."""
    email: str
    display_name: Optional[str] = None
    response_status: AttendeeStatus = AttendeeStatus.NEEDS_ACTION
    optional: bool = False
    organizer: bool = False


@dataclass
class RecurrenceRule:
    """Calendar event recurrence rule."""
    frequency: str  # DAILY, WEEKLY, MONTHLY, YEARLY
    interval: int = 1
    count: Optional[int] = None
    until: Optional[datetime] = None
    by_day: Optional[List[str]] = None
    by_month_day: Optional[List[int]] = None


@dataclass
class CalendarEvent:
    """Google Calendar event data model."""
    id: str
    summary: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: List[Attendee] = field(default_factory=list)
    recurrence: Optional[RecurrenceRule] = None
    status: EventStatus = EventStatus.CONFIRMED
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    calendar_id: str = "primary"
    
    def __post_init__(self):
        """Validate event data after initialization."""
        if self.start_time >= self.end_time:
            raise ValueError("Event start time must be before end time")


@dataclass
class AuthResult:
    """Authentication operation result."""
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    scopes: List[str] = field(default_factory=list)


@dataclass
class TokenInfo:
    """OAuth token information."""
    access_token: str
    refresh_token: str
    expires_at: datetime
    scopes: List[str]
    token_type: str = "Bearer"
    
    @property
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return datetime.utcnow() >= self.expires_at


@dataclass
class MCPError:
    """MCP protocol error information."""
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None


@dataclass
class MCPRequest:
    """MCP protocol request message."""
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None
    jsonrpc: str = "2.0"
    
    def __post_init__(self):
        """Generate ID if not provided."""
        if self.id is None:
            self.id = str(uuid4())


@dataclass
class MCPResponse:
    """MCP protocol response message."""
    result: Optional[Any] = None
    error: Optional[MCPError] = None
    id: Optional[str] = None
    jsonrpc: str = "2.0"
    
    def __post_init__(self):
        """Validate response has either result or error."""
        if self.result is None and self.error is None:
            raise ValueError("Response must have either result or error")
        if self.result is not None and self.error is not None:
            raise ValueError("Response cannot have both result and error")


@dataclass
class AvailabilityResult:
    """Calendar availability check result."""
    start_time: datetime
    end_time: datetime
    is_available: bool
    conflicting_events: List[CalendarEvent] = field(default_factory=list)
    free_slots: List[tuple[datetime, datetime]] = field(default_factory=list)


@dataclass
class EventData:
    """Data for creating or updating calendar events."""
    summary: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: List[str] = field(default_factory=list)  # Email addresses
    recurrence: Optional[RecurrenceRule] = None
    calendar_id: str = "primary"
    
    def to_calendar_event(self, event_id: Optional[str] = None) -> CalendarEvent:
        """Convert to CalendarEvent model."""
        attendee_objects = [
            Attendee(email=email) for email in self.attendees
        ]
        
        return CalendarEvent(
            id=event_id or str(uuid4()),
            summary=self.summary,
            start_time=self.start_time,
            end_time=self.end_time,
            description=self.description,
            location=self.location,
            attendees=attendee_objects,
            recurrence=self.recurrence,
            calendar_id=self.calendar_id
        )


@dataclass
class ModuleHealth:
    """Health status for ReflectiveModule components."""
    module_name: str
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    dependencies: Dict[str, str] = field(default_factory=dict)  # name -> status
    
    @property
    def is_healthy(self) -> bool:
        """Check if module is in healthy state."""
        return self.status == "healthy"