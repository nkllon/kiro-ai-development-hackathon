"""
Unit tests for Connection Tracker

Tests real-time connection status tracking functionality including
connection monitoring, metrics collection, and activity tracking.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from src.beast_mode.observatory.monitoring.connection_tracker import (
    ConnectionTracker, ConnectionInfo
)


class TestConnectionTracker:
    """Test cases for ConnectionTracker"""

    @pytest.fixture
    def tracker(self):
        """Create a connection tracker instance for testing"""
        return ConnectionTracker()

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket for testing"""
        websocket = Mock()
        websocket.close = AsyncMock()
        websocket.send = AsyncMock()
        websocket.recv = AsyncMock()
        return websocket

    def test_initialization(self, tracker):
        """Test connection tracker initialization"""
        assert len(tracker._connections) == 0
        assert len(tracker._connection_metrics) == 0
        assert len(tracker._tracking_tasks) == 0
        assert tracker._total_connections == 0
        assert tracker._total_disconnections == 0

    @pytest.mark.asyncio
    async def test_track_connection_success(self, tracker, mock_websocket):
        """Test successful connection tracking"""
        endpoint = "test_endpoint"
        metadata = {"user_id": "123", "session_id": "abc"}
        
        await tracker.track_connection(endpoint, mock_websocket, metadata)
        
        # Verify connection was tracked
        assert endpoint in tracker._connections
        assert endpoint in tracker._connection_metrics
        assert endpoint in tracker._tracking_tasks
        assert tracker._total_connections == 1
        
        # Verify connection info
        conn_info = tracker._connections[endpoint]
        assert conn_info.endpoint == endpoint
        assert conn_info.websocket == mock_websocket
        assert conn_info.metadata == metadata
        assert conn_info.is_active is True
        assert conn_info.message_count == 0
        assert conn_info.error_count == 0

    @pytest.mark.asyncio
    async def test_track_connection_without_metadata(self, tracker, mock_websocket):
        """Test connection tracking without metadata"""
        endpoint = "test_endpoint"
        
        await tracker.track_connection(endpoint, mock_websocket)
        
        conn_info = tracker._connections[endpoint]
        assert conn_info.metadata == {}

    @pytest.mark.asyncio
    async def test_stop_tracking(self, tracker, mock_websocket):
        """Test stopping connection tracking"""
        endpoint = "test_endpoint"
        
        # Track connection first
        await tracker.track_connection(endpoint, mock_websocket)
        
        # Stop tracking
        await tracker.stop_tracking(endpoint)
        
        # Verify tracking was stopped
        assert endpoint not in tracker._connections
        assert endpoint not in tracker._connection_metrics
        assert endpoint not in tracker._tracking_tasks
        assert tracker._total_disconnections == 1

    @pytest.mark.asyncio
    async def test_stop_tracking_nonexistent(self, tracker):
        """Test stopping tracking for non-existent connection"""
        endpoint = "nonexistent_endpoint"
        
        # Should not raise exception
        await tracker.stop_tracking(endpoint)
        
        assert tracker._total_disconnections == 0

    @pytest.mark.asyncio
    async def test_record_message_sent(self, tracker, mock_websocket):
        """Test recording message sent events"""
        endpoint = "test_endpoint"
        message_size = 1024
        
        await tracker.track_connection(endpoint, mock_websocket)
        await tracker.record_message_sent(endpoint, message_size)
        
        conn_info = tracker._connections[endpoint]
        assert conn_info.message_count == 1
        assert conn_info.bytes_sent == message_size
        assert conn_info.last_activity > datetime.now() - timedelta(seconds=1)

    @pytest.mark.asyncio
    async def test_record_message_received(self, tracker, mock_websocket):
        """Test recording message received events"""
        endpoint = "test_endpoint"
        message_size = 512
        
        await tracker.track_connection(endpoint, mock_websocket)
        await tracker.record_message_received(endpoint, message_size)
        
        conn_info = tracker._connections[endpoint]
        assert conn_info.message_count == 1
        assert conn_info.bytes_received == message_size
        assert conn_info.last_activity > datetime.now() - timedelta(seconds=1)

    @pytest.mark.asyncio
    async def test_record_error(self, tracker, mock_websocket):
        """Test recording error events"""
        endpoint = "test_endpoint"
        error_type = "connection_timeout"
        
        await tracker.track_connection(endpoint, mock_websocket)
        await tracker.record_error(endpoint, error_type)
        
        conn_info = tracker._connections[endpoint]
        assert conn_info.error_count == 1

    @pytest.mark.asyncio
    async def test_record_events_nonexistent_connection(self, tracker):
        """Test recording events for non-existent connection"""
        endpoint = "nonexistent_endpoint"
        
        # Should not raise exceptions
        await tracker.record_message_sent(endpoint, 100)
        await tracker.record_message_received(endpoint, 200)
        await tracker.record_error(endpoint, "test_error")

    def test_get_connection_info(self, tracker):
        """Test getting connection information"""
        endpoint = "test_endpoint"
        
        # Test non-existent connection
        assert tracker.get_connection_info(endpoint) is None

    def test_get_all_connections(self, tracker):
        """Test getting all connections"""
        # Initially empty
        connections = tracker.get_all_connections()
        assert len(connections) == 0
        
        # Add test connection info
        conn_info = ConnectionInfo(
            endpoint="test_endpoint",
            websocket=Mock(),
            connected_at=datetime.now(),
            last_activity=datetime.now()
        )
        tracker._connections["test_endpoint"] = conn_info
        
        connections = tracker.get_all_connections()
        assert len(connections) == 1
        assert "test_endpoint" in connections

    @pytest.mark.asyncio
    async def test_get_connection_metrics(self, tracker, mock_websocket):
        """Test getting connection metrics"""
        endpoint = "test_endpoint"
        
        # Track connection and add some activity
        await tracker.track_connection(endpoint, mock_websocket)
        await tracker.record_message_sent(endpoint, 100)
        await tracker.record_message_received(endpoint, 200)
        await tracker.record_error(endpoint, "test_error")
        
        # Wait a bit for duration calculation
        await asyncio.sleep(0.1)
        
        metrics = await tracker.get_connection_metrics(endpoint)
        
        # Verify metrics
        assert metrics['message_count'] == 2
        assert metrics['error_count'] == 1
        assert metrics['bytes_sent'] == 100
        assert metrics['bytes_received'] == 200
        assert metrics['connection_duration_sec'] > 0
        assert metrics['error_rate'] == 0.5  # 1 error / 2 messages
        assert metrics['is_active'] is True
        assert 'connected_at' in metrics
        assert 'last_activity' in metrics

    @pytest.mark.asyncio
    async def test_get_connection_metrics_nonexistent(self, tracker):
        """Test getting metrics for non-existent connection"""
        endpoint = "nonexistent_endpoint"
        
        metrics = await tracker.get_connection_metrics(endpoint)
        assert metrics == {}

    def test_get_overall_stats(self, tracker):
        """Test getting overall statistics"""
        stats = tracker.get_overall_stats()
        
        # Verify initial stats
        assert stats['active_connections'] == 0
        assert stats['total_connections'] == 0
        assert stats['total_disconnections'] == 0
        assert stats['total_messages'] == 0
        assert stats['total_errors'] == 0
        assert stats['total_bytes'] == 0
        assert stats['uptime_sec'] > 0
        assert stats['avg_messages_per_connection'] == 0
        assert stats['avg_bytes_per_connection'] == 0
        assert stats['overall_error_rate'] == 0

    def test_is_connection_active(self, tracker):
        """Test connection activity checking"""
        endpoint = "test_endpoint"
        
        # Test non-existent connection
        assert tracker.is_connection_active(endpoint) is False
        
        # Test active connection
        conn_info = ConnectionInfo(
            endpoint=endpoint,
            websocket=Mock(),
            connected_at=datetime.now(),
            last_activity=datetime.now()
        )
        tracker._connections[endpoint] = conn_info
        
        assert tracker.is_connection_active(endpoint) is True
        
        # Test inactive connection (old last activity)
        conn_info.last_activity = datetime.now() - timedelta(minutes=10)
        assert tracker.is_connection_active(endpoint) is False

    @pytest.mark.asyncio
    async def test_track_connection_background_task_cancellation(self, tracker, mock_websocket):
        """Test that background tracking task can be cancelled"""
        endpoint = "test_endpoint"
        
        await tracker.track_connection(endpoint, mock_websocket)
        
        # Verify task exists
        assert endpoint in tracker._tracking_tasks
        
        # Stop tracking (should cancel task)
        await tracker.stop_tracking(endpoint)
        
        # Verify task was cancelled
        assert endpoint not in tracker._tracking_tasks

    @pytest.mark.asyncio
    async def test_track_connection_background_error_handling(self, tracker, mock_websocket):
        """Test background tracking error handling"""
        endpoint = "test_endpoint"
        
        await tracker.track_connection(endpoint, mock_websocket)
        
        # Simulate error in background task
        with patch.object(tracker, '_connections', side_effect=Exception("Test error")):
            # Let the background task run briefly
            await asyncio.sleep(0.1)
        
        # Task should still be running (error handling should prevent crash)
        assert endpoint in tracker._tracking_tasks

    def test_log_action(self, tracker, capsys):
        """Test JSON logging functionality"""
        tracker._log_action("test_action", {"key": "value"})
        
        captured = capsys.readouterr()
        log_output = captured.out.strip()
        
        # Should be valid JSON
        import json
        log_data = json.loads(log_output)
        
        assert log_data["task"] == "3.1"
        assert log_data["action"] == "connection_tracker_test_action"
        assert log_data["status"] == "in_progress"
        assert log_data["details"]["key"] == "value"
        assert "timestamp" in log_data


