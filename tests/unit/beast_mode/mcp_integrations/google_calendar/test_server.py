"""Unit tests for Google Calendar MCP Server."""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from src.beast_mode.mcp_integrations.google_calendar.server import GoogleCalendarMCPServer
from src.beast_mode.mcp_integrations.google_calendar.models import MCPRequest, MCPResponse


class TestGoogleCalendarMCPServer(unittest.TestCase):
    """Test cases for GoogleCalendarMCPServer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "host": "localhost",
            "port": 3001,
            "log_level": "debug"
        }
        self.server = GoogleCalendarMCPServer(self.config)
        
        # Mock dependencies
        self.mock_auth_manager = Mock()
        self.mock_operations_handler = Mock()
        self.mock_error_handler = Mock()
        
        # Set up mocks
        self.server.set_auth_manager(self.mock_auth_manager)
        self.server.set_operations_handler(self.mock_operations_handler)
        self.server.set_error_handler(self.mock_error_handler)
    
    def test_server_initialization(self):
        """Test server initialization."""
        self.assertEqual(self.server.host, "localhost")
        self.assertEqual(self.server.port, 3001)
        self.assertEqual(self.server.module_name, "google_calendar_mcp_server")
        self.assertFalse(self.server.is_running)
    
    def test_dependency_injection(self):
        """Test dependency injection."""
        self.assertIsNotNone(self.server.auth_manager)
        self.assertIsNotNone(self.server.operations_handler)
        self.assertIsNotNone(self.server.error_handler)
    
    def test_initialize_success(self):
        """Test successful server initialization."""
        # Mock successful dependency initialization
        self.mock_auth_manager.initialize.return_value = True
        self.mock_operations_handler.initialize.return_value = True
        
        result = self.server.initialize()
        
        self.assertTrue(result)
        self.mock_auth_manager.initialize.assert_called_once()
        self.mock_operations_handler.initialize.assert_called_once()
    
    def test_initialize_failure(self):
        """Test server initialization failure."""
        # Mock failed auth manager initialization
        self.mock_auth_manager.initialize.return_value = False
        
        result = self.server.initialize()
        
        self.assertFalse(result)
        self.assertEqual(self.server.get_health_status().status, "unhealthy")
    
    def test_start_server(self):
        """Test starting the server."""
        result = self.server.start_server()
        
        self.assertTrue(result)
        self.assertTrue(self.server.is_running)
        self.assertEqual(self.server.get_health_status().status, "healthy")
    
    def test_stop_server(self):
        """Test stopping the server."""
        # Start server first
        self.server.start_server()
        
        result = self.server.stop_server()
        
        self.assertTrue(result)
        self.assertFalse(self.server.is_running)
    
    def test_handle_auth_status_request(self):
        """Test handling auth status request."""
        # Mock authentication status
        self.mock_auth_manager.is_authenticated.return_value = True
        self.mock_auth_manager.get_access_token.return_value = "test_token"
        
        request_data = {
            "method": "auth.status",
            "params": {},
            "id": "test_request_1"
        }
        
        response = self.server.handle_mcp_request(request_data)
        
        self.assertEqual(response["id"], "test_request_1")
        self.assertIsNone(response["error"])
        self.assertTrue(response["result"]["authenticated"])
        self.assertTrue(response["result"]["token_valid"])
    
    def test_handle_auth_authenticate_request(self):
        """Test handling authentication request."""
        # Mock successful authentication
        self.mock_auth_manager.authenticate.return_value = True
        
        request_data = {
            "method": "auth.authenticate",
            "params": {},
            "id": "test_request_2"
        }
        
        response = self.server.handle_mcp_request(request_data)
        
        self.assertEqual(response["id"], "test_request_2")
        self.assertIsNone(response["error"])
        self.assertTrue(response["result"]["success"])
        self.mock_auth_manager.authenticate.assert_called_once()
    
    def test_handle_get_events_request(self):
        """Test handling get events request."""
        # Mock events data
        mock_events = [
            {
                "id": "event_1",
                "summary": "Test Event",
                "start_time": "2024-01-01T10:00:00Z",
                "end_time": "2024-01-01T11:00:00Z"
            }
        ]
        self.mock_operations_handler.get_events.return_value = mock_events
        
        request_data = {
            "method": "calendar.get_events",
            "params": {
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-01T23:59:59Z"
            },
            "id": "test_request_3"
        }
        
        response = self.server.handle_mcp_request(request_data)
        
        self.assertEqual(response["id"], "test_request_3")
        self.assertIsNone(response["error"])
        self.assertEqual(len(response["result"]["events"]), 1)
        self.assertEqual(response["result"]["events"][0]["id"], "event_1")
    
    def test_handle_create_event_request(self):
        """Test handling create event request."""
        # Mock created event
        mock_event = {
            "id": "created_event_1",
            "summary": "New Meeting",
            "start_time": "2024-01-01T14:00:00Z",
            "end_time": "2024-01-01T15:00:00Z"
        }
        self.mock_operations_handler.create_event.return_value = mock_event
        
        request_data = {
            "method": "calendar.create_event",
            "params": {
                "event_data": {
                    "summary": "New Meeting",
                    "start_time": "2024-01-01T14:00:00Z",
                    "end_time": "2024-01-01T15:00:00Z"
                }
            },
            "id": "test_request_4"
        }
        
        response = self.server.handle_mcp_request(request_data)
        
        self.assertEqual(response["id"], "test_request_4")
        self.assertIsNone(response["error"])
        self.assertEqual(response["result"]["event"]["id"], "created_event_1")
    
    def test_handle_health_status_request(self):
        """Test handling health status request."""
        request_data = {
            "method": "health.status",
            "params": {},
            "id": "test_request_5"
        }
        
        response = self.server.handle_mcp_request(request_data)
        
        self.assertEqual(response["id"], "test_request_5")
        self.assertIsNone(response["error"])
        self.assertIn("module_name", response["result"])
        self.assertIn("status", response["result"])
    
    def test_handle_unknown_method(self):
        """Test handling unknown method request."""
        request_data = {
            "method": "unknown.method",
            "params": {},
            "id": "test_request_6"
        }
        
        response = self.server.handle_mcp_request(request_data)
        
        self.assertEqual(response["id"], "test_request_6")
        self.assertIsNotNone(response["error"])
        self.assertEqual(response["error"]["code"], -32601)
        self.assertEqual(response["error"]["message"], "Method not found")
    
    def test_handle_malformed_request(self):
        """Test handling malformed request."""
        request_data = {
            "invalid": "request"
        }
        
        response = self.server.handle_mcp_request(request_data)
        
        self.assertIsNotNone(response["error"])
        self.assertEqual(response["error"]["code"], -32700)
        self.assertEqual(response["error"]["message"], "Parse error")
    
    def test_request_counting(self):
        """Test request counting metrics."""
        initial_count = self.server.request_count
        
        # Make a request
        request_data = {
            "method": "health.status",
            "params": {},
            "id": "test_count"
        }
        
        self.server.handle_mcp_request(request_data)
        
        self.assertEqual(self.server.request_count, initial_count + 1)
    
    def test_error_counting(self):
        """Test error counting metrics."""
        initial_error_count = self.server.error_count
        
        # Make a request that will cause an error
        self.mock_operations_handler.get_events.side_effect = Exception("Test error")
        
        request_data = {
            "method": "calendar.get_events",
            "params": {
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-01T23:59:59Z"
            },
            "id": "test_error"
        }
        
        response = self.server.handle_mcp_request(request_data)
        
        self.assertEqual(self.server.error_count, initial_error_count + 1)
        self.assertIsNotNone(response["error"])
    
    def test_get_metrics(self):
        """Test getting server metrics."""
        metrics = self.server.get_metrics()
        
        self.assertIn("module_name", metrics)
        self.assertIn("request_count", metrics)
        self.assertIn("error_count", metrics)
        self.assertIn("error_rate", metrics)
        self.assertIn("is_running", metrics)
        self.assertIn("host", metrics)
        self.assertIn("port", metrics)
    
    def test_shutdown(self):
        """Test server shutdown."""
        # Start server first
        self.server.start_server()
        
        # Mock dependency shutdown
        self.mock_auth_manager.shutdown.return_value = True
        self.mock_operations_handler.shutdown.return_value = True
        
        result = self.server.shutdown()
        
        self.assertTrue(result)
        self.assertFalse(self.server.is_running)
        self.mock_auth_manager.shutdown.assert_called_once()
        self.mock_operations_handler.shutdown.assert_called_once()


if __name__ == "__main__":
    unittest.main()