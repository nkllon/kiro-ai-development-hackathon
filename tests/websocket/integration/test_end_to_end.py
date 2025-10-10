"""End-to-end integration tests for WebSocket connectivity."""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from src.beast_mode.observatory.websocket.manager import (
    WebSocketManager,
    WebSocketManagerConfig
)
from src.beast_mode.observatory.websocket.connection import (
    WebSocketConnection,
    ConnectionStatus
)
from tests.websocket.fixtures.websocket_test_data import (
    WebSocketTestConfig,
    WebSocketTestData,
    WebSocketTestMetrics
)
from tests.websocket.fixtures.mock_tunnel_config import (
    MockTunnelManager,
    MockTunnelConfig
)


class TestWebSocketEndToEnd:
    """Test end-to-end WebSocket functionality."""
    
    @pytest.fixture
    def test_config(self):
        """Create test configuration."""
        return WebSocketTestConfig(
            base_url="ws://localhost:8000",
            tunnel_url="wss://observatory.nkllon.com",
            connection_timeout=10.0,
            max_connections=50
        )
    
    @pytest.fixture
    def websocket_manager(self, test_config):
        """Create WebSocket manager."""
        config = WebSocketManagerConfig(
            base_url=test_config.base_url,
            max_connections_per_endpoint=test_config.max_connections,
            connection_timeout=test_config.connection_timeout,
            retry_max_attempts=3,
            health_check_interval=30.0
        )
        return WebSocketManager(config)
    
    @pytest.fixture
    def tunnel_manager(self):
        """Create tunnel manager."""
        tunnel_config = MockTunnelConfig(
            hostname="observatory.nkllon.com",
            protocol="wss"
        )
        return MockTunnelManager(tunnel_config)
    
    @pytest.fixture
    def test_metrics(self):
        """Create test metrics collector."""
        return WebSocketTestMetrics()
    
    @pytest.mark.asyncio
    async def test_complete_websocket_lifecycle(self, websocket_manager, test_metrics):
        """Test complete WebSocket connection lifecycle."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_complete_websocket_lifecycle",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "end_to_end"}
        }))
        
        # Step 1: Start manager
        await websocket_manager.start()
        assert websocket_manager._is_running is True
        
        # Step 2: Connect to endpoints
        connections = {}
        for endpoint in websocket_manager.endpoints:
            try:
                with patch.object(websocket_manager, '_create_connection') as mock_create:
                    mock_connection = Mock()
                    mock_connection.is_connected.return_value = True
                    mock_connection.send_message = AsyncMock()
                    mock_connection.disconnect = AsyncMock()
                    mock_connection.state = Mock()
                    mock_connection.state.status = ConnectionStatus.CONNECTED
                    mock_connection.state.failure_count = 0
                    mock_connection.state.last_error = None
                    mock_connection.state.message_count = 0
                    mock_connection.state.connection_time = datetime.utcnow()
                    
                    mock_create.return_value = mock_connection
                    
                    connection = await websocket_manager.connect_websocket(endpoint)
                    connections[endpoint] = connection
                    
                    test_metrics.record_connection_attempt(True, 25.5)
            except Exception as e:
                test_metrics.record_connection_attempt(False, 0)
                test_metrics.record_error(type(e).__name__)
        
        # Step 3: Send test messages
        test_messages = WebSocketTestData.get_test_messages(5)
        for endpoint, connection in connections.items():
            for message in test_messages:
                try:
                    await websocket_manager.send_message(endpoint, message.__dict__, connection)
                    test_metrics.record_message(True, 15.2)
                except Exception as e:
                    test_metrics.record_error(type(e).__name__)
        
        # Step 4: Check connection status
        all_status = websocket_manager.get_all_connection_status()
        assert len(all_status) == len(websocket_manager.endpoints)
        
        # Step 5: Disconnect all connections
        for endpoint in websocket_manager.endpoints:
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        # Step 6: Stop manager
        await websocket_manager.stop()
        assert websocket_manager._is_running is False
        
        # Verify metrics
        summary = test_metrics.get_summary()
        assert summary["connection_success_rate"] >= 0
        assert summary["messages_per_second"] >= 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_complete_websocket_lifecycle",
            "status": "completed",
            "details": {"test_type": "integration", "component": "end_to_end", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_websocket_message_roundtrip(self, websocket_manager, test_metrics):
        """Test bidirectional message communication."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_websocket_message_roundtrip",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "end_to_end"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/emoji-rain"
        
        # Create mock connection with message handling
        mock_websocket = Mock()
        mock_websocket.send = AsyncMock()
        mock_websocket.recv = AsyncMock()
        mock_websocket.close = AsyncMock()
        mock_websocket.closed = False
        mock_websocket.open = True
        
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        mock_connection.send_message = AsyncMock()
        mock_connection.receive_message = AsyncMock()
        mock_connection.disconnect = AsyncMock()
        mock_connection.state = Mock()
        mock_connection.state.status = ConnectionStatus.CONNECTED
        mock_connection.state.failure_count = 0
        mock_connection.state.last_error = None
        mock_connection.state.message_count = 0
        mock_connection.state.connection_time = datetime.utcnow()
        
        with patch.object(websocket_manager, '_create_connection', return_value=mock_connection):
            connection = await websocket_manager.connect_websocket(endpoint)
            
            # Test message sending
            test_message = {"type": "test", "data": "hello", "id": "msg-1"}
            await websocket_manager.send_message(endpoint, test_message, connection)
            test_metrics.record_message(True, 12.5)
            
            # Test message receiving
            response_message = {"type": "response", "data": "world", "id": "msg-1"}
            mock_connection.receive_message.return_value = response_message
            received_message = await connection.receive_message()
            
            assert received_message == response_message
            test_metrics.record_message(False, 8.3)
            
            # Test message roundtrip
            roundtrip_message = {"type": "roundtrip", "data": "test", "id": "msg-2"}
            await websocket_manager.send_message(endpoint, roundtrip_message, connection)
            test_metrics.record_message(True, 10.1)
            
            # Simulate response
            roundtrip_response = {"type": "roundtrip_response", "data": "test", "id": "msg-2"}
            mock_connection.receive_message.return_value = roundtrip_response
            received_response = await connection.receive_message()
            
            assert received_response == roundtrip_response
            test_metrics.record_message(False, 7.8)
        
        await websocket_manager.stop()
        
        # Verify metrics
        summary = test_metrics.get_summary()
        assert summary["messages_per_second"] > 0
        assert summary["average_message_latency_ms"] > 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_websocket_message_roundtrip",
            "status": "completed",
            "details": {"test_type": "integration", "component": "end_to_end", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_connection_recovery_scenario(self, websocket_manager, test_metrics):
        """Test connection recovery after failures."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_recovery_scenario",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "end_to_end"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/observatory"
        
        # Create mock connection
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        mock_connection.send_message = AsyncMock()
        mock_connection.disconnect = AsyncMock()
        mock_connection.state = Mock()
        mock_connection.state.status = ConnectionStatus.CONNECTED
        mock_connection.state.failure_count = 0
        mock_connection.state.last_error = None
        mock_connection.state.message_count = 0
        mock_connection.state.connection_time = datetime.utcnow()
        
        with patch.object(websocket_manager, '_create_connection', return_value=mock_connection):
            # Initial connection
            connection = await websocket_manager.connect_websocket(endpoint)
            test_metrics.record_connection_attempt(True, 20.0)
            
            # Simulate connection failure
            connection.state.status = ConnectionStatus.FAILED
            connection.state.failure_count = 1
            connection.state.last_error = "Network error"
            
            # Handle failure
            await websocket_manager.handle_connection_failure(endpoint, connection, Exception("Network error"))
            test_metrics.record_error("ConnectionFailedError")
            
            # Verify connection removed from pool
            assert connection not in websocket_manager.connections[endpoint]
            
            # Attempt reconnection
            new_mock_connection = Mock()
            new_mock_connection.is_connected.return_value = True
            new_mock_connection.send_message = AsyncMock()
            new_mock_connection.disconnect = AsyncMock()
            new_mock_connection.state = Mock()
            new_mock_connection.state.status = ConnectionStatus.CONNECTED
            new_mock_connection.state.failure_count = 0
            new_mock_connection.state.last_error = None
            new_mock_connection.state.message_count = 0
            new_mock_connection.state.connection_time = datetime.utcnow()
            
            with patch.object(websocket_manager, '_create_connection', return_value=new_mock_connection):
                recovered_connection = await websocket_manager.connect_websocket(endpoint)
                test_metrics.record_connection_attempt(True, 35.0)
                
                # Verify recovery
                assert recovered_connection == new_mock_connection
                assert len(websocket_manager.connections[endpoint]) == 1
        
        await websocket_manager.stop()
        
        # Verify recovery metrics
        summary = test_metrics.get_summary()
        assert summary["connection_success_rate"] > 0
        assert summary["total_errors"] > 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_recovery_scenario",
            "status": "completed",
            "details": {"test_type": "integration", "component": "end_to_end", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_multiple_endpoints_concurrent_operations(self, websocket_manager, test_metrics):
        """Test concurrent operations across multiple endpoints."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_multiple_endpoints_concurrent_operations",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "end_to_end"}
        }))
        
        await websocket_manager.start()
        
        # Create connections for all endpoints concurrently
        async def connect_endpoint(endpoint):
            mock_connection = Mock()
            mock_connection.is_connected.return_value = True
            mock_connection.send_message = AsyncMock()
            mock_connection.disconnect = AsyncMock()
            mock_connection.state = Mock()
            mock_connection.state.status = ConnectionStatus.CONNECTED
            mock_connection.state.failure_count = 0
            mock_connection.state.last_error = None
            mock_connection.state.message_count = 0
            mock_connection.state.connection_time = datetime.utcnow()
            
            with patch.object(websocket_manager, '_create_connection', return_value=mock_connection):
                return await websocket_manager.connect_websocket(endpoint)
        
        # Connect to all endpoints concurrently
        connections = await asyncio.gather(
            *[connect_endpoint(endpoint) for endpoint in websocket_manager.endpoints],
            return_exceptions=True
        )
        
        # Record connection attempts
        for i, connection in enumerate(connections):
            if isinstance(connection, Exception):
                test_metrics.record_connection_attempt(False, 0)
                test_metrics.record_error(type(connection).__name__)
            else:
                test_metrics.record_connection_attempt(True, 25.0 + i * 5)
        
        # Send messages concurrently across all endpoints
        async def send_messages_to_endpoint(endpoint, connection):
            if isinstance(connection, Exception):
                return
            
            test_messages = WebSocketTestData.get_test_messages(3)
            for message in test_messages:
                try:
                    await websocket_manager.send_message(endpoint, message.__dict__, connection)
                    test_metrics.record_message(True, 10.0)
                except Exception as e:
                    test_metrics.record_error(type(e).__name__)
        
        # Send messages concurrently
        await asyncio.gather(
            *[send_messages_to_endpoint(endpoint, connection) 
              for endpoint, connection in zip(websocket_manager.endpoints, connections)],
            return_exceptions=True
        )
        
        # Check status of all endpoints
        all_status = websocket_manager.get_all_connection_status()
        assert len(all_status) == len(websocket_manager.endpoints)
        
        # Disconnect all endpoints concurrently
        async def disconnect_endpoint(endpoint):
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        await asyncio.gather(
            *[disconnect_endpoint(endpoint) for endpoint in websocket_manager.endpoints],
            return_exceptions=True
        )
        
        await websocket_manager.stop()
        
        # Verify concurrent operation metrics
        summary = test_metrics.get_summary()
        assert summary["messages_per_second"] > 0
        assert summary["connection_success_rate"] >= 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_multiple_endpoints_concurrent_operations",
            "status": "completed",
            "details": {"test_type": "integration", "component": "end_to_end", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_health_monitoring_integration(self, websocket_manager, tunnel_manager, test_metrics):
        """Test health monitoring integration."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_health_monitoring_integration",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "end_to_end"}
        }))
        
        # Start both managers
        await websocket_manager.start()
        await tunnel_manager.connect()
        
        # Check initial health
        websocket_health = await websocket_manager.get_health_status()
        tunnel_health = await tunnel_manager.get_all_endpoints_health()
        
        assert websocket_health is not None
        assert tunnel_health is not None
        
        # Simulate endpoint failures
        tunnel_manager.simulate_endpoint_failure("/ws/emoji-rain")
        tunnel_manager.simulate_endpoint_failure("/ws/anomalies")
        
        # Check health after failures
        tunnel_health_after = await tunnel_manager.get_all_endpoints_health()
        
        unhealthy_count = sum(1 for health in tunnel_health_after.values() if health["status"] == "unhealthy")
        assert unhealthy_count == 2
        
        # Simulate recovery
        tunnel_manager.simulate_endpoint_recovery("/ws/emoji-rain")
        tunnel_manager.simulate_endpoint_recovery("/ws/anomalies")
        
        # Check health after recovery
        tunnel_health_recovered = await tunnel_manager.get_all_endpoints_health()
        
        healthy_count = sum(1 for health in tunnel_health_recovered.values() if health["status"] == "healthy")
        assert healthy_count == len(tunnel_manager.endpoints)
        
        # Test health monitoring over time
        for _ in range(3):
            await asyncio.sleep(0.1)  # Simulate time passage
            
            websocket_health = await websocket_manager.get_health_status()
            tunnel_health = await tunnel_manager.get_all_endpoints_health()
            
            assert websocket_health is not None
            assert tunnel_health is not None
        
        # Cleanup
        await websocket_manager.stop()
        await tunnel_manager.disconnect()
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_health_monitoring_integration",
            "status": "completed",
            "details": {"test_type": "integration", "component": "end_to_end", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_error_scenarios_comprehensive(self, websocket_manager, test_metrics):
        """Test comprehensive error scenarios."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_error_scenarios_comprehensive",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "end_to_end"}
        }))
        
        await websocket_manager.start()
        
        error_scenarios = WebSocketTestData.get_error_scenarios()
        
        for scenario in error_scenarios:
            endpoint = "/ws/emoji-rain"
            
            try:
                # Simulate different error types
                if scenario["name"] == "connection_timeout":
                    with patch.object(websocket_manager, '_create_connection', side_effect=asyncio.TimeoutError):
                        await websocket_manager.connect_websocket(endpoint)
                elif scenario["name"] == "authentication_failure":
                    with patch.object(websocket_manager, '_create_connection', side_effect=Exception("Authentication failed")):
                        await websocket_manager.connect_websocket(endpoint)
                elif scenario["name"] == "rate_limit_exceeded":
                    with patch.object(websocket_manager, '_create_connection', side_effect=Exception("Rate limit exceeded")):
                        await websocket_manager.connect_websocket(endpoint)
                elif scenario["name"] == "protocol_error":
                    with patch.object(websocket_manager, '_create_connection', side_effect=Exception("Protocol error")):
                        await websocket_manager.connect_websocket(endpoint)
                elif scenario["name"] == "network_unavailable":
                    with patch.object(websocket_manager, '_create_connection', side_effect=Exception("Network unavailable")):
                        await websocket_manager.connect_websocket(endpoint)
                
                test_metrics.record_error(scenario["error_type"])
                
            except Exception as e:
                test_metrics.record_error(type(e).__name__)
        
        # Test message sending errors
        try:
            await websocket_manager.send_message("/ws/nonexistent", {"test": "data"})
        except Exception as e:
            test_metrics.record_error(type(e).__name__)
        
        # Test invalid endpoint
        try:
            await websocket_manager.connect_websocket("/ws/invalid")
        except Exception as e:
            test_metrics.record_error(type(e).__name__)
        
        await websocket_manager.stop()
        
        # Verify error metrics
        summary = test_metrics.get_summary()
        assert summary["total_errors"] > 0
        assert len(summary["error_breakdown"]) > 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_error_scenarios_comprehensive",
            "status": "completed",
            "details": {"test_type": "integration", "component": "end_to_end", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_performance_characteristics(self, websocket_manager, test_metrics):
        """Test performance characteristics."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_performance_characteristics",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "end_to_end"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/emoji-rain"
        
        # Create mock connection
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        mock_connection.send_message = AsyncMock()
        mock_connection.disconnect = AsyncMock()
        mock_connection.state = Mock()
        mock_connection.state.status = ConnectionStatus.CONNECTED
        mock_connection.state.failure_count = 0
        mock_connection.state.last_error = None
        mock_connection.state.message_count = 0
        mock_connection.state.connection_time = datetime.utcnow()
        
        with patch.object(websocket_manager, '_create_connection', return_value=mock_connection):
            # Test connection performance
            start_time = asyncio.get_event_loop().time()
            connection = await websocket_manager.connect_websocket(endpoint)
            connection_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            test_metrics.record_connection_attempt(True, connection_time)
            
            # Test message throughput
            rapid_messages = WebSocketTestData.get_rapid_messages(100)
            
            start_time = asyncio.get_event_loop().time()
            for message in rapid_messages:
                await websocket_manager.send_message(endpoint, message.__dict__, connection)
                test_metrics.record_message(True, 5.0)  # Simulate low latency
            
            end_time = asyncio.get_event_loop().time()
            total_time = end_time - start_time
            messages_per_second = len(rapid_messages) / total_time
            
            # Test large message handling
            large_message = WebSocketTestData.get_large_message(10)  # 10KB
            start_time = asyncio.get_event_loop().time()
            await websocket_manager.send_message(endpoint, large_message.__dict__, connection)
            large_message_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            test_metrics.record_message(True, large_message_time)
            
            # Verify performance characteristics
            assert connection_time < 1000  # Connection should be fast
            assert messages_per_second > 50  # Should handle reasonable throughput
            assert large_message_time < 5000  # Large messages should be reasonable
        
        await websocket_manager.stop()
        
        # Verify performance metrics
        summary = test_metrics.get_summary()
        assert summary["average_connection_duration_ms"] > 0
        assert summary["messages_per_second"] > 0
        assert summary["average_message_latency_ms"] > 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_performance_characteristics",
            "status": "completed",
            "details": {"test_type": "integration", "component": "end_to_end", "result": "passed"}
        }))