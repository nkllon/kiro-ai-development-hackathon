"""Comprehensive tests for WebSocket heartbeat mechanism."""

import asyncio
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.beast_mode.observatory.websocket.heartbeat import (
    WebSocketHeartbeat,
    HeartbeatConfig,
    HeartbeatStatus,
    HeartbeatMetrics,
    HeartbeatEvent,
)
from src.beast_mode.observatory.websocket.connection import WebSocketConnection
from src.beast_mode.observatory.websocket.exceptions import (
    ConnectionTimeoutError,
    ConnectionFailedError,
)


class TestHeartbeatConfig:
    """Test heartbeat configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = HeartbeatConfig()
        
        assert config.ping_interval == 30.0
        assert config.pong_timeout == 90.0
        assert config.max_retries == 3
        assert config.backoff_base == 2.0
        assert config.max_backoff == 300.0
        assert config.jitter_range == 0.1
        assert config.health_check_interval == 60.0
        assert config.connection_timeout == 10.0
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = HeartbeatConfig(
            ping_interval=15.0,
            pong_timeout=45.0,
            max_retries=5,
            backoff_base=1.5,
            max_backoff=600.0,
            jitter_range=0.2,
            health_check_interval=30.0,
            connection_timeout=5.0
        )
        
        assert config.ping_interval == 15.0
        assert config.pong_timeout == 45.0
        assert config.max_retries == 5
        assert config.backoff_base == 1.5
        assert config.max_backoff == 600.0
        assert config.jitter_range == 0.2
        assert config.health_check_interval == 30.0
        assert config.connection_timeout == 5.0
    
    def test_config_to_dict(self):
        """Test configuration serialization."""
        config = HeartbeatConfig(ping_interval=20.0, max_retries=2)
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict['ping_interval'] == 20.0
        assert config_dict['max_retries'] == 2
        assert 'pong_timeout' in config_dict
        assert 'backoff_base' in config_dict


class TestHeartbeatMetrics:
    """Test heartbeat metrics."""
    
    def test_default_metrics(self):
        """Test default metrics initialization."""
        metrics = HeartbeatMetrics(endpoint="ws://test.com")
        
        assert metrics.endpoint == "ws://test.com"
        assert metrics.last_ping_time is None
        assert metrics.last_pong_time is None
        assert metrics.ping_count == 0
        assert metrics.pong_count == 0
        assert metrics.missed_heartbeats == 0
        assert metrics.connection_latency_ms == 0.0
        assert metrics.average_latency_ms == 0.0
        assert metrics.max_latency_ms == 0.0
        assert metrics.min_latency_ms == float('inf')
        assert metrics.consecutive_timeouts == 0
        assert metrics.total_reconnections == 0
        assert metrics.last_reconnection_time is None
        assert metrics.uptime_percentage == 100.0
        assert metrics.health_score == 1.0
    
    def test_metrics_to_dict(self):
        """Test metrics serialization."""
        metrics = HeartbeatMetrics(endpoint="ws://test.com")
        metrics_dict = metrics.to_dict()
        
        assert isinstance(metrics_dict, dict)
        assert metrics_dict['endpoint'] == "ws://test.com"
        assert metrics_dict['ping_count'] == 0
        assert metrics_dict['health_score'] == 1.0


class TestHeartbeatEvent:
    """Test heartbeat events."""
    
    def test_event_creation(self):
        """Test event creation."""
        event = HeartbeatEvent(
            event_type="ping_sent",
            endpoint="ws://test.com",
            timestamp=datetime.utcnow(),
            status=HeartbeatStatus.HEALTHY,
            latency_ms=50.0,
            metadata={"test": "data"}
        )
        
        assert event.event_type == "ping_sent"
        assert event.endpoint == "ws://test.com"
        assert event.status == HeartbeatStatus.HEALTHY
        assert event.latency_ms == 50.0
        assert event.metadata["test"] == "data"
    
    def test_event_to_dict(self):
        """Test event serialization."""
        timestamp = datetime.utcnow()
        event = HeartbeatEvent(
            event_type="pong_received",
            endpoint="ws://test.com",
            timestamp=timestamp,
            status=HeartbeatStatus.HEALTHY,
            latency_ms=25.0
        )
        
        event_dict = event.to_dict()
        assert isinstance(event_dict, dict)
        assert event_dict['event_type'] == "pong_received"
        assert event_dict['endpoint'] == "ws://test.com"
        assert event_dict['status'] == "healthy"
        assert event_dict['latency_ms'] == 25.0


class TestWebSocketHeartbeat:
    """Test WebSocket heartbeat mechanism."""
    
    @pytest.fixture
    def heartbeat_config(self):
        """Create test heartbeat configuration."""
        return HeartbeatConfig(
            ping_interval=1.0,  # 1 second for testing
            pong_timeout=3.0,   # 3 seconds timeout
            max_retries=2,
            health_check_interval=5.0
        )
    
    @pytest.fixture
    def heartbeat(self, heartbeat_config):
        """Create test heartbeat instance."""
        return WebSocketHeartbeat("ws://test.com", heartbeat_config)
    
    def test_heartbeat_initialization(self, heartbeat):
        """Test heartbeat initialization."""
        assert heartbeat.endpoint == "ws://test.com"
        assert heartbeat.config.ping_interval == 1.0
        assert heartbeat.config.pong_timeout == 3.0
        assert not heartbeat.is_connected
        assert not heartbeat.is_running
        assert heartbeat.websocket is None
    
    @pytest.mark.asyncio
    async def test_start_heartbeat_success(self, heartbeat):
        """Test successful heartbeat start."""
        # Mock WebSocket connection
        mock_websocket = AsyncMock()
        mock_websocket.closed = False
        
        with patch('websockets.connect', return_value=mock_websocket):
            await heartbeat.start()
            
            assert heartbeat.is_connected
            assert heartbeat.is_running
            assert heartbeat.websocket == mock_websocket
    
    @pytest.mark.asyncio
    async def test_start_heartbeat_connection_failure(self, heartbeat):
        """Test heartbeat start with connection failure."""
        with patch('websockets.connect', side_effect=ConnectionFailedError("Connection failed", "ws://test.com")):
            with pytest.raises(ConnectionFailedError):
                await heartbeat.start()
            
            assert not heartbeat.is_connected
            assert not heartbeat.is_running
    
    @pytest.mark.asyncio
    async def test_stop_heartbeat(self, heartbeat):
        """Test heartbeat stop."""
        # Start heartbeat first
        mock_websocket = AsyncMock()
        mock_websocket.closed = False
        
        with patch('websockets.connect', return_value=mock_websocket):
            await heartbeat.start()
            
            # Stop heartbeat
            await heartbeat.stop()
            
            assert not heartbeat.is_running
            assert not heartbeat.is_connected
            assert heartbeat.websocket is None
    
    @pytest.mark.asyncio
    async def test_send_ping_success(self, heartbeat):
        """Test successful ping send."""
        # Mock WebSocket connection
        mock_websocket = AsyncMock()
        mock_websocket.closed = False
        
        # Mock pong response
        pong_response = {
            "type": "pong",
            "id": "test-ping-id",
            "timestamp": datetime.utcnow().isoformat()
        }
        mock_websocket.recv.return_value = json.dumps(pong_response)
        
        with patch('websockets.connect', return_value=mock_websocket):
            await heartbeat.start()
            
            # Mock the ping ID to match response
            with patch('uuid.uuid4', return_value="test-ping-id"):
                result = await heartbeat.send_ping()
                
                assert result is True
                assert heartbeat.metrics.ping_count == 1
                assert heartbeat.metrics.pong_count == 1
                assert heartbeat.metrics.consecutive_timeouts == 0
    
    @pytest.mark.asyncio
    async def test_send_ping_timeout(self, heartbeat):
        """Test ping timeout."""
        # Mock WebSocket connection
        mock_websocket = AsyncMock()
        mock_websocket.closed = False
        
        # Mock timeout on recv
        mock_websocket.recv.side_effect = asyncio.TimeoutError()
        
        with patch('websockets.connect', return_value=mock_websocket):
            await heartbeat.start()
            
            result = await heartbeat.send_ping()
            
            assert result is False
            assert heartbeat.metrics.ping_count == 1
            assert heartbeat.metrics.pong_count == 0
            assert heartbeat.metrics.missed_heartbeats == 1
            assert heartbeat.metrics.consecutive_timeouts == 1
    
    @pytest.mark.asyncio
    async def test_send_ping_invalid_pong(self, heartbeat):
        """Test ping with invalid pong response."""
        # Mock WebSocket connection
        mock_websocket = AsyncMock()
        mock_websocket.closed = False
        
        # Mock invalid pong response
        invalid_response = {
            "type": "invalid",
            "id": "wrong-id"
        }
        mock_websocket.recv.return_value = json.dumps(invalid_response)
        
        with patch('websockets.connect', return_value=mock_websocket):
            await heartbeat.start()
            
            result = await heartbeat.send_ping()
            
            assert result is False
            assert heartbeat.metrics.ping_count == 1
            assert heartbeat.metrics.pong_count == 0
            assert heartbeat.metrics.missed_heartbeats == 1
    
    @pytest.mark.asyncio
    async def test_connection_closed_during_ping(self, heartbeat):
        """Test connection closed during ping."""
        # Mock WebSocket connection
        mock_websocket = AsyncMock()
        mock_websocket.closed = False
        
        # Mock connection closed during ping
        mock_websocket.send.side_effect = ConnectionClosed(None, None)
        
        with patch('websockets.connect', return_value=mock_websocket):
            await heartbeat.start()
            
            result = await heartbeat.send_ping()
            
            assert result is False
            assert not heartbeat.is_connected
    
    def test_latency_stats_update(self, heartbeat):
        """Test latency statistics update."""
        # Test first latency measurement
        heartbeat._update_latency_stats(100.0)
        assert heartbeat.metrics.average_latency_ms == 100.0
        assert heartbeat.metrics.min_latency_ms == 100.0
        assert heartbeat.metrics.max_latency_ms == 100.0
        
        # Test second latency measurement
        heartbeat._update_latency_stats(50.0)
        assert heartbeat.metrics.average_latency_ms == 75.0
        assert heartbeat.metrics.min_latency_ms == 50.0
        assert heartbeat.metrics.max_latency_ms == 100.0
        
        # Test third latency measurement
        heartbeat._update_latency_stats(150.0)
        assert heartbeat.metrics.average_latency_ms == 100.0
        assert heartbeat.metrics.min_latency_ms == 50.0
        assert heartbeat.metrics.max_latency_ms == 150.0
    
    def test_health_score_update(self, heartbeat):
        """Test health score calculation."""
        # Test perfect health
        heartbeat._update_health_score()
        assert heartbeat.metrics.health_score == 1.0
        
        # Test with missed heartbeats
        heartbeat.metrics.missed_heartbeats = 2
        heartbeat.metrics.ping_count = 10
        heartbeat._update_health_score()
        assert heartbeat.metrics.health_score < 1.0
        
        # Test with consecutive timeouts
        heartbeat.metrics.consecutive_timeouts = 3
        heartbeat._update_health_score()
        assert heartbeat.metrics.health_score < 0.5
    
    def test_uptime_percentage_update(self, heartbeat):
        """Test uptime percentage calculation."""
        # Test perfect uptime
        heartbeat._update_uptime_percentage()
        assert heartbeat.metrics.uptime_percentage == 100.0
        
        # Test with missed heartbeats
        heartbeat.metrics.ping_count = 10
        heartbeat.metrics.pong_count = 8
        heartbeat._update_uptime_percentage()
        assert heartbeat.metrics.uptime_percentage == 80.0
    
    def test_health_assessment(self, heartbeat):
        """Test health status assessment."""
        # Test healthy status
        heartbeat.is_connected = True
        heartbeat.metrics.health_score = 0.9
        status = heartbeat._assess_health()
        assert status == HeartbeatStatus.HEALTHY
        
        # Test degraded status
        heartbeat.metrics.health_score = 0.7
        status = heartbeat._assess_health()
        assert status == HeartbeatStatus.DEGRADED
        
        # Test unhealthy status
        heartbeat.metrics.health_score = 0.3
        status = heartbeat._assess_health()
        assert status == HeartbeatStatus.UNHEALTHY
        
        # Test timeout status
        heartbeat.metrics.consecutive_timeouts = 5
        status = heartbeat._assess_health()
        assert status == HeartbeatStatus.TIMEOUT
        
        # Test disconnected status
        heartbeat.is_connected = False
        status = heartbeat._assess_health()
        assert status == HeartbeatStatus.DISCONNECTED
    
    def test_event_callbacks(self, heartbeat):
        """Test event callback system."""
        callback_called = False
        received_event = None
        
        def test_callback(event):
            nonlocal callback_called, received_event
            callback_called = True
            received_event = event
        
        # Add callback
        heartbeat.add_event_callback(test_callback)
        
        # Emit test event
        asyncio.run(heartbeat._emit_event("test_event", HeartbeatStatus.HEALTHY))
        
        assert callback_called
        assert received_event.event_type == "test_event"
        assert received_event.status == HeartbeatStatus.HEALTHY
        
        # Remove callback
        heartbeat.remove_event_callback(test_callback)
        callback_called = False
        
        # Emit another event
        asyncio.run(heartbeat._emit_event("test_event_2", HeartbeatStatus.HEALTHY))
        
        assert not callback_called
    
    def test_get_metrics(self, heartbeat):
        """Test metrics retrieval."""
        metrics = heartbeat.get_metrics()
        assert isinstance(metrics, dict)
        assert metrics['endpoint'] == "ws://test.com"
        assert metrics['ping_count'] == 0
        assert metrics['health_score'] == 1.0
    
    def test_get_status(self, heartbeat):
        """Test status retrieval."""
        status = heartbeat.get_status()
        assert isinstance(status, dict)
        assert status['endpoint'] == "ws://test.com"
        assert status['is_connected'] is False
        assert status['is_running'] is False
        assert 'config' in status
        assert 'metrics' in status


class TestWebSocketConnectionHeartbeatIntegration:
    """Test WebSocket connection with heartbeat integration."""
    
    @pytest.fixture
    def connection(self):
        """Create test WebSocket connection."""
        config = HeartbeatConfig(ping_interval=1.0, pong_timeout=3.0)
        return WebSocketConnection("ws://test.com", heartbeat_config=config)
    
    def test_connection_with_heartbeat_config(self, connection):
        """Test connection initialization with heartbeat config."""
        assert connection.state.heartbeat_enabled is True
        assert connection.heartbeat_config.ping_interval == 1.0
        assert connection.heartbeat_config.pong_timeout == 3.0
        assert connection.heartbeat is None
    
    @pytest.mark.asyncio
    async def test_connect_with_heartbeat(self, connection):
        """Test connection establishment with heartbeat."""
        mock_websocket = AsyncMock()
        mock_websocket.closed = False
        
        with patch('websockets.connect', return_value=mock_websocket):
            await connection.connect()
            
            assert connection.state.status.value == "connected"
            assert connection.heartbeat is not None
            assert connection.heartbeat.is_running
    
    @pytest.mark.asyncio
    async def test_disconnect_stops_heartbeat(self, connection):
        """Test that disconnect stops heartbeat."""
        mock_websocket = AsyncMock()
        mock_websocket.closed = False
        
        with patch('websockets.connect', return_value=mock_websocket):
            await connection.connect()
            
            # Mock heartbeat stop
            connection.heartbeat.stop = AsyncMock()
            
            await connection.disconnect()
            
            assert connection.state.status.value == "disconnected"
            connection.heartbeat.stop.assert_called_once()
    
    def test_enable_disable_heartbeat(self, connection):
        """Test heartbeat enable/disable."""
        # Disable heartbeat
        connection.disable_heartbeat()
        assert connection.state.heartbeat_enabled is False
        
        # Enable heartbeat
        connection.enable_heartbeat()
        assert connection.state.heartbeat_enabled is True
    
    def test_heartbeat_callbacks(self, connection):
        """Test heartbeat event callbacks."""
        callback_called = False
        
        def test_callback(event):
            nonlocal callback_called
            callback_called = True
        
        # Add callback
        connection.add_heartbeat_callback(test_callback)
        
        # Simulate heartbeat event
        event = HeartbeatEvent(
            event_type="test",
            endpoint="ws://test.com",
            timestamp=datetime.utcnow(),
            status=HeartbeatStatus.HEALTHY
        )
        
        asyncio.run(connection._on_heartbeat_event(event))
        
        assert callback_called
        
        # Remove callback
        connection.remove_heartbeat_callback(test_callback)
        callback_called = False
        
        asyncio.run(connection._on_heartbeat_event(event))
        
        assert not callback_called
    
    def test_heartbeat_metrics_integration(self, connection):
        """Test heartbeat metrics integration with connection state."""
        # Mock heartbeat metrics
        mock_metrics = {
            "ping_count": 10,
            "pong_count": 9,
            "health_score": 0.9,
            "average_latency_ms": 50.0
        }
        
        # Simulate heartbeat event
        event = HeartbeatEvent(
            event_type="metrics_update",
            endpoint="ws://test.com",
            timestamp=datetime.utcnow(),
            status=HeartbeatStatus.HEALTHY
        )
        
        # Mock heartbeat get_metrics
        connection.heartbeat = MagicMock()
        connection.heartbeat.get_metrics.return_value = mock_metrics
        
        asyncio.run(connection._on_heartbeat_event(event))
        
        assert connection.state.heartbeat_metrics == mock_metrics
    
    def test_heartbeat_failure_handling(self, connection):
        """Test heartbeat failure handling."""
        # Simulate heartbeat failure event
        event = HeartbeatEvent(
            event_type="ping_timeout",
            endpoint="ws://test.com",
            timestamp=datetime.utcnow(),
            status=HeartbeatStatus.TIMEOUT,
            error_message="Pong timeout"
        )
        
        asyncio.run(connection._on_heartbeat_event(event))
        
        assert connection.state.status.value == "failed"
        assert "Heartbeat failure: Pong timeout" in connection.state.last_error


@pytest.mark.asyncio
async def test_heartbeat_integration_scenario():
    """Test complete heartbeat integration scenario."""
    # Create heartbeat with fast config for testing
    config = HeartbeatConfig(
        ping_interval=0.5,  # 500ms
        pong_timeout=1.0,    # 1 second
        max_retries=2,
        health_check_interval=2.0
    )
    
    heartbeat = WebSocketHeartbeat("ws://test.com", config)
    
    # Mock WebSocket connection
    mock_websocket = AsyncMock()
    mock_websocket.closed = False
    
    # Mock successful pong responses
    def mock_recv():
        return json.dumps({
            "type": "pong",
            "id": "test-id",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    mock_websocket.recv.side_effect = mock_recv
    
    events_received = []
    
    def event_callback(event):
        events_received.append(event)
    
    heartbeat.add_event_callback(event_callback)
    
    try:
        # Start heartbeat
        with patch('websockets.connect', return_value=mock_websocket):
            await heartbeat.start()
            
            # Wait for a few ping cycles
            await asyncio.sleep(2.0)
            
            # Check that we received events
            assert len(events_received) > 0
            
            # Check metrics
            metrics = heartbeat.get_metrics()
            assert metrics['ping_count'] > 0
            assert metrics['pong_count'] > 0
            assert metrics['health_score'] > 0.8
            
            # Stop heartbeat
            await heartbeat.stop()
            
            assert not heartbeat.is_running
            assert not heartbeat.is_connected
            
    except Exception as e:
        # Clean up on error
        await heartbeat.stop()
        raise e


if __name__ == "__main__":
    pytest.main([__file__, "-v"])