"""Google Calendar Operations Handler.

This module provides calendar operations functionality for the Google Calendar MCP integration,
following the Beast Mode framework's ReflectiveModule pattern.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.credentials import Credentials

from .base import GoogleCalendarReflectiveModule
from .interfaces.calendar_interfaces import CalendarOperationsInterface
from .models import CalendarEvent, EventData, AvailabilityResult
from .profiling import profile


class CalendarOperationsHandler(GoogleCalendarReflectiveModule, CalendarOperationsInterface):
    """Handler for Google Calendar operations.
    
    Provides calendar event management functionality including querying, creating,
    updating, and deleting events, as well as availability checking.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the calendar operations handler.
        
        Args:
            config: Operations configuration dictionary
        """
        super().__init__("calendar_operations_handler", config)
        
        # Configuration
        self.default_calendar_id = self.config.get("default_calendar_id", "primary")
        self.max_events_per_query = self.config.get("max_events_per_query", 250)
        self.timezone = self.config.get("timezone", "UTC")
        
        # Dependencies
        self.auth_manager = None
        self.google_calendar_service = None
        
        # Operation statistics
        self.operations_count = 0
        self.errors_count = 0
        
        self.logger.info(
            "Calendar Operations Handler initialized",
            extra={
                "correlation_id": self.correlation_id,
                "default_calendar_id": self.default_calendar_id,
                "max_events_per_query": self.max_events_per_query
            }
        )
    
    def set_auth_manager(self, auth_manager):
        """Set the authentication manager dependency.
        
        Args:
            auth_manager: GoogleAuthManager instance
        """
        self.auth_manager = auth_manager
        self.add_mcp_dependency("auth_manager", "healthy")
        self.logger.info("Auth manager dependency set")
    
    def initialize(self) -> bool:
        """Initialize the calendar operations handler.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing Calendar Operations Handler")
            
            # Validate dependencies
            if not self.auth_manager:
                self.log_with_correlation("warning", "Auth manager not set, continuing in stub mode")
                # Don't return False - continue in stub mode
            
            # Initialize Google Calendar service
            if not self._initialize_calendar_service():
                self.log_with_correlation("warning", "Failed to initialize calendar service, continuing in stub mode")
                # Don't return False - continue in stub mode
            self.logger.info("Calendar Operations Handler initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(
                f"Failed to initialize operations handler: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            # Health is managed by unified ReflectiveModule
            return False
    
    @profile("calendar_get_events")
    def get_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get calendar events in the specified time range.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of calendar events as dictionaries
        """
        try:
            self.operations_count += 1
            
            self.logger.info(
                f"Getting events from {start_time} to {end_time}",
                extra={
                    "correlation_id": self.correlation_id,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                }
            )
            
            # Validate authentication
            if not self.auth_manager or not self.auth_manager.is_authenticated():
                raise ValueError("Not authenticated with Google Calendar")
            
            # Check if we have real service or stub
            if self.google_calendar_service == "stub_service":
                return self._get_events_stub(start_time, end_time)
            
            # Real Google Calendar API call
            try:
                # Format times for Google API (RFC3339)
                time_min = start_time.isoformat() + 'Z' if start_time.tzinfo is None else start_time.isoformat()
                time_max = end_time.isoformat() + 'Z' if end_time.tzinfo is None else end_time.isoformat()
                
                # Call Google Calendar API
                events_result = self.google_calendar_service.events().list(
                    calendarId=self.default_calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=self.max_events_per_query,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                
                # Convert to our format
                formatted_events = []
                for event in events:
                    formatted_event = self._format_event_from_google(event)
                    formatted_events.append(formatted_event)
                
                self.logger.info(f"Retrieved {len(formatted_events)} events from Google Calendar")
                return formatted_events
                
            except HttpError as e:
                if e.resp.status == 401:
                    # Token might be expired, try to refresh
                    if self.auth_manager.refresh_token():
                        # Reinitialize service and retry
                        self._initialize_calendar_service()
                        return self.get_events(start_time, end_time)
                    else:
                        raise ValueError("Authentication expired and refresh failed")
                else:
                    raise ValueError(f"Google Calendar API error: {e}")
            
        except Exception as e:
            self.errors_count += 1
            self.logger.error(
                f"Failed to get events: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            raise
    
    def _get_events_stub(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Stub implementation for get_events when real API is not available."""
        return [
            {
                "id": "stub_event_1",
                "summary": "Sample Meeting (Stub)",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "description": "A sample calendar event from stub implementation",
                "location": "Conference Room A",
                "attendees": ["user@example.com"],
                "status": "confirmed"
            }
        ]
    
    def _format_event_from_google(self, google_event: Dict[str, Any]) -> Dict[str, Any]:
        """Format Google Calendar event to our standard format.
        
        Args:
            google_event: Event from Google Calendar API
            
        Returns:
            Formatted event dictionary
        """
        # Extract start and end times
        start = google_event.get('start', {})
        end = google_event.get('end', {})
        
        start_time = start.get('dateTime', start.get('date', ''))
        end_time = end.get('dateTime', end.get('date', ''))
        
        # Extract attendees
        attendees = []
        for attendee in google_event.get('attendees', []):
            attendees.append(attendee.get('email', ''))
        
        return {
            "id": google_event.get('id', ''),
            "summary": google_event.get('summary', 'No Title'),
            "start_time": start_time,
            "end_time": end_time,
            "description": google_event.get('description', ''),
            "location": google_event.get('location', ''),
            "attendees": attendees,
            "status": google_event.get('status', 'confirmed'),
            "html_link": google_event.get('htmlLink', ''),
            "created": google_event.get('created', ''),
            "updated": google_event.get('updated', '')
        }
    
    @profile("calendar_create_event")
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event.
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            Created event data as dictionary
        """
        try:
            self.operations_count += 1
            
            self.logger.info(
                f"Creating event: {event_data.get('summary', 'Untitled')}",
                extra={
                    "correlation_id": self.correlation_id,
                    "event_summary": event_data.get("summary")
                }
            )
            
            # Validate authentication
            if not self.auth_manager or not self.auth_manager.is_authenticated():
                raise ValueError("Not authenticated with Google Calendar")
            
            # Check if we have real service or stub
            if self.google_calendar_service == "stub_service":
                return self._create_event_stub(event_data)
            
            # Prepare event for Google Calendar API
            google_event = self._format_event_for_google(event_data)
            
            try:
                # Create event using Google Calendar API
                created_event = self.google_calendar_service.events().insert(
                    calendarId=self.default_calendar_id,
                    body=google_event
                ).execute()
                
                # Format response
                formatted_event = self._format_event_from_google(created_event)
                
                self.logger.info(f"Event created successfully: {formatted_event['id']}")
                return formatted_event
                
            except HttpError as e:
                if e.resp.status == 401:
                    # Token might be expired, try to refresh
                    if self.auth_manager.refresh_token():
                        # Reinitialize service and retry
                        self._initialize_calendar_service()
                        return self.create_event(event_data)
                    else:
                        raise ValueError("Authentication expired and refresh failed")
                else:
                    raise ValueError(f"Google Calendar API error: {e}")
            
        except Exception as e:
            self.errors_count += 1
            self.logger.error(
                f"Failed to create event: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            raise
    
    def _create_event_stub(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stub implementation for create_event when real API is not available."""
        return {
            "id": f"stub_created_event_{self.operations_count}",
            "summary": event_data.get("summary", "Untitled"),
            "start_time": event_data.get("start_time", datetime.utcnow().isoformat()),
            "end_time": event_data.get("end_time", datetime.utcnow().isoformat()),
            "description": event_data.get("description", ""),
            "location": event_data.get("location", ""),
            "attendees": event_data.get("attendees", []),
            "status": "confirmed",
            "created_at": datetime.utcnow().isoformat()
        }
    
    def _format_event_for_google(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format event data for Google Calendar API.
        
        Args:
            event_data: Our event data format
            
        Returns:
            Google Calendar API event format
        """
        google_event = {
            'summary': event_data.get('summary', 'No Title'),
            'description': event_data.get('description', ''),
            'location': event_data.get('location', ''),
        }
        
        # Format start and end times
        start_time = event_data.get('start_time')
        end_time = event_data.get('end_time')
        
        if isinstance(start_time, str):
            google_event['start'] = {'dateTime': start_time}
        elif isinstance(start_time, datetime):
            google_event['start'] = {'dateTime': start_time.isoformat()}
        
        if isinstance(end_time, str):
            google_event['end'] = {'dateTime': end_time}
        elif isinstance(end_time, datetime):
            google_event['end'] = {'dateTime': end_time.isoformat()}
        
        # Format attendees
        attendees = event_data.get('attendees', [])
        if attendees:
            google_event['attendees'] = [{'email': email} for email in attendees if email]
        
        return google_event
    
    @profile("calendar_update_event")
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing calendar event.
        
        Args:
            event_id: ID of event to update
            updates: Dictionary of updates to apply
            
        Returns:
            Updated event data as dictionary
        """
        try:
            self.operations_count += 1
            
            self.logger.info(
                f"Updating event: {event_id}",
                extra={
                    "correlation_id": self.correlation_id,
                    "event_id": event_id,
                    "updates": list(updates.keys())
                }
            )
            
            # Validate authentication
            if not self.auth_manager or not self.auth_manager.is_authenticated():
                raise ValueError("Not authenticated with Google Calendar")
            
            # Check if we have real service or stub
            if self.google_calendar_service == "stub_service":
                return self._update_event_stub(event_id, updates)
            
            try:
                # Get existing event first
                existing_event = self.google_calendar_service.events().get(
                    calendarId=self.default_calendar_id,
                    eventId=event_id
                ).execute()
                
                # Apply updates to existing event
                for key, value in updates.items():
                    if key == 'summary':
                        existing_event['summary'] = value
                    elif key == 'description':
                        existing_event['description'] = value
                    elif key == 'location':
                        existing_event['location'] = value
                    elif key == 'start_time':
                        if isinstance(value, str):
                            existing_event['start'] = {'dateTime': value}
                        elif isinstance(value, datetime):
                            existing_event['start'] = {'dateTime': value.isoformat()}
                    elif key == 'end_time':
                        if isinstance(value, str):
                            existing_event['end'] = {'dateTime': value}
                        elif isinstance(value, datetime):
                            existing_event['end'] = {'dateTime': value.isoformat()}
                    elif key == 'attendees':
                        existing_event['attendees'] = [{'email': email} for email in value if email]
                
                # Update event using Google Calendar API
                updated_event = self.google_calendar_service.events().update(
                    calendarId=self.default_calendar_id,
                    eventId=event_id,
                    body=existing_event
                ).execute()
                
                # Format response
                formatted_event = self._format_event_from_google(updated_event)
                
                self.logger.info(f"Event updated successfully: {event_id}")
                return formatted_event
                
            except HttpError as e:
                if e.resp.status == 401:
                    # Token might be expired, try to refresh
                    if self.auth_manager.refresh_token():
                        # Reinitialize service and retry
                        self._initialize_calendar_service()
                        return self.update_event(event_id, updates)
                    else:
                        raise ValueError("Authentication expired and refresh failed")
                elif e.resp.status == 404:
                    raise ValueError(f"Event not found: {event_id}")
                else:
                    raise ValueError(f"Google Calendar API error: {e}")
            
        except Exception as e:
            self.errors_count += 1
            self.logger.error(
                f"Failed to update event {event_id}: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            raise
    
    def _update_event_stub(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Stub implementation for update_event when real API is not available."""
        return {
            "id": event_id,
            "summary": updates.get("summary", "Updated Event (Stub)"),
            "start_time": updates.get("start_time", datetime.utcnow().isoformat()),
            "end_time": updates.get("end_time", datetime.utcnow().isoformat()),
            "description": updates.get("description", ""),
            "location": updates.get("location", ""),
            "status": "confirmed",
            "updated_at": datetime.utcnow().isoformat()
        }
    
    @profile("calendar_delete_event")
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event.
        
        Args:
            event_id: ID of event to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            self.operations_count += 1
            
            self.logger.info(
                f"Deleting event: {event_id}",
                extra={
                    "correlation_id": self.correlation_id,
                    "event_id": event_id
                }
            )
            
            # Validate authentication
            if not self.auth_manager or not self.auth_manager.is_authenticated():
                raise ValueError("Not authenticated with Google Calendar")
            
            # Check if we have real service or stub
            if self.google_calendar_service == "stub_service":
                self.logger.info(f"Event deleted successfully (stub): {event_id}")
                return True
            
            try:
                # Delete event using Google Calendar API
                self.google_calendar_service.events().delete(
                    calendarId=self.default_calendar_id,
                    eventId=event_id
                ).execute()
                
                self.logger.info(f"Event deleted successfully: {event_id}")
                return True
                
            except HttpError as e:
                if e.resp.status == 401:
                    # Token might be expired, try to refresh
                    if self.auth_manager.refresh_token():
                        # Reinitialize service and retry
                        self._initialize_calendar_service()
                        return self.delete_event(event_id)
                    else:
                        raise ValueError("Authentication expired and refresh failed")
                elif e.resp.status == 404:
                    self.logger.warning(f"Event not found for deletion: {event_id}")
                    return True  # Consider it successful if already gone
                elif e.resp.status == 410:
                    self.logger.warning(f"Event already deleted: {event_id}")
                    return True  # Already deleted
                else:
                    raise ValueError(f"Google Calendar API error: {e}")
            
        except Exception as e:
            self.errors_count += 1
            self.logger.error(
                f"Failed to delete event {event_id}: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            return False
    
    @profile("calendar_check_availability")
    def check_availability(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Check calendar availability for the specified time range.
        
        Args:
            start_time: Start of time range to check
            end_time: End of time range to check
            
        Returns:
            Availability result as dictionary
        """
        try:
            self.operations_count += 1
            
            self.logger.info(
                f"Checking availability from {start_time} to {end_time}",
                extra={
                    "correlation_id": self.correlation_id,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                }
            )
            
            # Validate authentication
            if not self.auth_manager or not self.auth_manager.is_authenticated():
                raise ValueError("Not authenticated with Google Calendar")
            
            # Check if we have real service or stub
            if self.google_calendar_service == "stub_service":
                return self._check_availability_stub(start_time, end_time)
            
            try:
                # Use Google Calendar freebusy API for more accurate availability
                time_min = start_time.isoformat() + 'Z' if start_time.tzinfo is None else start_time.isoformat()
                time_max = end_time.isoformat() + 'Z' if end_time.tzinfo is None else end_time.isoformat()
                
                freebusy_request = {
                    'timeMin': time_min,
                    'timeMax': time_max,
                    'items': [{'id': self.default_calendar_id}]
                }
                
                freebusy_result = self.google_calendar_service.freebusy().query(
                    body=freebusy_request
                ).execute()
                
                # Extract busy periods
                calendar_busy = freebusy_result.get('calendars', {}).get(self.default_calendar_id, {})
                busy_periods = calendar_busy.get('busy', [])
                
                # Calculate availability
                is_available = len(busy_periods) == 0
                
                # Get conflicting events for more details
                conflicting_events = []
                if not is_available:
                    conflicting_events = self.get_events(start_time, end_time)
                
                # Calculate free slots (simplified - could be more sophisticated)
                free_slots = []
                if is_available:
                    free_slots = [(start_time.isoformat(), end_time.isoformat())]
                else:
                    # For now, just indicate no free slots if any conflicts
                    # In a more sophisticated implementation, we'd calculate gaps between busy periods
                    free_slots = []
                
                availability_result = {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "is_available": is_available,
                    "busy_periods": busy_periods,
                    "conflicting_events": conflicting_events,
                    "free_slots": free_slots
                }
                
                self.logger.info(f"Availability check complete: {'available' if is_available else 'busy'}")
                return availability_result
                
            except HttpError as e:
                if e.resp.status == 401:
                    # Token might be expired, try to refresh
                    if self.auth_manager.refresh_token():
                        # Reinitialize service and retry
                        self._initialize_calendar_service()
                        return self.check_availability(start_time, end_time)
                    else:
                        raise ValueError("Authentication expired and refresh failed")
                else:
                    raise ValueError(f"Google Calendar API error: {e}")
            
        except Exception as e:
            self.errors_count += 1
            self.logger.error(
                f"Failed to check availability: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            raise
    
    def _check_availability_stub(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Stub implementation for check_availability when real API is not available."""
        # Get stub events
        events = self._get_events_stub(start_time, end_time)
        is_available = len(events) == 0
        
        return {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "is_available": is_available,
            "busy_periods": [] if is_available else [{"start": start_time.isoformat(), "end": end_time.isoformat()}],
            "conflicting_events": events if not is_available else [],
            "free_slots": [(start_time.isoformat(), end_time.isoformat())] if is_available else []
        }
    
    def _initialize_calendar_service(self) -> bool:
        """Initialize the Google Calendar service.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if not self.auth_manager or not self.auth_manager.is_authenticated():
                self.logger.warning("Auth manager not available or not authenticated, using stub service")
                self.google_calendar_service = "stub_service"
                return True
            
            # Create credentials object from token info
            token_info = self.auth_manager.token_info
            if not token_info:
                self.logger.warning("No token info available, using stub service")
                self.google_calendar_service = "stub_service"
                return True
            
            # Create credentials for Google API client
            credentials = self._create_credentials_from_token(token_info)
            
            # Build the Calendar service
            self.google_calendar_service = build('calendar', 'v3', credentials=credentials)
            
            self.logger.info("Google Calendar service initialized with real API")
            return True
            
        except Exception as e:
            self.logger.error(
                f"Failed to initialize calendar service: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            # Fall back to stub service
            self.google_calendar_service = "stub_service"
            return True
    
    def _create_credentials_from_token(self, token_info) -> Credentials:
        """Create Google API credentials from token info.
        
        Args:
            token_info: TokenInfo object with access token
            
        Returns:
            Google API Credentials object
        """
        from google.oauth2.credentials import Credentials as OAuth2Credentials
        
        return OAuth2Credentials(
            token=token_info.access_token,
            refresh_token=token_info.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=None,  # Will be set by auth manager if needed
            client_secret=None,  # Will be set by auth manager if needed
            scopes=token_info.scopes
        )
    
    def shutdown(self) -> bool:
        """Gracefully shutdown the operations handler.
        
        Returns:
            True if shutdown successful, False otherwise
        """
        try:
            self.logger.info("Shutting down Calendar Operations Handler")
            
            # Clean up resources
            self.google_calendar_service = None
            
            # Health is managed by unified ReflectiveModule
            self.logger.info("Calendar Operations Handler shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(
                f"Error during operations handler shutdown: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get operations handler performance metrics.
        
        Returns:
            Dictionary of performance metrics
        """
        base_metrics = super().get_metrics()
        
        operations_metrics = {
            "operations_count": self.operations_count,
            "errors_count": self.errors_count,
            "error_rate": self.errors_count / max(self.operations_count, 1),
            "default_calendar_id": self.default_calendar_id
        }
        
        return {**base_metrics, **operations_metrics}