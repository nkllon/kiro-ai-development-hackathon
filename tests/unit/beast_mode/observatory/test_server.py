"""
Unit tests for the Observatory FastAPI Server.

Tests the web server functionality including HTTP endpoints, WebSocket connections,
and integration with the emoji rain system.
"""

import asyncio
import json
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

from src.beast_mode.observatory.server import ObservatoryServer, create_server
from src.beast_mode.observatory.models import (
    ObservatoryConfig,
    CoordinationEventType,
)


class TestObservatoryServer:
    """Test ObservatoryServer functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ObservatoryConfig()
    
    @pytest.fixture
    def server(self, config):
        """Create Observatory server for testing."""
        return ObservatoryServer(config)
    
    @pytest.fixture
    def client(self, server):
        """Create test client."""
        return TestClient(server.app)
    
    def test_server_initialization(self, server, config):
        """Test server initialization."""
        assert server.config == config
        assert server.emoji_engine is not None
        assert server.observatory_core is not None
        assert server.emoji_ws_handler is not None
        assert server.app is not None
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "observatory" in data
        assert "emoji_rain" in data
        
        # Check observatory health structure
        observatory = data["observatory"]
        assert "status" in observatory
        assert "health_score" in observatory
        assert "uptime_seconds" in observatory
        
        # Check emoji rain structure
        emoji_rain = data["emoji_rain"]
        assert "active" in emoji_rain
        assert "active_effects" in emoji_rain
        assert "total_particles" in emoji_rain
        assert "connected_clients" in emoji_rain
    
    def test_observatory_status_endpoint(self, client):
        """Test Observatory status endpoint."""
        response = client.get("/api/observatory/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "health" in data
        assert "metrics" in data
        assert "module_info" in data
        
        # Check health structure
        health = data["health"]
        assert "status" in health
        assert "health_score" in health
        assert "uptime_seconds" in health
        assert "error_count" in health
        assert "warning_count" in health
        assert "issues" in health
    
    def test_emoji_rain_stats_endpoint(self, client):
        """Test emoji rain stats endpoint."""
        response = client.get("/api/emoji-rain/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "active_effects" in data
        assert "total_particles" in data
        assert "target_fps" in data
        assert "canvas_size" in data
        assert "animation_running" in data
        assert "registered_callbacks" in data
    
    def test_active_effects_endpoint(self, client):
        """Test active effects endpoint."""
        response = client.get("/api/emoji-rain/effects")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be empty initially
        assert isinstance(data, dict)
    
    def test_trigger_emoji_rain_endpoint(self, client):
        """Test triggering emoji rain via API."""
        payload = {
            "event_type": "TASK_COMPLETED",
            "data": {"task_id": "test-123"},
            "user_id": "test-user"
        }
        
        response = client.post("/api/emoji-rain/trigger", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "effect_id" in data
        assert data["event_type"] == "TASK_COMPLETED"
        assert "event_id" in data
    
    def test_trigger_emoji_rain_invalid_event_type(self, client):
        """Test triggering emoji rain with invalid event type."""
        payload = {
            "event_type": "INVALID_EVENT_TYPE",
            "data": {}
        }
        
        response = client.post("/api/emoji-rain/trigger", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid event type" in data["detail"]
    
    def test_trigger_achievement_celebration(self, client):
        """Test triggering achievement celebration."""
        payload = {
            "name": "Test Achievement",
            "description": "Test achievement description",
            "icon_emoji": "🏆",
            "user_id": "test-user"
        }
        
        response = client.post("/api/emoji-rain/achievement", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "effect_id" in data
        assert "achievement" in data
        
        achievement = data["achievement"]
        assert achievement["name"] == "Test Achievement"
        assert achievement["description"] == "Test achievement description"
        assert achievement["icon_emoji"] == "🏆"
    
    def test_get_event_types_endpoint(self, client):
        """Test getting available event types."""
        response = client.get("/api/emoji-rain/event-types")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "event_types" in data
        event_types = data["event_types"]
        
        assert len(event_types) > 0
        
        # Check structure of event types
        for event_type in event_types:
            assert "name" in event_type
            assert "description" in event_type
        
        # Check that all CoordinationEventType values are present
        event_names = {et["name"] for et in event_types}
        expected_names = {et.name for et in CoordinationEventType}
        assert event_names == expected_names
    
    def test_dashboard_endpoint(self, client):
        """Test dashboard HTML endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # Check that HTML contains expected elements
        html_content = response.text
        assert "Beast Mode Coordination Observatory" in html_content
        assert "emoji-rain-canvas" in html_content
        assert "WebSocket" in html_content