class TestConnectionInfo:
    """Test cases for ConnectionInfo dataclass"""
    
    def test_connection_info_creation(self):
        """Test ConnectionInfo creation"""
        websocket = Mock()
        connected_at = datetime.now()
        last_activity = datetime.now()
        
        conn_info = ConnectionInfo(
            endpoint="test_endpoint",
            websocket=websocket,
            connected_at=connected_at,
            last_activity=last_activity,
            message_count=5,
            error_count=1,
            bytes_sent=1024,
            bytes_received=2048,
            is_active=True,
            metadata={"user_id": "123"}
        )
        
        assert conn_info.endpoint == "test_endpoint"
        assert conn_info.websocket == websocket
        assert conn_info.connected_at == connected_at
        assert conn_info.last_activity == last_activity
        assert conn_info.message_count == 5
        assert conn_info.error_count == 1
        assert conn_info.bytes_sent == 1024
        assert conn_info.bytes_received == 2048
        assert conn_info.is_active is True
        assert conn_info.metadata == {"user_id": "123"}

    def test_connection_info_defaults(self):
        """Test ConnectionInfo default values"""
        websocket = Mock()
        connected_at = datetime.now()
        last_activity = datetime.now()
        
        conn_info = ConnectionInfo(
            endpoint="test_endpoint",
            websocket=websocket,
            connected_at=connected_at,
            last_activity=last_activity
        )
        
        assert conn_info.message_count == 0
        assert conn_info.error_count == 0
        assert conn_info.bytes_sent == 0
        assert conn_info.bytes_received == 0
        assert conn_info.is_active is True
        assert conn_info.metadata == {}