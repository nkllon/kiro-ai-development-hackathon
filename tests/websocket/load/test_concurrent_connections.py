"""Load tests for concurrent WebSocket connections."""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import time

from src.beast_mode.observatory.websocket.manager import (
    WebSocketManager,
    WebSocketManagerConfig
)
from src.beast_mode.observatory.websocket.connection import ConnectionStatus
from tests.websocket.fixtures.websocket_test_data import (
    WebSocketTestConfig,
    WebSocketTestData,
    WebSocketTestMetrics
)


class TestConcurrentWebSocketConnections:
    """Test concurrent WebSocket connection handling."""
    
    @pytest.fixture
    def load_test_config(self):
        """Create load test configuration."""
        return WebSocketTestConfig(
            base_url="ws://localhost:8000",
            max_connections=200,
            connection_timeout=30.0,
            retry_attempts=3
        )
    
    @pytest.fixture
    def websocket_manager(self, load_test_config):
        """Create WebSocket manager for load testing."""
        config = WebSocketManagerConfig(
            base_url=load_test_config.base_url,
            max_connections_per_endpoint=load_test_config.max_connections,
            connection_timeout=load_test_config.connection_timeout,
            retry_max_attempts=load_test_config.retry_attempts,
            health_check_interval=60.0
        )
        return WebSocketManager(config)
    
    @pytest.fixture
    def load_test_metrics(self):
        """Create load test metrics collector."""
        return WebSocketTestMetrics()
    
    @pytest.mark.asyncio
    async def test_light_load_concurrent_connections(self, websocket_manager, load_test_metrics):
        """Test light load with 10 concurrent connections."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_light_load_concurrent_connections",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "concurrent_connections", "load_level": "light"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/emoji-rain"
        concurrent_connections = 10
        
        # Create mock connections
        mock_connections = []
        for i in range(concurrent_connections):
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
            mock_connections.append(mock_connection)
        
        async def connect_single():
            """Connect a single WebSocket."""
            start_time = time.time()
            try:
                with patch.object(websocket_manager, '_create_connection', return_value=mock_connections.pop()):
                    connection = await websocket_manager.connect_websocket(endpoint)
                    connection_time = (time.time() - start_time) * 1000
                    load_test_metrics.record_connection_attempt(True, connection_time)
                    return connection
            except Exception as e:
                connection_time = (time.time() - start_time) * 1000
                load_test_metrics.record_connection_attempt(False, connection_time)
                load_test_metrics.record_error(type(e).__name__)
                return None
        
        # Connect concurrently
        start_time = time.time()
        connections = await asyncio.gather(*[connect_single() for _ in range(concurrent_connections)])
        total_time = time.time() - start_time
        
        # Verify connections
        successful_connections = [conn for conn in connections if conn is not None]
        assert len(successful_connections) == concurrent_connections
        
        # Check connection status
        status = websocket_manager.get_connection_status(endpoint)
        assert status['total_connections'] == concurrent_connections
        assert status['connected_connections'] == concurrent_connections
        
        # Test concurrent message sending
        async def send_messages(connection):
            """Send messages through a connection."""
            test_messages = WebSocketTestData.get_test_messages(10)
            for message in test_messages:
                try:
                    await websocket_manager.send_message(endpoint, message.__dict__, connection)
                    load_test_metrics.record_message(True, 10.0)
                except Exception as e:
                    load_test_metrics.record_error(type(e).__name__)
        
        # Send messages concurrently
        start_time = time.time()
        await asyncio.gather(*[send_messages(conn) for conn in successful_connections])
        message_time = time.time() - start_time
        
        # Disconnect all connections
        await websocket_manager.disconnect_all_websockets(endpoint)
        await websocket_manager.stop()
        
        # Verify load test results
        summary = load_test_metrics.get_summary()
        assert summary["connection_success_rate"] == 1.0
        assert summary["messages_per_second"] > 0
        assert total_time < 10.0  # Should complete quickly
        assert message_time < 5.0  # Messages should be fast
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_light_load_concurrent_connections",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "concurrent_connections", 
                "load_level": "light",
                "connections": concurrent_connections,
                "success_rate": summary["connection_success_rate"],
                "total_time": total_time,
                "message_time": message_time
            }
        }))
    
    @pytest.mark.asyncio
    async def test_medium_load_concurrent_connections(self, websocket_manager, load_test_metrics):
        """Test medium load with 50 concurrent connections."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_medium_load_concurrent_connections",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "concurrent_connections", "load_level": "medium"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/observatory"
        concurrent_connections = 50
        
        # Create mock connections
        mock_connections = []
        for i in range(concurrent_connections):
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
            mock_connections.append(mock_connection)
        
        async def connect_single():
            """Connect a single WebSocket."""
            start_time = time.time()
            try:
                with patch.object(websocket_manager, '_create_connection', return_value=mock_connections.pop()):
                    connection = await websocket_manager.connect_websocket(endpoint)
                    connection_time = (time.time() - start_time) * 1000
                    load_test_metrics.record_connection_attempt(True, connection_time)
                    return connection
            except Exception as e:
                connection_time = (time.time() - start_time) * 1000
                load_test_metrics.record_connection_attempt(False, connection_time)
                load_test_metrics.record_error(type(e).__name__)
                return None
        
        # Connect concurrently with batching to avoid overwhelming
        batch_size = 10
        all_connections = []
        
        start_time = time.time()
        for i in range(0, concurrent_connections, batch_size):
            batch_connections = await asyncio.gather(
                *[connect_single() for _ in range(min(batch_size, concurrent_connections - i))],
                return_exceptions=True
            )
            all_connections.extend(batch_connections)
            await asyncio.sleep(0.1)  # Small delay between batches
        
        total_time = time.time() - start_time
        
        # Verify connections
        successful_connections = [conn for conn in all_connections if conn is not None and not isinstance(conn, Exception)]
        assert len(successful_connections) == concurrent_connections
        
        # Check connection status
        status = websocket_manager.get_connection_status(endpoint)
        assert status['total_connections'] == concurrent_connections
        assert status['connected_connections'] == concurrent_connections
        
        # Test concurrent message sending
        async def send_messages(connection):
            """Send messages through a connection."""
            test_messages = WebSocketTestData.get_test_messages(5)
            for message in test_messages:
                try:
                    await websocket_manager.send_message(endpoint, message.__dict__, connection)
                    load_test_metrics.record_message(True, 15.0)
                except Exception as e:
                    load_test_metrics.record_error(type(e).__name__)
        
        # Send messages concurrently
        start_time = time.time()
        await asyncio.gather(*[send_messages(conn) for conn in successful_connections])
        message_time = time.time() - start_time
        
        # Disconnect all connections
        await websocket_manager.disconnect_all_websockets(endpoint)
        await websocket_manager.stop()
        
        # Verify load test results
        summary = load_test_metrics.get_summary()
        assert summary["connection_success_rate"] == 1.0
        assert summary["messages_per_second"] > 0
        assert total_time < 30.0  # Should complete within reasonable time
        assert message_time < 10.0  # Messages should be fast
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_medium_load_concurrent_connections",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "concurrent_connections", 
                "load_level": "medium",
                "connections": concurrent_connections,
                "success_rate": summary["connection_success_rate"],
                "total_time": total_time,
                "message_time": message_time
            }
        }))
    
    @pytest.mark.asyncio
    async def test_heavy_load_concurrent_connections(self, websocket_manager, load_test_metrics):
        """Test heavy load with 100 concurrent connections."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_heavy_load_concurrent_connections",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "concurrent_connections", "load_level": "heavy"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/anomalies"
        concurrent_connections = 100
        
        # Create mock connections
        mock_connections = []
        for i in range(concurrent_connections):
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
            mock_connections.append(mock_connection)
        
        async def connect_single():
            """Connect a single WebSocket."""
            start_time = time.time()
            try:
                with patch.object(websocket_manager, '_create_connection', return_value=mock_connections.pop()):
                    connection = await websocket_manager.connect_websocket(endpoint)
                    connection_time = (time.time() - start_time) * 1000
                    load_test_metrics.record_connection_attempt(True, connection_time)
                    return connection
            except Exception as e:
                connection_time = (time.time() - start_time) * 1000
                load_test_metrics.record_connection_attempt(False, connection_time)
                load_test_metrics.record_error(type(e).__name__)
                return None
        
        # Connect concurrently with smaller batches for heavy load
        batch_size = 5
        all_connections = []
        
        start_time = time.time()
        for i in range(0, concurrent_connections, batch_size):
            batch_connections = await asyncio.gather(
                *[connect_single() for _ in range(min(batch_size, concurrent_connections - i))],
                return_exceptions=True
            )
            all_connections.extend(batch_connections)
            await asyncio.sleep(0.05)  # Small delay between batches
        
        total_time = time.time() - start_time
        
        # Verify connections
        successful_connections = [conn for conn in all_connections if conn is not None and not isinstance(conn, Exception)]
        assert len(successful_connections) == concurrent_connections
        
        # Check connection status
        status = websocket_manager.get_connection_status(endpoint)
        assert status['total_connections'] == concurrent_connections
        assert status['connected_connections'] == concurrent_connections
        
        # Test concurrent message sending with batching
        async def send_messages(connection):
            """Send messages through a connection."""
            test_messages = WebSocketTestData.get_test_messages(3)
            for message in test_messages:
                try:
                    await websocket_manager.send_message(endpoint, message.__dict__, connection)
                    load_test_metrics.record_message(True, 20.0)
                except Exception as e:
                    load_test_metrics.record_error(type(e).__name__)
        
        # Send messages concurrently in batches
        start_time = time.time()
        message_batch_size = 20
        for i in range(0, len(successful_connections), message_batch_size):
            batch = successful_connections[i:i + message_batch_size]
            await asyncio.gather(*[send_messages(conn) for conn in batch])
            await asyncio.sleep(0.01)  # Small delay between batches
        
        message_time = time.time() - start_time
        
        # Disconnect all connections
        await websocket_manager.disconnect_all_websockets(endpoint)
        await websocket_manager.stop()
        
        # Verify load test results
        summary = load_test_metrics.get_summary()
        assert summary["connection_success_rate"] == 1.0
        assert summary["messages_per_second"] > 0
        assert total_time < 60.0  # Should complete within reasonable time
        assert message_time < 20.0  # Messages should be fast
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_heavy_load_concurrent_connections",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "concurrent_connections", 
                "load_level": "heavy",
                "connections": concurrent_connections,
                "success_rate": summary["connection_success_rate"],
                "total_time": total_time,
                "message_time": message_time
            }
        }))
    
    @pytest.mark.asyncio
    async def test_stress_test_concurrent_connections(self, websocket_manager, load_test_metrics):
        """Test stress test with 200 concurrent connections."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_stress_test_concurrent_connections",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "concurrent_connections", "load_level": "stress"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/doctor-status"
        concurrent_connections = 200
        
        # Create mock connections
        mock_connections = []
        for i in range(concurrent_connections):
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
            mock_connections.append(mock_connection)
        
        async def connect_single():
            """Connect a single WebSocket."""
            start_time = time.time()
            try:
                with patch.object(websocket_manager, '_create_connection', return_value=mock_connections.pop()):
                    connection = await websocket_manager.connect_websocket(endpoint)
                    connection_time = (time.time() - start_time) * 1000
                    load_test_metrics.record_connection_attempt(True, connection_time)
                    return connection
            except Exception as e:
                connection_time = (time.time() - start_time) * 1000
                load_test_metrics.record_connection_attempt(False, connection_time)
                load_test_metrics.record_error(type(e).__name__)
                return None
        
        # Connect concurrently with very small batches for stress test
        batch_size = 3
        all_connections = []
        
        start_time = time.time()
        for i in range(0, concurrent_connections, batch_size):
            batch_connections = await asyncio.gather(
                *[connect_single() for _ in range(min(batch_size, concurrent_connections - i))],
                return_exceptions=True
            )
            all_connections.extend(batch_connections)
            await asyncio.sleep(0.02)  # Small delay between batches
        
        total_time = time.time() - start_time
        
        # Verify connections
        successful_connections = [conn for conn in all_connections if conn is not None and not isinstance(conn, Exception)]
        assert len(successful_connections) == concurrent_connections
        
        # Check connection status
        status = websocket_manager.get_connection_status(endpoint)
        assert status['total_connections'] == concurrent_connections
        assert status['connected_connections'] == concurrent_connections
        
        # Test concurrent message sending with very small batches
        async def send_messages(connection):
            """Send messages through a connection."""
            test_messages = WebSocketTestData.get_test_messages(2)
            for message in test_messages:
                try:
                    await websocket_manager.send_message(endpoint, message.__dict__, connection)
                    load_test_metrics.record_message(True, 25.0)
                except Exception as e:
                    load_test_metrics.record_error(type(e).__name__)
        
        # Send messages concurrently in very small batches
        start_time = time.time()
        message_batch_size = 10
        for i in range(0, len(successful_connections), message_batch_size):
            batch = successful_connections[i:i + message_batch_size]
            await asyncio.gather(*[send_messages(conn) for conn in batch])
            await asyncio.sleep(0.005)  # Very small delay between batches
        
        message_time = time.time() - start_time
        
        # Disconnect all connections
        await websocket_manager.disconnect_all_websockets(endpoint)
        await websocket_manager.stop()
        
        # Verify load test results
        summary = load_test_metrics.get_summary()
        assert summary["connection_success_rate"] == 1.0
        assert summary["messages_per_second"] > 0
        assert total_time < 120.0  # Should complete within reasonable time
        assert message_time < 30.0  # Messages should be fast
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_stress_test_concurrent_connections",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "concurrent_connections", 
                "load_level": "stress",
                "connections": concurrent_connections,
                "success_rate": summary["connection_success_rate"],
                "total_time": total_time,
                "message_time": message_time
            }
        }))
    
    @pytest.mark.asyncio
    async def test_mixed_load_multiple_endpoints(self, websocket_manager, load_test_metrics):
        """Test mixed load across multiple endpoints."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_mixed_load_multiple_endpoints",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "concurrent_connections", "load_level": "mixed"}
        }))
        
        await websocket_manager.start()
        
        # Distribute connections across endpoints
        endpoints = websocket_manager.endpoints
        connections_per_endpoint = 25
        total_connections = len(endpoints) * connections_per_endpoint
        
        async def connect_to_endpoint(endpoint):
            """Connect to a specific endpoint."""
            mock_connections = []
            for i in range(connections_per_endpoint):
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
                mock_connections.append(mock_connection)
            
            connections = []
            for mock_conn in mock_connections:
                start_time = time.time()
                try:
                    with patch.object(websocket_manager, '_create_connection', return_value=mock_conn):
                        connection = await websocket_manager.connect_websocket(endpoint)
                        connection_time = (time.time() - start_time) * 1000
                        load_test_metrics.record_connection_attempt(True, connection_time)
                        connections.append(connection)
                except Exception as e:
                    connection_time = (time.time() - start_time) * 1000
                    load_test_metrics.record_connection_attempt(False, connection_time)
                    load_test_metrics.record_error(type(e).__name__)
            
            return connections
        
        # Connect to all endpoints concurrently
        start_time = time.time()
        all_endpoint_connections = await asyncio.gather(
            *[connect_to_endpoint(endpoint) for endpoint in endpoints],
            return_exceptions=True
        )
        total_time = time.time() - start_time
        
        # Verify connections
        total_successful = 0
        for connections in all_endpoint_connections:
            if not isinstance(connections, Exception):
                total_successful += len(connections)
        
        assert total_successful == total_connections
        
        # Test concurrent message sending across all endpoints
        async def send_messages_to_endpoint(endpoint, connections):
            """Send messages to all connections for an endpoint."""
            if isinstance(connections, Exception):
                return
            
            async def send_to_connection(connection):
                test_messages = WebSocketTestData.get_test_messages(3)
                for message in test_messages:
                    try:
                        await websocket_manager.send_message(endpoint, message.__dict__, connection)
                        load_test_metrics.record_message(True, 15.0)
                    except Exception as e:
                        load_test_metrics.record_error(type(e).__name__)
            
            await asyncio.gather(*[send_to_connection(conn) for conn in connections])
        
        # Send messages concurrently across all endpoints
        start_time = time.time()
        await asyncio.gather(
            *[send_messages_to_endpoint(endpoint, connections) 
              for endpoint, connections in zip(endpoints, all_endpoint_connections)],
            return_exceptions=True
        )
        message_time = time.time() - start_time
        
        # Disconnect all connections
        for endpoint in endpoints:
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        await websocket_manager.stop()
        
        # Verify load test results
        summary = load_test_metrics.get_summary()
        assert summary["connection_success_rate"] == 1.0
        assert summary["messages_per_second"] > 0
        assert total_time < 60.0  # Should complete within reasonable time
        assert message_time < 15.0  # Messages should be fast
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_mixed_load_multiple_endpoints",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "concurrent_connections", 
                "load_level": "mixed",
                "total_connections": total_connections,
                "endpoints": len(endpoints),
                "success_rate": summary["connection_success_rate"],
                "total_time": total_time,
                "message_time": message_time
            }
        }))