class TestWebSocketEndpoints:
    """Test WebSocket functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ObservatoryConfig()
    
    @pytest.fixture
    def server(self, config):
        """Create Observatory server for testing."""
        return ObservatoryServer(config)
    
    @pytest.mark.asyncio
    async def test_emoji_rain_websocket_connection(self, server):
        """Test emoji rain WebSocket connection."""
        # Mock WebSocket
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        mock_websocket.receive_text = AsyncMock(side_effect=asyncio.CancelledError())
        
        # Test connection handling
        try:
            # This would normally be called by FastAPI
            await server.emoji_ws_handler.add_client(mock_websocket)
            assert mock_websocket in server.emoji_ws_handler.connected_clients
            
            await server.emoji_ws_handler.remove_client(mock_websocket)
            assert mock_websocket not in server.emoji_ws_handler.connected_clients
            
        except asyncio.CancelledError:
            pass
    
    @pytest.mark.asyncio
    async def test_websocket_message_handling(self, server):
        """Test WebSocket message handling."""
        mock_websocket = AsyncMock(spec=WebSocket)
        
        # Test ping message
        ping_data = {"type": "ping"}
        await server._handle_websocket_message(mock_websocket, ping_data)
        
        # Should send pong response
        mock_websocket.send_text.assert_called_once()
        sent_message = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_message["type"] == "pong"
    
    @pytest.mark.asyncio
    async def test_websocket_trigger_test_rain(self, server):
        """Test triggering test rain via WebSocket."""
        mock_websocket = AsyncMock(spec=WebSocket)
        
        # Test trigger test rain message
        rain_data = {
            "type": "trigger_test_rain",
            "event_type": "TASK_COMPLETED",
            "data": {"test": True}
        }
        
        await server._handle_websocket_message(mock_websocket, rain_data)
        
        # Should send success response
        mock_websocket.send_text.assert_called_once()
        sent_message = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_message["type"] == "test_rain_triggered"
        assert sent_message["data"]["success"] is True
    
    @pytest.mark.asyncio
    async def test_websocket_set_canvas_size(self, server):
        """Test setting canvas size via WebSocket."""
        mock_websocket = AsyncMock(spec=WebSocket)
        
        # Test set canvas size message
        canvas_data = {
            "type": "set_canvas_size",
            "width": 1280,
            "height": 720
        }
        
        await server._handle_websocket_message(mock_websocket, canvas_data)
        
        # Check that canvas size was updated
        assert server.emoji_engine._canvas_width == 1280
        assert server.emoji_engine._canvas_height == 720
    
    @pytest.mark.asyncio
    async def test_websocket_unknown_message_type(self, server):
        """Test handling unknown WebSocket message type."""
        mock_websocket = AsyncMock(spec=WebSocket)
        
        # Test unknown message type
        unknown_data = {"type": "unknown_message_type"}
        
        with patch('src.beast_mode.observatory.server.logger') as mock_logger:
            await server._handle_websocket_message(mock_websocket, unknown_data)
            
            # Should log warning
            mock_logger.warning.assert_called_once()


class TestServerLifecycle:
    """Test server lifecycle management."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ObservatoryConfig()
    
    @pytest.mark.asyncio
    async def test_server_lifespan(self, config):
        """Test server lifespan management."""
        server = ObservatoryServer(config)
        
        # Mock the lifespan context manager
        async with server.lifespan(server.app):
            # During lifespan, components should be running
            assert server.observatory_core._running is True
            assert server.emoji_engine._running is True
        
        # After lifespan, components should be stopped
        assert server.observatory_core._running is False
        assert server.emoji_engine._running is False


class TestServerCreation:
    """Test server creation utilities."""
    
    def test_create_server_default_config(self):
        """Test creating server with default configuration."""
        server = create_server()
        
        assert isinstance(server, ObservatoryServer)
        assert server.config is not None
        assert server.emoji_engine is not None
        assert server.observatory_core is not None
    
    def test_create_server_custom_config(self):
        """Test creating server with custom configuration."""
        # Create a temporary config file
        import tempfile
        import yaml
        
        config_data = {
            "websocket": {"port": 9999},
            "gamification": {"emoji_rain_enabled": False}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            server = create_server(config_path)
            
            assert isinstance(server, ObservatoryServer)
            assert server.config.websocket_config.port == 9999
            assert server.config.gamification_config.emoji_rain_enabled is False
            
        finally:
            import os
            os.unlink(config_path)


class TestMiddleware:
    """Test server middleware."""
    
    @pytest.fixture
    def server(self):
        """Create Observatory server for testing."""
        config = ObservatoryConfig()
        return ObservatoryServer(config)
    
    def test_cors_middleware(self, server):
        """Test CORS middleware is configured."""
        # Check that CORS middleware is in the middleware stack
        middleware_classes = [middleware.cls for middleware in server.app.user_middleware]
        
        from starlette.middleware.cors import CORSMiddleware
        assert CORSMiddleware in middleware_classes


class TestStaticFiles:
    """Test static file serving."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        config = ObservatoryConfig()
        server = ObservatoryServer(config)
        return TestClient(server.app)
    
    def test_static_files_mounted(self, client):
        """Test that static files are properly mounted."""
        # Try to access a non-existent static file
        response = client.get("/static/nonexistent.css")
        
        # Should return 404, not 500, indicating static files are mounted
        assert response.status_code == 404


class TestErrorHandling:
    """Test error handling in server endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        config = ObservatoryConfig()
        server = ObservatoryServer(config)
        return TestClient(server.app)
    
    def test_trigger_rain_with_malformed_json(self, client):
        """Test triggering rain with malformed JSON."""
        response = client.post(
            "/api/emoji-rain/trigger",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_achievement_with_missing_fields(self, client):
        """Test achievement endpoint with missing fields."""
        # Should work with defaults
        response = client.post("/api/emoji-rain/achievement", json={})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["achievement"]["name"] == "API Achievement"