"""
Comprehensive unit tests for the Observatory Web Interface system.

Tests FastAPI web server, WebSocket endpoints, emoji rain dashboard,
and real-time monitoring capabilities.
"""

import asyncio
import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import Dict, Any

from src.beast_mode.observatory.models import (
    ObservatoryConfig,
    WebSocketConfig,
    WebInterfaceConfig,
    GamificationConfig,
    CoordinationEvent,
    CoordinationEventType
)

# Handle optional FastAPI dependency
try:
    from fastapi.testclient import TestClient
    from src.beast_mode.observatory.web_interface import (
        ObservatoryWebInterface,
        create_dashboard_html,
        FASTAPI_AVAILABLE
    )
    FASTAPI_TEST_AVAILABLE = True
except ImportError:
    FASTAPI_TEST_AVAILABLE = False
    TestClient = None


@pytest.fixture
def web_interface_config():
    """Sample web interface configuration."""
    return WebInterfaceConfig(
        title="Test Observatory Dashboard",
        theme="dark",
        refresh_rate_ms=1000
    )


@pytest.fixture
def websocket_config():
    """Sample WebSocket configuration."""
    return WebSocketConfig(
        host="localhost",
        port=8080,
        max_connections=100,
        heartbeat_interval=30
    )


@pytest.fixture
def gamification_config():
    """Sample gamification configuration."""
    return GamificationConfig(
        emoji_rain_enabled=True,
        achievements_enabled=True,
        celebration_effects_enabled=True
    )


@pytest.fixture
def observatory_config(web_interface_config, websocket_config, gamification_config):
    """Sample observatory configuration."""
    return ObservatoryConfig(
        web_interface_config=web_interface_config,
        websocket_config=websocket_config,
        gamification_config=gamification_config
    )


@pytest.fixture
def mock_emoji_engine():
    """Mock emoji rain engine."""
    mock_engine = AsyncMock()
    mock_engine._running = True
    mock_engine._active_effects = []
    mock_engine.start_animation_loop = AsyncMock()
    mock_engine.stop_animation_loop = AsyncMock()
    mock_engine.trigger_event_rain = AsyncMock(return_value="effect-123")
    mock_engine.set_canvas_size = MagicMock()
    mock_engine.get_performance_stats = MagicMock(return_value={
        "active_effects": 2,
        "total_particles": 150,
        "target_fps": 60,
        "average_fps": 58.5
    })
    mock_engine.get_active_effects = MagicMock(return_value=[
        {"id": "effect-1", "type": "celebration"},
        {"id": "effect-2", "type": "milestone"}
    ])
    return mock_engine


