"""Load tests for WebSocket message throughput."""

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


class TestWebSocketMessageThroughput:
    """Test WebSocket message throughput under load."""
    
    @pytest.fixture
    def throughput_config(self):
        """Create throughput test configuration."""
        return WebSocketTestConfig(
            base_url="ws://localhost:8000",
            max_connections=50,
            connection_timeout=30.0,
            message_timeout=5.0
        )
    
    @pytest.fixture
    def websocket_manager(self, throughput_config):
        """Create WebSocket manager for throughput testing."""
        config = WebSocketManagerConfig(
            base_url=throughput_config.base_url,
            max_connections_per_endpoint=throughput_config.max_connections,
            connection_timeout=throughput_config.connection_timeout,
            retry_max_attempts=3,
            health_check_interval=60.0
        )
        return WebSocketManager(config)
    
    @pytest.fixture
    def throughput_metrics(self):
        """Create throughput test metrics collector."""
        return WebSocketTestMetrics()
    
    @pytest.mark.asyncio
    async def test_light_message_throughput(self, websocket_manager, throughput_metrics):
        """Test light message throughput (100 messages/second)."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_light_message_throughput",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "message_throughput", "load_level": "light"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/emoji-rain"
        target_messages_per_second = 100
        test_duration = 10  # seconds
        
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
            connection = await websocket_manager.connect_websocket(endpoint)
            
            # Send messages at target rate
            messages_sent = 0
            start_time = time.time()
            
            while time.time() - start_time < test_duration:
                message_start = time.time()
                
                test_message = WebSocketTestData.get_test_messages(1)[0]
                await websocket_manager.send_message(endpoint, test_message.__dict__, connection)
                throughput_metrics.record_message(True, 5.0)
                messages_sent += 1
                
                # Calculate delay to maintain target rate
                elapsed = time.time() - message_start
                target_interval = 1.0 / target_messages_per_second
                if elapsed < target_interval:
                    await asyncio.sleep(target_interval - elapsed)
            
            total_time = time.time() - start_time
            actual_rate = messages_sent / total_time
            
            # Verify throughput
            assert actual_rate >= target_messages_per_second * 0.9  # Allow 10% tolerance
            assert messages_sent > 0
            
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        await websocket_manager.stop()
        
        # Verify metrics
        summary = throughput_metrics.get_summary()
        assert summary["messages_per_second"] >= target_messages_per_second * 0.9
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_light_message_throughput",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "message_throughput", 
                "load_level": "light",
                "target_rate": target_messages_per_second,
                "actual_rate": actual_rate,
                "messages_sent": messages_sent,
                "test_duration": total_time
            }
        }))
    
    @pytest.mark.asyncio
    async def test_medium_message_throughput(self, websocket_manager, throughput_metrics):
        """Test medium message throughput (500 messages/second)."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_medium_message_throughput",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "message_throughput", "load_level": "medium"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/observatory"
        target_messages_per_second = 500
        test_duration = 15  # seconds
        
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
            connection = await websocket_manager.connect_websocket(endpoint)
            
            # Send messages at target rate
            messages_sent = 0
            start_time = time.time()
            
            while time.time() - start_time < test_duration:
                message_start = time.time()
                
                test_message = WebSocketTestData.get_test_messages(1)[0]
                await websocket_manager.send_message(endpoint, test_message.__dict__, connection)
                throughput_metrics.record_message(True, 3.0)
                messages_sent += 1
                
                # Calculate delay to maintain target rate
                elapsed = time.time() - message_start
                target_interval = 1.0 / target_messages_per_second
                if elapsed < target_interval:
                    await asyncio.sleep(target_interval - elapsed)
            
            total_time = time.time() - start_time
            actual_rate = messages_sent / total_time
            
            # Verify throughput
            assert actual_rate >= target_messages_per_second * 0.8  # Allow 20% tolerance for higher load
            assert messages_sent > 0
            
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        await websocket_manager.stop()
        
        # Verify metrics
        summary = throughput_metrics.get_summary()
        assert summary["messages_per_second"] >= target_messages_per_second * 0.8
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_medium_message_throughput",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "message_throughput", 
                "load_level": "medium",
                "target_rate": target_messages_per_second,
                "actual_rate": actual_rate,
                "messages_sent": messages_sent,
                "test_duration": total_time
            }
        }))
    
    @pytest.mark.asyncio
    async def test_heavy_message_throughput(self, websocket_manager, throughput_metrics):
        """Test heavy message throughput (1000 messages/second)."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_heavy_message_throughput",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "message_throughput", "load_level": "heavy"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/anomalies"
        target_messages_per_second = 1000
        test_duration = 20  # seconds
        
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
            connection = await websocket_manager.connect_websocket(endpoint)
            
            # Send messages at target rate
            messages_sent = 0
            start_time = time.time()
            
            while time.time() - start_time < test_duration:
                message_start = time.time()
                
                test_message = WebSocketTestData.get_test_messages(1)[0]
                await websocket_manager.send_message(endpoint, test_message.__dict__, connection)
                throughput_metrics.record_message(True, 2.0)
                messages_sent += 1
                
                # Calculate delay to maintain target rate
                elapsed = time.time() - message_start
                target_interval = 1.0 / target_messages_per_second
                if elapsed < target_interval:
                    await asyncio.sleep(target_interval - elapsed)
            
            total_time = time.time() - start_time
            actual_rate = messages_sent / total_time
            
            # Verify throughput
            assert actual_rate >= target_messages_per_second * 0.7  # Allow 30% tolerance for heavy load
            assert messages_sent > 0
            
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        await websocket_manager.stop()
        
        # Verify metrics
        summary = throughput_metrics.get_summary()
        assert summary["messages_per_second"] >= target_messages_per_second * 0.7
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_heavy_message_throughput",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "message_throughput", 
                "load_level": "heavy",
                "target_rate": target_messages_per_second,
                "actual_rate": actual_rate,
                "messages_sent": messages_sent,
                "test_duration": total_time
            }
        }))
    
    @pytest.mark.asyncio
    async def test_burst_message_throughput(self, websocket_manager, throughput_metrics):
        """Test burst message throughput (2000 messages/second)."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_burst_message_throughput",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "message_throughput", "load_level": "burst"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/doctor-status"
        burst_messages_per_second = 2000
        burst_duration = 5  # seconds
        
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
            connection = await websocket_manager.connect_websocket(endpoint)
            
            # Send burst of messages
            messages_sent = 0
            start_time = time.time()
            
            while time.time() - start_time < burst_duration:
                message_start = time.time()
                
                test_message = WebSocketTestData.get_test_messages(1)[0]
                await websocket_manager.send_message(endpoint, test_message.__dict__, connection)
                throughput_metrics.record_message(True, 1.0)
                messages_sent += 1
                
                # Calculate delay to maintain burst rate
                elapsed = time.time() - message_start
                target_interval = 1.0 / burst_messages_per_second
                if elapsed < target_interval:
                    await asyncio.sleep(target_interval - elapsed)
            
            total_time = time.time() - start_time
            actual_rate = messages_sent / total_time
            
            # Verify burst throughput
            assert actual_rate >= burst_messages_per_second * 0.6  # Allow 40% tolerance for burst
            assert messages_sent > 0
            
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        await websocket_manager.stop()
        
        # Verify metrics
        summary = throughput_metrics.get_summary()
        assert summary["messages_per_second"] >= burst_messages_per_second * 0.6
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_burst_message_throughput",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "message_throughput", 
                "load_level": "burst",
                "target_rate": burst_messages_per_second,
                "actual_rate": actual_rate,
                "messages_sent": messages_sent,
                "burst_duration": total_time
            }
        }))
    
    @pytest.mark.asyncio
    async def test_concurrent_message_throughput(self, websocket_manager, throughput_metrics):
        """Test concurrent message throughput across multiple connections."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_concurrent_message_throughput",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "message_throughput", "load_level": "concurrent"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/emoji-rain"
        concurrent_connections = 10
        messages_per_connection = 50
        total_messages = concurrent_connections * messages_per_connection
        
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
        
        async def send_messages_for_connection(connection):
            """Send messages for a single connection."""
            test_messages = WebSocketTestData.get_test_messages(messages_per_connection)
            for message in test_messages:
                try:
                    await websocket_manager.send_message(endpoint, message.__dict__, connection)
                    throughput_metrics.record_message(True, 8.0)
                except Exception as e:
                    throughput_metrics.record_error(type(e).__name__)
        
        # Connect all connections
        connections = []
        for mock_conn in mock_connections:
            with patch.object(websocket_manager, '_create_connection', return_value=mock_conn):
                connection = await websocket_manager.connect_websocket(endpoint)
                connections.append(connection)
        
        # Send messages concurrently
        start_time = time.time()
        await asyncio.gather(*[send_messages_for_connection(conn) for conn in connections])
        total_time = time.time() - start_time
        
        # Calculate throughput
        actual_rate = total_messages / total_time
        
        # Verify concurrent throughput
        assert actual_rate > 100  # Should handle at least 100 messages/second
        assert total_time < 30.0  # Should complete within reasonable time
        
        # Disconnect all connections
        await websocket_manager.disconnect_all_websockets(endpoint)
        await websocket_manager.stop()
        
        # Verify metrics
        summary = throughput_metrics.get_summary()
        assert summary["messages_per_second"] > 100
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_concurrent_message_throughput",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "message_throughput", 
                "load_level": "concurrent",
                "concurrent_connections": concurrent_connections,
                "total_messages": total_messages,
                "actual_rate": actual_rate,
                "total_time": total_time
            }
        }))
    
    @pytest.mark.asyncio
    async def test_large_message_throughput(self, websocket_manager, throughput_metrics):
        """Test throughput with large messages."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_large_message_throughput",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "message_throughput", "load_level": "large_messages"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/observatory"
        large_message_size_kb = 100  # 100KB messages
        message_count = 20
        
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
            connection = await websocket_manager.connect_websocket(endpoint)
            
            # Send large messages
            start_time = time.time()
            
            for i in range(message_count):
                large_message = WebSocketTestData.get_large_message(large_message_size_kb)
                message_start = time.time()
                
                await websocket_manager.send_message(endpoint, large_message.__dict__, connection)
                
                message_time = (time.time() - message_start) * 1000
                throughput_metrics.record_message(True, message_time)
            
            total_time = time.time() - start_time
            actual_rate = message_count / total_time
            
            # Verify large message throughput
            assert actual_rate > 0.5  # Should handle at least 0.5 large messages/second
            assert total_time < 60.0  # Should complete within reasonable time
            
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        await websocket_manager.stop()
        
        # Verify metrics
        summary = throughput_metrics.get_summary()
        assert summary["messages_per_second"] > 0
        assert summary["average_message_latency_ms"] > 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_large_message_throughput",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "message_throughput", 
                "load_level": "large_messages",
                "message_size_kb": large_message_size_kb,
                "message_count": message_count,
                "actual_rate": actual_rate,
                "total_time": total_time
            }
        }))
    
    @pytest.mark.asyncio
    async def test_sustained_message_throughput(self, websocket_manager, throughput_metrics):
        """Test sustained message throughput over extended period."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_sustained_message_throughput",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "message_throughput", "load_level": "sustained"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/anomalies"
        sustained_rate = 200  # messages per second
        sustained_duration = 60  # 1 minute
        
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
            connection = await websocket_manager.connect_websocket(endpoint)
            
            # Send messages at sustained rate
            messages_sent = 0
            start_time = time.time()
            
            while time.time() - start_time < sustained_duration:
                message_start = time.time()
                
                test_message = WebSocketTestData.get_test_messages(1)[0]
                await websocket_manager.send_message(endpoint, test_message.__dict__, connection)
                throughput_metrics.record_message(True, 4.0)
                messages_sent += 1
                
                # Calculate delay to maintain sustained rate
                elapsed = time.time() - message_start
                target_interval = 1.0 / sustained_rate
                if elapsed < target_interval:
                    await asyncio.sleep(target_interval - elapsed)
            
            total_time = time.time() - start_time
            actual_rate = messages_sent / total_time
            
            # Verify sustained throughput
            assert actual_rate >= sustained_rate * 0.8  # Allow 20% tolerance
            assert messages_sent > 0
            assert total_time >= sustained_duration * 0.9  # Should run for most of the duration
            
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        await websocket_manager.stop()
        
        # Verify metrics
        summary = throughput_metrics.get_summary()
        assert summary["messages_per_second"] >= sustained_rate * 0.8
        assert summary["test_duration_seconds"] >= sustained_duration * 0.9
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_sustained_message_throughput",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "message_throughput", 
                "load_level": "sustained",
                "sustained_rate": sustained_rate,
                "actual_rate": actual_rate,
                "messages_sent": messages_sent,
                "sustained_duration": total_time
            }
        }))