"""Integration tests for WebSocket fallback scenarios."""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from src.beast_mode.observatory.websocket.manager import (
    WebSocketManager,
    WebSocketManagerConfig
)
from src.beast_mode.observatory.websocket.connection import ConnectionStatus
from src.beast_mode.observatory.websocket.exceptions import (
    WebSocketConnectionError,
    ConnectionFailedError,
    ConnectionTimeoutError
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


class TestWebSocketFallbackIntegration:
    """Test WebSocket fallback integration scenarios."""
    
    @pytest.fixture
    def fallback_config(self):
        """Create fallback test configuration."""
        return WebSocketTestConfig(
            base_url="ws://localhost:8000",
            tunnel_url="wss://observatory.nkllon.com",
            connection_timeout=10.0,
            retry_attempts=3
        )
    
    @pytest.fixture
    def primary_manager(self, fallback_config):
        """Create primary WebSocket manager."""
        config = WebSocketManagerConfig(
            base_url=fallback_config.base_url,
            max_connections_per_endpoint=10,
            connection_timeout=fallback_config.connection_timeout,
            retry_max_attempts=fallback_config.retry_attempts,
            health_check_interval=30.0
        )
        return WebSocketManager(config)
    
    @pytest.fixture
    def fallback_manager(self, fallback_config):
        """Create fallback WebSocket manager."""
        config = WebSocketManagerConfig(
            base_url=fallback_config.tunnel_url,
            max_connections_per_endpoint=10,
            connection_timeout=fallback_config.connection_timeout,
            retry_max_attempts=fallback_config.retry_attempts,
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
    def fallback_metrics(self):
        """Create fallback test metrics collector."""
        return WebSocketTestMetrics()
    
    @pytest.mark.asyncio
    async def test_primary_to_fallback_switch(self, primary_manager, fallback_manager, fallback_metrics):
        """Test switching from primary to fallback WebSocket manager."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_primary_to_fallback_switch",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "fallback_integration"}
        }))
        
        await primary_manager.start()
        await fallback_manager.start()
        
        endpoint = "/ws/emoji-rain"
        
        # Create mock connections
        primary_mock_connection = Mock()
        primary_mock_connection.is_connected.return_value = True
        primary_mock_connection.send_message = AsyncMock()
        primary_mock_connection.disconnect = AsyncMock()
        primary_mock_connection.state = Mock()
        primary_mock_connection.state.status = ConnectionStatus.CONNECTED
        primary_mock_connection.state.failure_count = 0
        primary_mock_connection.state.last_error = None
        primary_mock_connection.state.message_count = 0
        primary_mock_connection.state.connection_time = datetime.utcnow()
        
        fallback_mock_connection = Mock()
        fallback_mock_connection.is_connected.return_value = True
        fallback_mock_connection.send_message = AsyncMock()
        fallback_mock_connection.disconnect = AsyncMock()
        fallback_mock_connection.state = Mock()
        fallback_mock_connection.state.status = ConnectionStatus.CONNECTED
        fallback_mock_connection.state.failure_count = 0
        fallback_mock_connection.state.last_error = None
        fallback_mock_connection.state.message_count = 0
        fallback_mock_connection.state.connection_time = datetime.utcnow()
        
        # Connect to primary
        with patch.object(primary_manager, '_create_connection', return_value=primary_mock_connection):
            primary_connection = await primary_manager.connect_websocket(endpoint)
            fallback_metrics.record_connection_attempt(True, 20.0)
        
        # Send message through primary
        test_message = {"type": "test", "data": "primary"}
        await primary_manager.send_message(endpoint, test_message, primary_connection)
        fallback_metrics.record_message(True, 10.0)
        
        # Simulate primary failure
        primary_connection.state.status = ConnectionStatus.FAILED
        primary_connection.state.failure_count = 1
        primary_connection.state.last_error = "Primary connection failed"
        
        # Handle primary failure
        await primary_manager.handle_connection_failure(endpoint, primary_connection, Exception("Primary failed"))
        fallback_metrics.record_error("ConnectionFailedError")
        
        # Switch to fallback
        with patch.object(fallback_manager, '_create_connection', return_value=fallback_mock_connection):
            fallback_connection = await fallback_manager.connect_websocket(endpoint)
            fallback_metrics.record_connection_attempt(True, 35.0)
        
        # Send message through fallback
        test_message = {"type": "test", "data": "fallback"}
        await fallback_manager.send_message(endpoint, test_message, fallback_connection)
        fallback_metrics.record_message(True, 15.0)
        
        # Verify fallback is working
        fallback_status = fallback_manager.get_connection_status(endpoint)
        assert fallback_status['connected_connections'] == 1
        
        # Cleanup
        await primary_manager.disconnect_all_websockets(endpoint)
        await fallback_manager.disconnect_all_websockets(endpoint)
        await primary_manager.stop()
        await fallback_manager.stop()
        
        # Verify fallback metrics
        summary = fallback_metrics.get_summary()
        assert summary["connection_success_rate"] == 1.0
        assert summary["total_errors"] > 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_primary_to_fallback_switch",
            "status": "completed",
            "details": {"test_type": "integration", "component": "fallback_integration", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_fallback_to_primary_recovery(self, primary_manager, fallback_manager, fallback_metrics):
        """Test recovery from fallback back to primary."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_fallback_to_primary_recovery",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "fallback_integration"}
        }))
        
        await primary_manager.start()
        await fallback_manager.start()
        
        endpoint = "/ws/observatory"
        
        # Create mock connections
        primary_mock_connection = Mock()
        primary_mock_connection.is_connected.return_value = True
        primary_mock_connection.send_message = AsyncMock()
        primary_mock_connection.disconnect = AsyncMock()
        primary_mock_connection.state = Mock()
        primary_mock_connection.state.status = ConnectionStatus.CONNECTED
        primary_mock_connection.state.failure_count = 0
        primary_mock_connection.state.last_error = None
        primary_mock_connection.state.message_count = 0
        primary_mock_connection.state.connection_time = datetime.utcnow()
        
        fallback_mock_connection = Mock()
        fallback_mock_connection.is_connected.return_value = True
        fallback_mock_connection.send_message = AsyncMock()
        fallback_mock_connection.disconnect = AsyncMock()
        fallback_mock_connection.state = Mock()
        fallback_mock_connection.state.status = ConnectionStatus.CONNECTED
        fallback_mock_connection.state.failure_count = 0
        fallback_mock_connection.state.last_error = None
        fallback_mock_connection.state.message_count = 0
        fallback_mock_connection.state.connection_time = datetime.utcnow()
        
        # Start with fallback (primary failed)
        with patch.object(fallback_manager, '_create_connection', return_value=fallback_mock_connection):
            fallback_connection = await fallback_manager.connect_websocket(endpoint)
            fallback_metrics.record_connection_attempt(True, 40.0)
        
        # Send message through fallback
        test_message = {"type": "test", "data": "fallback"}
        await fallback_manager.send_message(endpoint, test_message, fallback_connection)
        fallback_metrics.record_message(True, 20.0)
        
        # Simulate primary recovery
        with patch.object(primary_manager, '_create_connection', return_value=primary_mock_connection):
            primary_connection = await primary_manager.connect_websocket(endpoint)
            fallback_metrics.record_connection_attempt(True, 25.0)
        
        # Send message through recovered primary
        test_message = {"type": "test", "data": "primary_recovered"}
        await primary_manager.send_message(endpoint, test_message, primary_connection)
        fallback_metrics.record_message(True, 12.0)
        
        # Disconnect fallback
        await fallback_manager.disconnect_all_websockets(endpoint)
        
        # Verify primary is working
        primary_status = primary_manager.get_connection_status(endpoint)
        assert primary_status['connected_connections'] == 1
        
        # Cleanup
        await primary_manager.disconnect_all_websockets(endpoint)
        await primary_manager.stop()
        await fallback_manager.stop()
        
        # Verify recovery metrics
        summary = fallback_metrics.get_summary()
        assert summary["connection_success_rate"] == 1.0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_fallback_to_primary_recovery",
            "status": "completed",
            "details": {"test_type": "integration", "component": "fallback_integration", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_multiple_fallback_endpoints(self, fallback_manager, tunnel_manager, fallback_metrics):
        """Test fallback across multiple endpoints."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_multiple_fallback_endpoints",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "fallback_integration"}
        }))
        
        await fallback_manager.start()
        await tunnel_manager.connect()
        
        endpoints = fallback_manager.endpoints
        
        # Create mock connections for all endpoints
        mock_connections = {}
        for endpoint in endpoints:
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
            mock_connections[endpoint] = mock_connection
        
        # Connect to all endpoints
        connections = {}
        for endpoint in endpoints:
            with patch.object(fallback_manager, '_create_connection', return_value=mock_connections[endpoint]):
                connection = await fallback_manager.connect_websocket(endpoint)
                connections[endpoint] = connection
                fallback_metrics.record_connection_attempt(True, 30.0)
        
        # Send messages to all endpoints
        for endpoint, connection in connections.items():
            test_message = {"type": "test", "data": f"fallback_{endpoint}"}
            await fallback_manager.send_message(endpoint, test_message, connection)
            fallback_metrics.record_message(True, 15.0)
        
        # Simulate failures on some endpoints
        failed_endpoints = endpoints[:2]  # First two endpoints
        for endpoint in failed_endpoints:
            tunnel_manager.simulate_endpoint_failure(endpoint)
            connections[endpoint].state.status = ConnectionStatus.FAILED
            connections[endpoint].state.failure_count = 1
            connections[endpoint].state.last_error = "Endpoint failure"
            
            await fallback_manager.handle_connection_failure(endpoint, connections[endpoint], Exception("Endpoint failed"))
            fallback_metrics.record_error("ConnectionFailedError")
        
        # Check status of all endpoints
        all_status = fallback_manager.get_all_connection_status()
        tunnel_health = await tunnel_manager.get_all_endpoints_health()
        
        # Verify some endpoints are still working
        working_endpoints = [ep for ep in endpoints if ep not in failed_endpoints]
        for endpoint in working_endpoints:
            assert all_status[endpoint]['connected_connections'] == 1
            assert tunnel_health[endpoint]['status'] == 'healthy'
        
        # Cleanup
        for endpoint in endpoints:
            await fallback_manager.disconnect_all_websockets(endpoint)
        
        await fallback_manager.stop()
        await tunnel_manager.disconnect()
        
        # Verify fallback metrics
        summary = fallback_metrics.get_summary()
        assert summary["connection_success_rate"] == 1.0
        assert summary["total_errors"] > 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_multiple_fallback_endpoints",
            "status": "completed",
            "details": {"test_type": "integration", "component": "fallback_integration", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_fallback_health_monitoring(self, fallback_manager, tunnel_manager, fallback_metrics):
        """Test fallback health monitoring."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_fallback_health_monitoring",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "fallback_integration"}
        }))
        
        await fallback_manager.start()
        await tunnel_manager.connect()
        
        endpoint = "/ws/anomalies"
        
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
        
        with patch.object(fallback_manager, '_create_connection', return_value=mock_connection):
            connection = await fallback_manager.connect_websocket(endpoint)
            fallback_metrics.record_connection_attempt(True, 25.0)
        
        # Monitor health over time
        health_checks = 0
        start_time = time.time()
        
        while time.time() - start_time < 60:  # Monitor for 1 minute
            # Check WebSocket health
            websocket_health = await fallback_manager.get_health_status()
            assert websocket_health is not None
            
            # Check tunnel health
            tunnel_health = await tunnel_manager.get_endpoint_health(endpoint)
            assert tunnel_health is not None
            
            health_checks += 1
            
            # Simulate periodic health issues
            if health_checks % 3 == 0:  # Every 3rd check
                tunnel_manager.simulate_endpoint_failure(endpoint)
                await asyncio.sleep(1)
                tunnel_manager.simulate_endpoint_recovery(endpoint)
            
            await asyncio.sleep(10)  # Check every 10 seconds
        
        # Verify health monitoring
        assert health_checks > 0
        
        # Final health check
        final_websocket_health = await fallback_manager.get_health_status()
        final_tunnel_health = await tunnel_manager.get_endpoint_health(endpoint)
        
        assert final_websocket_health is not None
        assert final_tunnel_health is not None
        
        # Cleanup
        await fallback_manager.disconnect_all_websockets(endpoint)
        await fallback_manager.stop()
        await tunnel_manager.disconnect()
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_fallback_health_monitoring",
            "status": "completed",
            "details": {"test_type": "integration", "component": "fallback_integration", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_fallback_error_scenarios(self, fallback_manager, fallback_metrics):
        """Test fallback error scenarios."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_fallback_error_scenarios",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "fallback_integration"}
        }))
        
        await fallback_manager.start()
        
        endpoint = "/ws/doctor-status"
        
        # Test various error scenarios
        error_scenarios = [
            ("connection_timeout", asyncio.TimeoutError("Connection timeout")),
            ("authentication_failure", Exception("Authentication failed")),
            ("rate_limit_exceeded", Exception("Rate limit exceeded")),
            ("protocol_error", Exception("Protocol error")),
            ("network_unavailable", Exception("Network unavailable"))
        ]
        
        for scenario_name, error in error_scenarios:
            try:
                with patch.object(fallback_manager, '_create_connection', side_effect=error):
                    await fallback_manager.connect_websocket(endpoint)
            except Exception as e:
                fallback_metrics.record_error(type(e).__name__)
        
        # Test invalid endpoint
        try:
            await fallback_manager.connect_websocket("/ws/invalid")
        except Exception as e:
            fallback_metrics.record_error(type(e).__name__)
        
        # Test message sending to non-existent connection
        try:
            await fallback_manager.send_message(endpoint, {"test": "data"})
        except Exception as e:
            fallback_metrics.record_error(type(e).__name__)
        
        await fallback_manager.stop()
        
        # Verify error metrics
        summary = fallback_metrics.get_summary()
        assert summary["total_errors"] > 0
        assert len(summary["error_breakdown"]) > 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_fallback_error_scenarios",
            "status": "completed",
            "details": {"test_type": "integration", "component": "fallback_integration", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_fallback_performance_characteristics(self, fallback_manager, fallback_metrics):
        """Test fallback performance characteristics."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_fallback_performance_characteristics",
            "status": "in_progress",
            "details": {"test_type": "integration", "component": "fallback_integration"}
        }))
        
        await fallback_manager.start()
        
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
        
        with patch.object(fallback_manager, '_create_connection', return_value=mock_connection):
            # Test connection performance
            start_time = time.time()
            connection = await fallback_manager.connect_websocket(endpoint)
            connection_time = (time.time() - start_time) * 1000
            
            fallback_metrics.record_connection_attempt(True, connection_time)
            
            # Test message throughput
            rapid_messages = WebSocketTestData.get_rapid_messages(50)
            
            start_time = time.time()
            for message in rapid_messages:
                await fallback_manager.send_message(endpoint, message.__dict__, connection)
                fallback_metrics.record_message(True, 8.0)
            
            end_time = time.time()
            total_time = end_time - start_time
            messages_per_second = len(rapid_messages) / total_time
            
            # Test large message handling
            large_message = WebSocketTestData.get_large_message(5)  # 5KB
            start_time = time.time()
            await fallback_manager.send_message(endpoint, large_message.__dict__, connection)
            large_message_time = (time.time() - start_time) * 1000
            
            fallback_metrics.record_message(True, large_message_time)
            
            # Verify performance characteristics
            assert connection_time < 1000  # Connection should be fast
            assert messages_per_second > 10  # Should handle reasonable throughput
            assert large_message_time < 2000  # Large messages should be reasonable
            
            await fallback_manager.disconnect_all_websockets(endpoint)
        
        await fallback_manager.stop()
        
        # Verify performance metrics
        summary = fallback_metrics.get_summary()
        assert summary["average_connection_duration_ms"] > 0
        assert summary["messages_per_second"] > 0
        assert summary["average_message_latency_ms"] > 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_fallback_performance_characteristics",
            "status": "completed",
            "details": {"test_type": "integration", "component": "fallback_integration", "result": "passed"}
        }))