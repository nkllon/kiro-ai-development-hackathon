"""Unit tests for Google Calendar MCP integration data models."""

import unittest
from datetime import datetime, timedelta
from uuid import UUID

from src.beast_mode.mcp_integrations.google_calendar.models import (
    CalendarEvent,
    EventData,
    AuthResult,
    TokenInfo,
    MCPRequest,
    MCPResponse,
    MCPError,
    AvailabilityResult,
    ModuleHealth,
    Attendee,
    RecurrenceRule,
    EventStatus,
    AttendeeStatus
)


class TestCalendarEvent(unittest.TestCase):
    """Test cases for CalendarEvent model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.start_time = datetime.utcnow()
        self.end_time = self.start_time + timedelta(hours=1)
    
    def test_calendar_event_creation(self):
        """Test creating a calendar event."""
        event = CalendarEvent(
            id="test_event_1",
            summary="Test Meeting",
            start_time=self.start_time,
            end_time=self.end_time,
            description="A test meeting",
            location="Conference Room A"
        )
        
        self.assertEqual(event.id, "test_event_1")
        self.assertEqual(event.summary, "Test Meeting")
        self.assertEqual(event.start_time, self.start_time)
        self.assertEqual(event.end_time, self.end_time)
        self.assertEqual(event.description, "A test meeting")
        self.assertEqual(event.location, "Conference Room A")
        self.assertEqual(event.status, EventStatus.CONFIRMED)
        self.assertEqual(event.calendar_id, "primary")
    
    def test_calendar_event_validation(self):
        """Test calendar event validation."""
        # Test invalid time range (start >= end)
        with self.assertRaises(ValueError):
            CalendarEvent(
                id="invalid_event",
                summary="Invalid Event",
                start_time=self.end_time,
                end_time=self.start_time
            )
    
    def test_calendar_event_with_attendees(self):
        """Test calendar event with attendees."""
        attendees = [
            Attendee(email="user1@example.com", display_name="User One"),
            Attendee(email="user2@example.com", response_status=AttendeeStatus.ACCEPTED)
        ]
        
        event = CalendarEvent(
            id="event_with_attendees",
            summary="Team Meeting",
            start_time=self.start_time,
            end_time=self.end_time,
            attendees=attendees
        )
        
        self.assertEqual(len(event.attendees), 2)
        self.assertEqual(event.attendees[0].email, "user1@example.com")
        self.assertEqual(event.attendees[1].response_status, AttendeeStatus.ACCEPTED)


class TestEventData(unittest.TestCase):
    """Test cases for EventData model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.start_time = datetime.utcnow()
        self.end_time = self.start_time + timedelta(hours=1)
    
    def test_event_data_creation(self):
        """Test creating event data."""
        event_data = EventData(
            summary="New Meeting",
            start_time=self.start_time,
            end_time=self.end_time,
            description="A new meeting",
            attendees=["user1@example.com", "user2@example.com"]
        )
        
        self.assertEqual(event_data.summary, "New Meeting")
        self.assertEqual(len(event_data.attendees), 2)
    
    def test_event_data_to_calendar_event(self):
        """Test converting EventData to CalendarEvent."""
        event_data = EventData(
            summary="Convert Test",
            start_time=self.start_time,
            end_time=self.end_time,
            attendees=["user@example.com"]
        )
        
        calendar_event = event_data.to_calendar_event("test_id")
        
        self.assertEqual(calendar_event.id, "test_id")
        self.assertEqual(calendar_event.summary, "Convert Test")
        self.assertEqual(len(calendar_event.attendees), 1)
        self.assertEqual(calendar_event.attendees[0].email, "user@example.com")


class TestAuthResult(unittest.TestCase):
    """Test cases for AuthResult model."""
    
    def test_successful_auth_result(self):
        """Test successful authentication result."""
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        auth_result = AuthResult(
            success=True,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_at=expires_at,
            scopes=["calendar", "calendar.events"]
        )
        
        self.assertTrue(auth_result.success)
        self.assertEqual(auth_result.access_token, "test_access_token")
        self.assertEqual(len(auth_result.scopes), 2)
    
    def test_failed_auth_result(self):
        """Test failed authentication result."""
        auth_result = AuthResult(
            success=False,
            error_message="Invalid credentials"
        )
        
        self.assertFalse(auth_result.success)
        self.assertEqual(auth_result.error_message, "Invalid credentials")
        self.assertIsNone(auth_result.access_token)


