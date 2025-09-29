"""Unit tests for WebSocket Manager."""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from src.beast_mode.observatory.websocket.manager import (
    WebSocketManager,
    WebSocketManagerConfig,
    create_websocket_manager,
    connect_to_endpoints
)
from src.beast_mode.observatory.websocket.exceptions import (
    WebSocketConnectionError,
    MaxConnectionsError,
    RetryExhaustedError
)
from tests.websocket.fixtures.websocket_test_data import (
    WebSocketTestConfig,
    WebSocketTestData,
    WebSocketTestMetrics
)


class TestWebSocketManager:
    """Test WebSocket Manager functionality."""
    
    @pytest.fixture
    def manager_config(self):
        """Create test manager configuration."""
        return WebSocketManagerConfig(
            base_url="ws://localhost:8000",
            max_connections_per_endpoint=5,
            connection_timeout=10.0,
            retry_max_attempts=3,
            health_check_interval=30.0
        )
    
    @pytest.fixture
    def manager(self, manager_config):
        """Create WebSocket manager instance."""
        return WebSocketManager(manager_config)
    
    @pytest.fixture
    def mock_connection(self):
        """Create mock WebSocket connection."""
        connection = Mock()
        connection.is_connected.return_value = True
        connection.send_message = AsyncMock()
        connection.disconnect = AsyncMock()
        connection.state = Mock()
        connection.state.status = Mock()
        connection.state.status.value = "connected"
        connection.state.failure_count = 0
        connection.state.last_error = None
        connection.state.message_count = 0
        connection.state.connection_time = datetime.utcnow()
        return connection
    
    def test_manager_initialization(self, manager_config):
        """Test WebSocket manager initialization."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_manager_initialization",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        manager = WebSocketManager(manager_config)
        
        assert manager.config == manager_config
        assert len(manager.endpoints) == 4
        assert "/ws/emoji-rain" in manager.endpoints
        assert "/ws/observatory" in manager.endpoints
        assert "/ws/anomalies" in manager.endpoints
        assert "/ws/doctor-status" in manager.endpoints
        
        # Check retry strategies initialized
        for endpoint in manager.endpoints:
            assert endpoint in manager.retry_strategies
            assert endpoint in manager.connection_locks
            assert endpoint in manager.connections
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_manager_initialization",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_manager_start_stop(self, manager):
        """Test manager start and stop functionality."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_manager_start_stop",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        # Test start
        await manager.start()
        assert manager._is_running is True
        
        # Test stop
        await manager.stop()
        assert manager._is_running is False
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_manager_start_stop",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_connect_websocket_success(self, manager, mock_connection):
        """Test successful WebSocket connection."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connect_websocket_success",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        endpoint = "/ws/emoji-rain"
        
        with patch.object(manager, '_create_connection', return_value=mock_connection):
            connection = await manager.connect_websocket(endpoint)
            
            assert connection == mock_connection
            assert len(manager.connections[endpoint]) == 1
            assert connection in manager.connections[endpoint]
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connect_websocket_success",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_connect_websocket_max_connections(self, manager, mock_connection):
        """Test connection failure when max connections reached."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connect_websocket_max_connections",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        endpoint = "/ws/emoji-rain"
        
        # Fill up connections to max
        for _ in range(manager.config.max_connections_per_endpoint):
            manager.connections[endpoint].append(mock_connection)
        
        with pytest.raises(MaxConnectionsError):
            await manager.connect_websocket(endpoint)
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connect_websocket_max_connections",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_connect_websocket_retry_exhausted(self, manager):
        """Test connection failure after retry exhaustion."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connect_websocket_retry_exhausted",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        endpoint = "/ws/emoji-rain"
        
        with patch.object(manager, '_create_connection', side_effect=RetryExhaustedError("Max retries exceeded", 3)):
            with pytest.raises(WebSocketConnectionError):
                await manager.connect_websocket(endpoint)
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connect_websocket_retry_exhausted",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_disconnect_websocket(self, manager, mock_connection):
        """Test WebSocket disconnection."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_disconnect_websocket",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        endpoint = "/ws/emoji-rain"
        manager.connections[endpoint].append(mock_connection)
        
        await manager.disconnect_websocket(endpoint, mock_connection)
        
        assert len(manager.connections[endpoint]) == 0
        mock_connection.disconnect.assert_called_once()
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_disconnect_websocket",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_disconnect_all_websockets(self, manager, mock_connection):
        """Test disconnecting all WebSocket connections."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_disconnect_all_websockets",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        endpoint = "/ws/emoji-rain"
        
        # Add multiple connections
        connections = [mock_connection for _ in range(3)]
        manager.connections[endpoint].extend(connections)
        
        await manager.disconnect_all_websockets(endpoint)
        
        assert len(manager.connections[endpoint]) == 0
        assert mock_connection.disconnect.call_count == 3
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_disconnect_all_websockets",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, manager, mock_connection):
        """Test successful message sending."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_send_message_success",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        endpoint = "/ws/emoji-rain"
        manager.connections[endpoint].append(mock_connection)
        
        test_message = {"type": "test", "data": "hello"}
        await manager.send_message(endpoint, test_message, mock_connection)
        
        mock_connection.send_message.assert_called_once_with(test_message)
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_send_message_success",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_send_message_no_connections(self, manager):
        """Test message sending with no available connections."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_send_message_no_connections",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        endpoint = "/ws/emoji-rain"
        test_message = {"type": "test", "data": "hello"}
        
        with pytest.raises(WebSocketConnectionError):
            await manager.send_message(endpoint, test_message)
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_send_message_no_connections",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_handle_connection_failure(self, manager, mock_connection):
        """Test connection failure handling."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_handle_connection_failure",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        endpoint = "/ws/emoji-rain"
        manager.connections[endpoint].append(mock_connection)
        
        error = Exception("Connection failed")
        
        with patch.object(manager, 'connect_websocket', return_value=mock_connection):
            await manager.handle_connection_failure(endpoint, mock_connection, error)
        
        # Connection should be removed from pool
        assert mock_connection not in manager.connections[endpoint]
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_handle_connection_failure",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    def test_get_connection_status(self, manager, mock_connection):
        """Test getting connection status."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_get_connection_status",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        endpoint = "/ws/emoji-rain"
        manager.connections[endpoint].append(mock_connection)
        
        status = manager.get_connection_status(endpoint)
        
        assert status['endpoint'] == endpoint
        assert status['total_connections'] == 1
        assert status['connected_connections'] == 1
        assert status['disconnected_connections'] == 0
        assert status['max_connections'] == manager.config.max_connections_per_endpoint
        assert len(status['connections']) == 1
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_get_connection_status",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    def test_get_all_connection_status(self, manager, mock_connection):
        """Test getting status for all endpoints."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_get_all_connection_status",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        endpoint = "/ws/emoji-rain"
        manager.connections[endpoint].append(mock_connection)
        
        all_status = manager.get_all_connection_status()
        
        assert len(all_status) == len(manager.endpoints)
        assert endpoint in all_status
        assert all_status[endpoint]['total_connections'] == 1
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_get_all_connection_status",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_connection_callbacks(self, manager):
        """Test connection event callbacks."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_callbacks",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        callback_called = False
        callback_data = None
        
        async def test_callback(endpoint, connection, data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = data
        
        manager.add_connection_callback('connected', test_callback)
        
        await manager._notify_callbacks('connected', '/ws/test', None, {'test': 'data'})
        
        assert callback_called is True
        assert callback_data == {'test': 'data'}
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_callbacks",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_create_websocket_manager(self):
        """Test convenience function for creating WebSocket manager."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_create_websocket_manager",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        with patch('src.beast_mode.observatory.websocket.manager.WebSocketManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            
            manager = await create_websocket_manager("ws://test:8000")
            
            mock_manager_class.assert_called_once()
            mock_manager.start.assert_called_once()
            assert manager == mock_manager
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_create_websocket_manager",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_connect_to_endpoints(self, manager, mock_connection):
        """Test connecting to multiple endpoints."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connect_to_endpoints",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "websocket_manager"}
        }))
        
        with patch.object(manager, 'connect_websocket', return_value=mock_connection):
            connections = await connect_to_endpoints(manager, ['/ws/emoji-rain'])
            
            assert '/ws/emoji-rain' in connections
            assert len(connections['/ws/emoji-rain']) == 1
            assert connections['/ws/emoji-rain'][0] == mock_connection
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connect_to_endpoints",
            "status": "completed",
            "details": {"test_type": "unit", "component": "websocket_manager", "result": "passed"}
        }))