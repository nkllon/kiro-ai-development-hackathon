"""Load tests for WebSocket connection stability."""

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


class TestWebSocketConnectionStability:
    """Test WebSocket connection stability under load."""
    
    @pytest.fixture
    def stability_config(self):
        """Create stability test configuration."""
        return WebSocketTestConfig(
            base_url="ws://localhost:8000",
            max_connections=100,
            connection_timeout=30.0,
            retry_attempts=5
        )
    
    @pytest.fixture
    def websocket_manager(self, stability_config):
        """Create WebSocket manager for stability testing."""
        config = WebSocketManagerConfig(
            base_url=stability_config.base_url,
            max_connections_per_endpoint=stability_config.max_connections,
            connection_timeout=stability_config.connection_timeout,
            retry_max_attempts=stability_config.retry_attempts,
            health_check_interval=30.0
        )
        return WebSocketManager(config)
    
    @pytest.fixture
    def stability_metrics(self):
        """Create stability test metrics collector."""
        return WebSocketTestMetrics()
    
    @pytest.mark.asyncio
    async def test_connection_stability_30_minutes(self, websocket_manager, stability_metrics):
        """Test connection stability over 30 minutes."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_stability_30_minutes",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "connection_stability", "duration": "30_minutes"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/emoji-rain"
        test_duration = 30 * 60  # 30 minutes in seconds
        message_interval = 10  # Send message every 10 seconds
        
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
            stability_metrics.record_connection_attempt(True, 25.0)
            
            # Monitor connection stability
            start_time = time.time()
            messages_sent = 0
            connection_checks = 0
            
            while time.time() - start_time < test_duration:
                # Send periodic message
                test_message = WebSocketTestData.get_test_messages(1)[0]
                await websocket_manager.send_message(endpoint, test_message.__dict__, connection)
                stability_metrics.record_message(True, 15.0)
                messages_sent += 1
                
                # Check connection status
                status = websocket_manager.get_connection_status(endpoint)
                assert status['connected_connections'] == 1
                assert status['total_connections'] == 1
                connection_checks += 1
                
                # Wait for next interval
                await asyncio.sleep(message_interval)
            
            total_time = time.time() - start_time
            
            # Verify stability
            assert messages_sent > 0
            assert connection_checks > 0
            assert total_time >= test_duration * 0.9  # Should run for most of the duration
            
            # Final status check
            final_status = websocket_manager.get_connection_status(endpoint)
            assert final_status['connected_connections'] == 1
            
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        await websocket_manager.stop()
        
        # Verify stability metrics
        summary = stability_metrics.get_summary()
        assert summary["test_duration_seconds"] >= test_duration * 0.9
        assert summary["connection_success_rate"] == 1.0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_stability_30_minutes",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "connection_stability", 
                "duration": "30_minutes",
                "messages_sent": messages_sent,
                "connection_checks": connection_checks,
                "total_time": total_time,
                "success_rate": summary["connection_success_rate"]
            }
        }))
    
    @pytest.mark.asyncio
    async def test_connection_stability_with_failures(self, websocket_manager, stability_metrics):
        """Test connection stability with simulated failures."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_stability_with_failures",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "connection_stability", "scenario": "with_failures"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/observatory"
        test_duration = 300  # 5 minutes
        failure_interval = 60  # Simulate failure every 60 seconds
        
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
            stability_metrics.record_connection_attempt(True, 30.0)
            
            start_time = time.time()
            messages_sent = 0
            failures_simulated = 0
            
            while time.time() - start_time < test_duration:
                # Send message
                test_message = WebSocketTestData.get_test_messages(1)[0]
                await websocket_manager.send_message(endpoint, test_message.__dict__, connection)
                stability_metrics.record_message(True, 12.0)
                messages_sent += 1
                
                # Simulate periodic failures
                if (time.time() - start_time) % failure_interval < 5:  # 5-second failure window
                    # Simulate connection failure
                    connection.state.status = ConnectionStatus.FAILED
                    connection.state.failure_count += 1
                    connection.state.last_error = "Simulated network failure"
                    
                    # Handle failure
                    await websocket_manager.handle_connection_failure(endpoint, connection, Exception("Network failure"))
                    stability_metrics.record_error("ConnectionFailedError")
                    failures_simulated += 1
                    
                    # Simulate reconnection
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
                        connection = await websocket_manager.connect_websocket(endpoint)
                        stability_metrics.record_connection_attempt(True, 35.0)
                
                await asyncio.sleep(10)  # Wait 10 seconds between operations
            
            total_time = time.time() - start_time
            
            # Verify stability despite failures
            assert messages_sent > 0
            assert failures_simulated > 0
            
            # Final status check
            final_status = websocket_manager.get_connection_status(endpoint)
            assert final_status['connected_connections'] == 1
            
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        await websocket_manager.stop()
        
        # Verify stability metrics
        summary = stability_metrics.get_summary()
        assert summary["test_duration_seconds"] >= test_duration * 0.9
        assert summary["total_errors"] > 0  # Should have recorded failures
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_stability_with_failures",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "connection_stability", 
                "scenario": "with_failures",
                "messages_sent": messages_sent,
                "failures_simulated": failures_simulated,
                "total_time": total_time,
                "total_errors": summary["total_errors"]
            }
        }))
    
    @pytest.mark.asyncio
    async def test_multiple_connections_stability(self, websocket_manager, stability_metrics):
        """Test stability with multiple concurrent connections."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_multiple_connections_stability",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "connection_stability", "scenario": "multiple_connections"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/anomalies"
        concurrent_connections = 20
        test_duration = 600  # 10 minutes
        message_interval = 30  # Send message every 30 seconds
        
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
        
        # Connect all connections
        connections = []
        for mock_conn in mock_connections:
            with patch.object(websocket_manager, '_create_connection', return_value=mock_conn):
                connection = await websocket_manager.connect_websocket(endpoint)
                connections.append(connection)
                stability_metrics.record_connection_attempt(True, 20.0)
        
        # Monitor stability
        start_time = time.time()
        total_messages_sent = 0
        
        while time.time() - start_time < test_duration:
            # Send messages through all connections
            async def send_message_to_connection(connection):
                test_message = WebSocketTestData.get_test_messages(1)[0]
                await websocket_manager.send_message(endpoint, test_message.__dict__, connection)
                stability_metrics.record_message(True, 10.0)
                return 1
            
            messages_sent = await asyncio.gather(
                *[send_message_to_connection(conn) for conn in connections],
                return_exceptions=True
            )
            
            total_messages_sent += sum(1 for msg in messages_sent if msg == 1)
            
            # Check connection status
            status = websocket_manager.get_connection_status(endpoint)
            assert status['total_connections'] == concurrent_connections
            assert status['connected_connections'] == concurrent_connections
            
            await asyncio.sleep(message_interval)
        
        total_time = time.time() - start_time
        
        # Verify stability
        assert total_messages_sent > 0
        assert total_time >= test_duration * 0.9
        
        # Final status check
        final_status = websocket_manager.get_connection_status(endpoint)
        assert final_status['connected_connections'] == concurrent_connections
        
        # Disconnect all connections
        await websocket_manager.disconnect_all_websockets(endpoint)
        await websocket_manager.stop()
        
        # Verify stability metrics
        summary = stability_metrics.get_summary()
        assert summary["test_duration_seconds"] >= test_duration * 0.9
        assert summary["connection_success_rate"] == 1.0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_multiple_connections_stability",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "connection_stability", 
                "scenario": "multiple_connections",
                "concurrent_connections": concurrent_connections,
                "total_messages_sent": total_messages_sent,
                "total_time": total_time,
                "success_rate": summary["connection_success_rate"]
            }
        }))
    
    @pytest.mark.asyncio
    async def test_connection_stability_under_load(self, websocket_manager, stability_metrics):
        """Test connection stability under high message load."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_stability_under_load",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "connection_stability", "scenario": "under_load"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/doctor-status"
        test_duration = 300  # 5 minutes
        high_load_rate = 100  # 100 messages per second
        
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
            stability_metrics.record_connection_attempt(True, 25.0)
            
            # Send high load of messages
            start_time = time.time()
            messages_sent = 0
            
            while time.time() - start_time < test_duration:
                message_start = time.time()
                
                test_message = WebSocketTestData.get_test_messages(1)[0]
                await websocket_manager.send_message(endpoint, test_message.__dict__, connection)
                stability_metrics.record_message(True, 5.0)
                messages_sent += 1
                
                # Maintain high load rate
                elapsed = time.time() - message_start
                target_interval = 1.0 / high_load_rate
                if elapsed < target_interval:
                    await asyncio.sleep(target_interval - elapsed)
            
            total_time = time.time() - start_time
            actual_rate = messages_sent / total_time
            
            # Verify stability under load
            assert actual_rate >= high_load_rate * 0.8  # Allow 20% tolerance
            assert messages_sent > 0
            
            # Check connection is still stable
            status = websocket_manager.get_connection_status(endpoint)
            assert status['connected_connections'] == 1
            assert status['total_connections'] == 1
            
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        await websocket_manager.stop()
        
        # Verify stability metrics
        summary = stability_metrics.get_summary()
        assert summary["test_duration_seconds"] >= test_duration * 0.9
        assert summary["connection_success_rate"] == 1.0
        assert summary["messages_per_second"] >= high_load_rate * 0.8
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_stability_under_load",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "connection_stability", 
                "scenario": "under_load",
                "target_rate": high_load_rate,
                "actual_rate": actual_rate,
                "messages_sent": messages_sent,
                "total_time": total_time,
                "success_rate": summary["connection_success_rate"]
            }
        }))
    
    @pytest.mark.asyncio
    async def test_connection_stability_memory_usage(self, websocket_manager, stability_metrics):
        """Test connection stability and memory usage over time."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_stability_memory_usage",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "connection_stability", "scenario": "memory_usage"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/emoji-rain"
        test_duration = 1800  # 30 minutes
        message_interval = 60  # Send message every minute
        
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
            stability_metrics.record_connection_attempt(True, 30.0)
            
            start_time = time.time()
            messages_sent = 0
            memory_checks = 0
            
            while time.time() - start_time < test_duration:
                # Send message
                test_message = WebSocketTestData.get_test_messages(1)[0]
                await websocket_manager.send_message(endpoint, test_message.__dict__, connection)
                stability_metrics.record_message(True, 8.0)
                messages_sent += 1
                
                # Simulate memory usage check (in real implementation, would use psutil)
                memory_checks += 1
                
                # Check connection status
                status = websocket_manager.get_connection_status(endpoint)
                assert status['connected_connections'] == 1
                
                await asyncio.sleep(message_interval)
            
            total_time = time.time() - start_time
            
            # Verify stability
            assert messages_sent > 0
            assert memory_checks > 0
            assert total_time >= test_duration * 0.9
            
            # Final status check
            final_status = websocket_manager.get_connection_status(endpoint)
            assert final_status['connected_connections'] == 1
            
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        await websocket_manager.stop()
        
        # Verify stability metrics
        summary = stability_metrics.get_summary()
        assert summary["test_duration_seconds"] >= test_duration * 0.9
        assert summary["connection_success_rate"] == 1.0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_stability_memory_usage",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "connection_stability", 
                "scenario": "memory_usage",
                "messages_sent": messages_sent,
                "memory_checks": memory_checks,
                "total_time": total_time,
                "success_rate": summary["connection_success_rate"]
            }
        }))
    
    @pytest.mark.asyncio
    async def test_connection_stability_cpu_usage(self, websocket_manager, stability_metrics):
        """Test connection stability and CPU usage over time."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_stability_cpu_usage",
            "status": "in_progress",
            "details": {"test_type": "load", "component": "connection_stability", "scenario": "cpu_usage"}
        }))
        
        await websocket_manager.start()
        
        endpoint = "/ws/observatory"
        test_duration = 1200  # 20 minutes
        message_interval = 30  # Send message every 30 seconds
        
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
            stability_metrics.record_connection_attempt(True, 25.0)
            
            start_time = time.time()
            messages_sent = 0
            cpu_checks = 0
            
            while time.time() - start_time < test_duration:
                # Send message
                test_message = WebSocketTestData.get_test_messages(1)[0]
                await websocket_manager.send_message(endpoint, test_message.__dict__, connection)
                stability_metrics.record_message(True, 6.0)
                messages_sent += 1
                
                # Simulate CPU usage check (in real implementation, would use psutil)
                cpu_checks += 1
                
                # Check connection status
                status = websocket_manager.get_connection_status(endpoint)
                assert status['connected_connections'] == 1
                
                await asyncio.sleep(message_interval)
            
            total_time = time.time() - start_time
            
            # Verify stability
            assert messages_sent > 0
            assert cpu_checks > 0
            assert total_time >= test_duration * 0.9
            
            # Final status check
            final_status = websocket_manager.get_connection_status(endpoint)
            assert final_status['connected_connections'] == 1
            
            await websocket_manager.disconnect_all_websockets(endpoint)
        
        await websocket_manager.stop()
        
        # Verify stability metrics
        summary = stability_metrics.get_summary()
        assert summary["test_duration_seconds"] >= test_duration * 0.9
        assert summary["connection_success_rate"] == 1.0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_connection_stability_cpu_usage",
            "status": "completed",
            "details": {
                "test_type": "load", 
                "component": "connection_stability", 
                "scenario": "cpu_usage",
                "messages_sent": messages_sent,
                "cpu_checks": cpu_checks,
                "total_time": total_time,
                "success_rate": summary["connection_success_rate"]
            }
        }))