class TestTokenInfo(unittest.TestCase):
    """Test cases for TokenInfo model."""
    
    def test_token_info_creation(self):
        """Test creating token info."""
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        token_info = TokenInfo(
            access_token="access_token",
            refresh_token="refresh_token",
            expires_at=expires_at,
            scopes=["calendar"]
        )
        
        self.assertEqual(token_info.access_token, "access_token")
        self.assertFalse(token_info.is_expired)
    
    def test_token_expiration(self):
        """Test token expiration check."""
        # Expired token
        expired_token = TokenInfo(
            access_token="expired_token",
            refresh_token="refresh_token",
            expires_at=datetime.utcnow() - timedelta(hours=1),
            scopes=["calendar"]
        )
        
        self.assertTrue(expired_token.is_expired)


class TestMCPModels(unittest.TestCase):
    """Test cases for MCP protocol models."""
    
    def test_mcp_request_creation(self):
        """Test creating MCP request."""
        request = MCPRequest(
            method="calendar.get_events",
            params={"start_time": "2024-01-01T00:00:00Z"}
        )
        
        self.assertEqual(request.method, "calendar.get_events")
        self.assertEqual(request.jsonrpc, "2.0")
        self.assertIsNotNone(request.id)
        
        # Verify ID is a valid UUID
        UUID(request.id)  # Should not raise exception
    
    def test_mcp_response_with_result(self):
        """Test creating MCP response with result."""
        response = MCPResponse(
            result={"events": []},
            id="test_request_id"
        )
        
        self.assertEqual(response.result, {"events": []})
        self.assertIsNone(response.error)
        self.assertEqual(response.id, "test_request_id")
    
    def test_mcp_response_with_error(self):
        """Test creating MCP response with error."""
        error = MCPError(
            code=-32601,
            message="Method not found",
            data={"method": "invalid_method"}
        )
        
        response = MCPResponse(
            error=error,
            id="test_request_id"
        )
        
        self.assertIsNone(response.result)
        self.assertEqual(response.error.code, -32601)
        self.assertEqual(response.error.message, "Method not found")
    
    def test_mcp_response_validation(self):
        """Test MCP response validation."""
        # Response with neither result nor error should raise ValueError
        with self.assertRaises(ValueError):
            MCPResponse(id="test_id")
        
        # Response with both result and error should raise ValueError
        error = MCPError(code=-1, message="Test error")
        with self.assertRaises(ValueError):
            MCPResponse(result={"test": "data"}, error=error, id="test_id")


class TestAvailabilityResult(unittest.TestCase):
    """Test cases for AvailabilityResult model."""
    
    def test_availability_result_creation(self):
        """Test creating availability result."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=1)
        
        availability = AvailabilityResult(
            start_time=start_time,
            end_time=end_time,
            is_available=True,
            free_slots=[(start_time, end_time)]
        )
        
        self.assertTrue(availability.is_available)
        self.assertEqual(len(availability.free_slots), 1)
        self.assertEqual(len(availability.conflicting_events), 0)


class TestModuleHealth(unittest.TestCase):
    """Test cases for ModuleHealth model."""
    
    def test_module_health_creation(self):
        """Test creating module health status."""
        health = ModuleHealth(
            module_name="test_module",
            status="healthy",
            timestamp=datetime.utcnow(),
            details={"version": "1.0.0"},
            dependencies={"auth": "healthy", "api": "degraded"}
        )
        
        self.assertEqual(health.module_name, "test_module")
        self.assertTrue(health.is_healthy)
        self.assertEqual(health.dependencies["auth"], "healthy")
    
    def test_module_health_status_check(self):
        """Test module health status checking."""
        healthy = ModuleHealth(
            module_name="healthy_module",
            status="healthy",
            timestamp=datetime.utcnow()
        )
        
        unhealthy = ModuleHealth(
            module_name="unhealthy_module",
            status="unhealthy",
            timestamp=datetime.utcnow()
        )
        
        self.assertTrue(healthy.is_healthy)
        self.assertFalse(unhealthy.is_healthy)


if __name__ == "__main__":
    unittest.main()