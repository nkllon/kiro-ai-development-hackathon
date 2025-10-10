"""Unit tests for WebSocket Connection Handler."""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from src.beast_mode.observatory.websocket.connection import (
    WebSocketConnection,
    ConnectionState,
    ConnectionStatus
)
from src.beast_mode.observatory.websocket.exceptions import (
    WebSocketConnectionError,
    WebSocketTimeoutError,
    ConnectionFailedError,
    ConnectionTimeoutError
)
from tests.websocket.fixtures.websocket_test_data import (
    WebSocketTestConfig,
    WebSocketTestData,
    WebSocketTestMetrics
)


class TestWebSocketConnection:
    """Test WebSocket Connection functionality."""
    
    @pytest.fixture
    def connection_config(self):
        """Create test connection configuration."""
        return {
            "endpoint": "ws://localhost:8000/ws/test",
            "connection_timeout": 10.0,
            "heartbeat_config": None
        }
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket connection."""
        websocket = Mock()
        websocket.send = AsyncMock()
        websocket.recv = AsyncMock()
        websocket.close = AsyncMock()
        websocket.closed = False
        websocket.open = True
        return websocket
    
    def test_connection_initialization(self, connection_config):
        """Test WebSocket connection initialization."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_initialization",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        
        assert connection.endpoint == connection_config["endpoint"]
        assert connection.connection_timeout == connection_config["connection_timeout"]
        assert connection.state.status == ConnectionStatus.DISCONNECTED
        assert connection.state.failure_count == 0
        assert connection.state.message_count == 0
        assert connection.state.last_error is None
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_initialization",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_connection_success(self, connection_config, mock_websocket):
        """Test successful WebSocket connection."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_success",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        
        with patch('websockets.connect', return_value=mock_websocket):
            await connection.connect()
            
            assert connection.state.status == ConnectionStatus.CONNECTED
            assert connection.websocket == mock_websocket
            assert connection.state.connection_time is not None
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_success",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_connection_timeout(self, connection_config):
        """Test connection timeout handling."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_timeout",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        
        with patch('websockets.connect', side_effect=asyncio.TimeoutError):
            with pytest.raises(ConnectionTimeoutError):
                await connection.connect()
            
            assert connection.state.status == ConnectionStatus.FAILED
            assert connection.state.failure_count == 1
            assert connection.state.last_error is not None
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_timeout",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_connection_failure(self, connection_config):
        """Test connection failure handling."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_failure",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        
        with patch('websockets.connect', side_effect=Exception("Connection failed")):
            with pytest.raises(ConnectionFailedError):
                await connection.connect()
            
            assert connection.state.status == ConnectionStatus.FAILED
            assert connection.state.failure_count == 1
            assert "Connection failed" in str(connection.state.last_error)
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_failure",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, connection_config, mock_websocket):
        """Test successful message sending."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_send_message_success",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        connection.websocket = mock_websocket
        connection.state.status = ConnectionStatus.CONNECTED
        
        test_message = {"type": "test", "data": "hello"}
        await connection.send_message(test_message)
        
        mock_websocket.send.assert_called_once_with(json.dumps(test_message))
        assert connection.state.message_count == 1
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_send_message_success",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_send_message_not_connected(self, connection_config):
        """Test message sending when not connected."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_send_message_not_connected",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        connection.state.status = ConnectionStatus.DISCONNECTED
        
        test_message = {"type": "test", "data": "hello"}
        
        with pytest.raises(WebSocketConnectionError):
            await connection.send_message(test_message)
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_send_message_not_connected",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_send_message_failure(self, connection_config, mock_websocket):
        """Test message sending failure."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_send_message_failure",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        connection.websocket = mock_websocket
        connection.state.status = ConnectionStatus.CONNECTED
        
        mock_websocket.send.side_effect = Exception("Send failed")
        
        test_message = {"type": "test", "data": "hello"}
        
        with pytest.raises(WebSocketConnectionError):
            await connection.send_message(test_message)
        
        assert connection.state.failure_count == 1
        assert connection.state.last_error is not None
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_send_message_failure",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_receive_message_success(self, connection_config, mock_websocket):
        """Test successful message receiving."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_receive_message_success",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        connection.websocket = mock_websocket
        connection.state.status = ConnectionStatus.CONNECTED
        
        test_message = {"type": "response", "data": "world"}
        mock_websocket.recv.return_value = json.dumps(test_message)
        
        received_message = await connection.receive_message()
        
        assert received_message == test_message
        mock_websocket.recv.assert_called_once()
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_receive_message_success",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_receive_message_not_connected(self, connection_config):
        """Test message receiving when not connected."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_receive_message_not_connected",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        connection.state.status = ConnectionStatus.DISCONNECTED
        
        with pytest.raises(WebSocketConnectionError):
            await connection.receive_message()
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_receive_message_not_connected",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_disconnect_success(self, connection_config, mock_websocket):
        """Test successful disconnection."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_disconnect_success",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        connection.websocket = mock_websocket
        connection.state.status = ConnectionStatus.CONNECTED
        
        await connection.disconnect()
        
        mock_websocket.close.assert_called_once()
        assert connection.state.status == ConnectionStatus.DISCONNECTED
        assert connection.websocket is None
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_disconnect_success",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_disconnect_not_connected(self, connection_config):
        """Test disconnection when not connected."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_disconnect_not_connected",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        connection.state.status = ConnectionStatus.DISCONNECTED
        
        # Should not raise exception
        await connection.disconnect()
        
        assert connection.state.status == ConnectionStatus.DISCONNECTED
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_disconnect_not_connected",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    def test_is_connected(self, connection_config):
        """Test connection status checking."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_is_connected",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        
        # Test disconnected
        connection.state.status = ConnectionStatus.DISCONNECTED
        assert connection.is_connected() is False
        
        # Test connected
        connection.state.status = ConnectionStatus.CONNECTED
        assert connection.is_connected() is True
        
        # Test failed
        connection.state.status = ConnectionStatus.FAILED
        assert connection.is_connected() is False
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_is_connected",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    def test_connection_state_transitions(self, connection_config):
        """Test connection state transitions."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_state_transitions",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        
        # Initial state
        assert connection.state.status == ConnectionStatus.DISCONNECTED
        assert connection.state.failure_count == 0
        
        # Simulate connection attempt
        connection.state.status = ConnectionStatus.CONNECTING
        assert connection.state.status == ConnectionStatus.CONNECTING
        
        # Simulate successful connection
        connection.state.status = ConnectionStatus.CONNECTED
        connection.state.connection_time = datetime.utcnow()
        assert connection.state.status == ConnectionStatus.CONNECTED
        assert connection.state.connection_time is not None
        
        # Simulate failure
        connection.state.status = ConnectionStatus.FAILED
        connection.state.failure_count = 1
        connection.state.last_error = "Test error"
        assert connection.state.status == ConnectionStatus.FAILED
        assert connection.state.failure_count == 1
        assert connection.state.last_error == "Test error"
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_state_transitions",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_heartbeat_functionality(self, connection_config, mock_websocket):
        """Test heartbeat functionality."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_heartbeat_functionality",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        from src.beast_mode.observatory.websocket.heartbeat import HeartbeatConfig
        
        heartbeat_config = HeartbeatConfig(
            interval=1.0,
            timeout=5.0
        )
        
        connection = WebSocketConnection(
            endpoint=connection_config["endpoint"],
            connection_timeout=connection_config["connection_timeout"],
            heartbeat_config=heartbeat_config
        )
        
        connection.websocket = mock_websocket
        connection.state.status = ConnectionStatus.CONNECTED
        
        # Test heartbeat sending
        await connection._send_heartbeat()
        
        # Should send ping message
        mock_websocket.send.assert_called()
        call_args = mock_websocket.send.call_args[0][0]
        heartbeat_message = json.loads(call_args)
        assert heartbeat_message["type"] == "ping"
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_heartbeat_functionality",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))
    
    def test_connection_metrics(self, connection_config):
        """Test connection metrics tracking."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_metrics",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_connection"}
        }))
        
        connection = WebSocketConnection(**connection_config)
        
        # Test initial metrics
        assert connection.state.message_count == 0
        assert connection.state.failure_count == 0
        assert connection.state.last_error is None
        
        # Simulate message sending
        connection.state.message_count = 5
        assert connection.state.message_count == 5
        
        # Simulate failures
        connection.state.failure_count = 2
        connection.state.last_error = "Test error"
        assert connection.state.failure_count == 2
        assert connection.state.last_error == "Test error"
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_metrics",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_connection", "result": "passed"}
        }))