@pytest.fixture
def mock_templates_dir(tmp_path):
    """Create temporary templates directory."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    return templates_dir


@pytest.fixture
def mock_static_dir(tmp_path):
    """Create temporary static directory."""
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    return static_dir


@pytest.mark.skipif(not FASTAPI_TEST_AVAILABLE, reason="FastAPI not available")
class TestObservatoryWebInterfaceInitialization:
    """Test ObservatoryWebInterface initialization."""

    def test_web_interface_creation_fastapi_available(self, observatory_config, mock_emoji_engine):
        """Test web interface creation when FastAPI is available."""
        with patch('src.beast_mode.observatory.web_interface.FASTAPI_AVAILABLE', True):
            with patch('pathlib.Path.mkdir'):
                interface = ObservatoryWebInterface(observatory_config, mock_emoji_engine)

                assert interface.config == observatory_config
                assert interface.emoji_engine == mock_emoji_engine
                assert interface.app is not None
                assert interface.emoji_ws_handler is not None

    def test_web_interface_creation_fastapi_unavailable(self, observatory_config, mock_emoji_engine):
        """Test web interface creation when FastAPI is unavailable."""
        with patch('src.beast_mode.observatory.web_interface.FASTAPI_AVAILABLE', False):
            with pytest.raises(ImportError, match="FastAPI is required"):
                ObservatoryWebInterface(observatory_config, mock_emoji_engine)

    def test_web_interface_directory_creation(self, observatory_config, mock_emoji_engine, tmp_path):
        """Test that templates and static directories are created."""
        with patch('pathlib.Path.__truediv__') as mock_div:
            # Mock the path operations
            mock_templates_path = MagicMock()
            mock_static_path = MagicMock()
            mock_div.side_effect = lambda x: mock_templates_path if 'templates' in str(x) else mock_static_path

            with patch('src.beast_mode.observatory.web_interface.FASTAPI_AVAILABLE', True):
                interface = ObservatoryWebInterface(observatory_config, mock_emoji_engine)

                # Check that mkdir was called for both directories
                mock_templates_path.mkdir.assert_called_once_with(exist_ok=True)
                mock_static_path.mkdir.assert_called_once_with(exist_ok=True)


@pytest.mark.skipif(not FASTAPI_TEST_AVAILABLE, reason="FastAPI not available")
class TestWebInterfaceRoutes:
    """Test HTTP route functionality."""

    @pytest.fixture
    def web_interface(self, observatory_config, mock_emoji_engine):
        """Create web interface for testing."""
        with patch('pathlib.Path.mkdir'):
            return ObservatoryWebInterface(observatory_config, mock_emoji_engine)

    @pytest.fixture
    def client(self, web_interface):
        """Create test client."""
        return TestClient(web_interface.app)

    def test_health_check_route(self, client, mock_emoji_engine):
        """Test health check endpoint."""
        # Mock WebSocket handler
        mock_ws_handler = MagicMock()
        mock_ws_handler.connected_clients = ["client1", "client2"]

        with patch.object(client.app, 'emoji_ws_handler', mock_ws_handler):
            response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["emoji_rain_active"] is True
        assert data["active_effects"] == 0  # Empty list
        assert data["connected_clients"] == 2

    def test_emoji_rain_stats_route(self, client, web_interface):
        """Test emoji rain stats endpoint."""
        response = client.get("/api/emoji-rain/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["active_effects"] == 2
        assert data["total_particles"] == 150
        assert data["target_fps"] == 60
        assert data["average_fps"] == 58.5

    def test_active_effects_route(self, client, web_interface):
        """Test active effects endpoint."""
        response = client.get("/api/emoji-rain/effects")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2
        assert data[0]["id"] == "effect-1"
        assert data[0]["type"] == "celebration"
        assert data[1]["id"] == "effect-2"
        assert data[1]["type"] == "milestone"

    def test_trigger_emoji_rain_route_success(self, client, web_interface):
        """Test manual emoji rain trigger endpoint - success case."""
        trigger_data = {
            "event_type": "TASK_COMPLETED",
            "data": {
                "task_id": "test-task-123",
                "user": "test-user"
            }
        }

        response = client.post("/api/emoji-rain/trigger", json=trigger_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["effect_id"] == "effect-123"
        assert data["event_type"] == "TASK_COMPLETED"

        # Verify emoji engine was called
        web_interface.emoji_engine.trigger_event_rain.assert_called_once()

    def test_trigger_emoji_rain_route_invalid_event_type(self, client, web_interface):
        """Test manual emoji rain trigger with invalid event type."""
        trigger_data = {
            "event_type": "INVALID_EVENT_TYPE",
            "data": {}
        }

        response = client.post("/api/emoji-rain/trigger", json=trigger_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is False
        assert "error" in data

    def test_trigger_emoji_rain_route_engine_error(self, client, web_interface):
        """Test manual emoji rain trigger when engine throws error."""
        web_interface.emoji_engine.trigger_event_rain.side_effect = Exception("Engine error")

        trigger_data = {
            "event_type": "TASK_COMPLETED",
            "data": {}
        }

        response = client.post("/api/emoji-rain/trigger", json=trigger_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is False
        assert data["error"] == "Engine error"

    def test_trigger_emoji_rain_route_default_event_type(self, client, web_interface):
        """Test manual emoji rain trigger with default event type."""
        trigger_data = {
            "data": {"source": "test"}
        }

        response = client.post("/api/emoji-rain/trigger", json=trigger_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["event_type"] == "TASK_COMPLETED"  # Default


@pytest.mark.skipif(not FASTAPI_TEST_AVAILABLE, reason="FastAPI not available")
class TestWebSocketHandling:
    """Test WebSocket functionality."""

    @pytest.fixture
    def web_interface(self, observatory_config, mock_emoji_engine):
        """Create web interface for testing."""
        with patch('pathlib.Path.mkdir'):
            return ObservatoryWebInterface(observatory_config, mock_emoji_engine)

    @pytest.mark.asyncio
    async def test_websocket_message_handling_ping(self, web_interface):
        """Test handling of ping WebSocket messages."""
        mock_websocket = AsyncMock()
        ping_message = {"type": "ping"}

        await web_interface._handle_websocket_message(mock_websocket, ping_message)

        mock_websocket.send_text.assert_called_once()
        sent_data = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_data["type"] == "pong"

    @pytest.mark.asyncio
    async def test_websocket_message_handling_trigger_test_rain(self, web_interface):
        """Test handling of trigger test rain WebSocket messages."""
        mock_websocket = AsyncMock()
        test_rain_message = {
            "type": "trigger_test_rain",
            "event_type": "ACHIEVEMENT_UNLOCKED",
            "data": {"achievement": "first_task"}
        }

        await web_interface._handle_websocket_message(mock_websocket, test_rain_message)

        # Verify emoji engine was triggered
        web_interface.emoji_engine.trigger_event_rain.assert_called_once()
        call_args = web_interface.emoji_engine.trigger_event_rain.call_args[0][0]
        assert call_args.event_type == CoordinationEventType.ACHIEVEMENT_UNLOCKED
        assert call_args.source_component == "websocket_test"
        assert call_args.event_data == {"achievement": "first_task"}

        # Verify response was sent
        mock_websocket.send_text.assert_called_once()
        sent_data = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_data["type"] == "test_rain_triggered"
        assert sent_data["data"]["success"] is True
        assert sent_data["data"]["effect_id"] == "effect-123"

    @pytest.mark.asyncio
    async def test_websocket_message_handling_trigger_test_rain_error(self, web_interface):
        """Test handling of trigger test rain WebSocket messages with error."""
        web_interface.emoji_engine.trigger_event_rain.side_effect = Exception("Test error")

        mock_websocket = AsyncMock()
        test_rain_message = {
            "type": "trigger_test_rain",
            "event_type": "TASK_COMPLETED"
        }

        await web_interface._handle_websocket_message(mock_websocket, test_rain_message)

        # Verify error response was sent
        mock_websocket.send_text.assert_called_once()
        sent_data = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_data["type"] == "test_rain_triggered"
        assert sent_data["data"]["success"] is False
        assert sent_data["data"]["error"] == "Test error"

    @pytest.mark.asyncio
    async def test_websocket_message_handling_set_canvas_size(self, web_interface):
        """Test handling of canvas size WebSocket messages."""
        mock_websocket = AsyncMock()
        canvas_message = {
            "type": "set_canvas_size",
            "width": 1920,
            "height": 1080
        }

        await web_interface._handle_websocket_message(mock_websocket, canvas_message)

        # Verify emoji engine canvas size was set
        web_interface.emoji_engine.set_canvas_size.assert_called_once_with(1920, 1080)

    @pytest.mark.asyncio
    async def test_websocket_message_handling_set_canvas_size_defaults(self, web_interface):
        """Test handling of canvas size WebSocket messages with defaults."""
        mock_websocket = AsyncMock()
        canvas_message = {
            "type": "set_canvas_size"
            # No width/height provided
        }

        await web_interface._handle_websocket_message(mock_websocket, canvas_message)

        # Verify default values were used
        web_interface.emoji_engine.set_canvas_size.assert_called_once_with(1920, 1080)

    @pytest.mark.asyncio
    async def test_websocket_message_handling_trigger_test_rain_default_event(self, web_interface):
        """Test handling of trigger test rain with default event type."""
        mock_websocket = AsyncMock()
        test_rain_message = {
            "type": "trigger_test_rain"
            # No event_type provided
        }

        await web_interface._handle_websocket_message(mock_websocket, test_rain_message)

        # Verify default event type was used
        call_args = web_interface.emoji_engine.trigger_event_rain.call_args[0][0]
        assert call_args.event_type == CoordinationEventType.TASK_COMPLETED

    @pytest.mark.asyncio
    async def test_websocket_message_handling_unknown_type(self, web_interface):
        """Test handling of unknown WebSocket message types."""
        mock_websocket = AsyncMock()
        unknown_message = {
            "type": "unknown_message_type",
            "data": "test"
        }

        # Should not raise exception
        await web_interface._handle_websocket_message(mock_websocket, unknown_message)

        # Should not send any response
        mock_websocket.send_text.assert_not_called()


@pytest.mark.skipif(not FASTAPI_TEST_AVAILABLE, reason="FastAPI not available")
class TestServerLifecycle:
    """Test server lifecycle management."""

    @pytest.fixture
    def web_interface(self, observatory_config, mock_emoji_engine):
        """Create web interface for testing."""
        with patch('pathlib.Path.mkdir'):
            return ObservatoryWebInterface(observatory_config, mock_emoji_engine)

    @pytest.mark.asyncio
    async def test_start_server(self, web_interface):
        """Test starting the web server."""
        await web_interface.start_server()

        # Verify emoji engine animation loop was started
        web_interface.emoji_engine.start_animation_loop.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_server(self, web_interface):
        """Test stopping the web server."""
        await web_interface.stop_server()

        # Verify emoji engine animation loop was stopped
        web_interface.emoji_engine.stop_animation_loop.assert_called_once()


class TestDashboardHTML:
    """Test dashboard HTML template generation."""

    def test_create_dashboard_html_returns_string(self):
        """Test that create_dashboard_html returns a string."""
        html = create_dashboard_html()

        assert isinstance(html, str)
        assert len(html) > 0

    def test_dashboard_html_contains_required_elements(self):
        """Test that dashboard HTML contains required elements."""
        html = create_dashboard_html()

        # Check for key HTML elements
        assert '<!DOCTYPE html>' in html
        assert '<canvas id="emoji-rain-canvas">' in html
        assert 'class="btn btn-primary"' in html
        assert 'triggerRain(' in html
        assert 'EmojiRainRenderer' in html
        assert '/ws/emoji-rain' in html

    def test_dashboard_html_template_variables(self):
        """Test that dashboard HTML contains Jinja2 template variables."""
        html = create_dashboard_html()

        # Check for template variables
        assert '{{ title }}' in html
        assert '{{ theme }}' in html
        assert '{% if theme == \'dark\' %}' in html
        assert '{{ refresh_rate }}' in html

    def test_dashboard_html_javascript_functionality(self):
        """Test that dashboard HTML contains required JavaScript functionality."""
        html = create_dashboard_html()

        # Check for key JavaScript functionality
        assert 'class EmojiRainRenderer' in html
        assert 'connectWebSocket()' in html
        assert 'handleWebSocketMessage' in html
        assert 'updateParticles' in html
        assert 'renderFrame()' in html
        assert 'triggerRain(' in html

    def test_dashboard_html_css_styling(self):
        """Test that dashboard HTML contains CSS styling."""
        html = create_dashboard_html()

        # Check for key CSS classes and styling
        assert '.emoji-rain-canvas' in html or '#emoji-rain-canvas' in html
        assert '.dashboard-container' in html
        assert '.btn' in html
        assert '.stat-card' in html
        assert '.connection-status' in html
        assert 'animation:' in html or '@keyframes' in html


class TestWebInterfaceEdgeCases:
    """Test edge cases and error handling."""

    def test_import_error_handling(self):
        """Test that import error is handled gracefully."""
        # This test verifies that the module can be imported even when FastAPI is not available
        with patch('src.beast_mode.observatory.web_interface.FASTAPI_AVAILABLE', False):
            from src.beast_mode.observatory.web_interface import FASTAPI_AVAILABLE
            assert FASTAPI_AVAILABLE is False

    @pytest.mark.skipif(not FASTAPI_TEST_AVAILABLE, reason="FastAPI not available")
    def test_web_interface_with_minimal_config(self, mock_emoji_engine):
        """Test web interface with minimal configuration."""
        minimal_config = ObservatoryConfig()

        with patch('pathlib.Path.mkdir'):
            interface = ObservatoryWebInterface(minimal_config, mock_emoji_engine)

        assert interface.config == minimal_config
        assert interface.emoji_engine == mock_emoji_engine

    @pytest.mark.skipif(not FASTAPI_TEST_AVAILABLE, reason="FastAPI not available")
    @pytest.mark.asyncio
    async def test_websocket_message_with_missing_fields(self, observatory_config, mock_emoji_engine):
        """Test WebSocket message handling with missing required fields."""
        with patch('pathlib.Path.mkdir'):
            interface = ObservatoryWebInterface(observatory_config, mock_emoji_engine)

        mock_websocket = AsyncMock()

        # Message with missing fields
        incomplete_message = {
            "type": "trigger_test_rain"
            # Missing event_type and data
        }

        # Should handle gracefully without raising exception
        await interface._handle_websocket_message(mock_websocket, incomplete_message)

        # Should still trigger emoji rain with defaults
        interface.emoji_engine.trigger_event_rain.assert_called_once()

    @pytest.mark.skipif(not FASTAPI_TEST_AVAILABLE, reason="FastAPI not available")
    def test_web_interface_route_setup_verification(self, observatory_config, mock_emoji_engine):
        """Test that all expected routes are properly set up."""
        with patch('pathlib.Path.mkdir'):
            interface = ObservatoryWebInterface(observatory_config, mock_emoji_engine)

        # Get all routes from the FastAPI app
        routes = [route.path for route in interface.app.routes]

        # Check that expected routes exist
        expected_routes = [
            "/",
            "/health",
            "/api/emoji-rain/stats",
            "/api/emoji-rain/effects",
            "/api/emoji-rain/trigger"
        ]

        for expected_route in expected_routes:
            assert expected_route in routes, f"Expected route {expected_route} not found"

    @pytest.mark.skipif(not FASTAPI_TEST_AVAILABLE, reason="FastAPI not available")
    def test_emoji_ws_handler_initialization(self, observatory_config, mock_emoji_engine):
        """Test that emoji WebSocket handler is properly initialized."""
        with patch('pathlib.Path.mkdir'):
            with patch('src.beast_mode.observatory.web_interface.EmojiRainWebSocketHandler') as mock_handler_class:
                mock_handler = MagicMock()
                mock_handler_class.return_value = mock_handler

                interface = ObservatoryWebInterface(observatory_config, mock_emoji_engine)

                # Verify handler was created with emoji engine
                mock_handler_class.assert_called_once_with(mock_emoji_engine)
                assert interface.emoji_ws_handler == mock_handler


@pytest.mark.skipif(not FASTAPI_TEST_AVAILABLE, reason="FastAPI not available")
class TestWebInterfaceIntegration:
    """Test integration scenarios for the web interface."""

    @pytest.fixture
    def web_interface(self, observatory_config, mock_emoji_engine):
        """Create web interface for testing."""
        with patch('pathlib.Path.mkdir'):
            return ObservatoryWebInterface(observatory_config, mock_emoji_engine)

    @pytest.fixture
    def client(self, web_interface):
        """Create test client."""
        return TestClient(web_interface.app)

    def test_full_emoji_rain_trigger_flow(self, client, web_interface):
        """Test complete flow from HTTP trigger to emoji engine."""
        # Trigger emoji rain via HTTP API
        trigger_data = {
            "event_type": "COORDINATION_MILESTONE",
            "data": {
                "milestone": "10_tasks_completed",
                "team": "development"
            }
        }

        response = client.post("/api/emoji-rain/trigger", json=trigger_data)

        # Verify HTTP response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["effect_id"] == "effect-123"

        # Verify emoji engine was called with correct event
        web_interface.emoji_engine.trigger_event_rain.assert_called_once()
        event_arg = web_interface.emoji_engine.trigger_event_rain.call_args[0][0]

        assert event_arg.event_type == CoordinationEventType.COORDINATION_MILESTONE
        assert event_arg.source_component == "web_interface_test"
        assert event_arg.event_data["milestone"] == "10_tasks_completed"
        assert event_arg.event_data["team"] == "development"

    def test_stats_integration_with_emoji_engine(self, client, web_interface):
        """Test that stats endpoints properly integrate with emoji engine."""
        # Mock emoji engine to return specific stats
        web_interface.emoji_engine.get_performance_stats.return_value = {
            "active_effects": 5,
            "total_particles": 250,
            "target_fps": 60,
            "average_fps": 59.2,
            "dropped_frames": 2
        }

        response = client.get("/api/emoji-rain/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["active_effects"] == 5
        assert data["total_particles"] == 250
        assert data["target_fps"] == 60
        assert data["average_fps"] == 59.2
        assert data["dropped_frames"] == 2

        # Verify engine method was called
        web_interface.emoji_engine.get_performance_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_websocket_emoji_engine_integration(self, web_interface):
        """Test WebSocket integration with emoji engine."""
        mock_websocket = AsyncMock()

        # Simulate canvas size update
        canvas_message = {
            "type": "set_canvas_size",
            "width": 2560,
            "height": 1440
        }

        await web_interface._handle_websocket_message(mock_websocket, canvas_message)

        # Verify emoji engine canvas was updated
        web_interface.emoji_engine.set_canvas_size.assert_called_once_with(2560, 1440)

        # Simulate emoji rain trigger
        rain_message = {
            "type": "trigger_test_rain",
            "event_type": "API_CALL_SUCCESS",
            "data": {"api": "user_registration", "latency_ms": 45}
        }

        await web_interface._handle_websocket_message(mock_websocket, rain_message)

        # Verify emoji engine was triggered
        assert web_interface.emoji_engine.trigger_event_rain.call_count == 1
        event_arg = web_interface.emoji_engine.trigger_event_rain.call_args[0][0]
        assert event_arg.event_type == CoordinationEventType.API_CALL_SUCCESS
        assert event_arg.event_data["api"] == "user_registration"