"""
Unit tests for Status Broadcaster

Tests WebSocket broadcasting, connection management, and brownfield safety.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import asdict

from src.beast_mode.observatory.ai_consultation.status_broadcaster import (
    StatusBroadcaster,
    BroadcastChannel,
    WebSocketMessage,
    ClientConnection,
    status_broadcaster,
    initialize_broadcaster,
    cleanup_broadcaster
)
from src.beast_mode.observatory.ai_consultation.doctor_status_manager import (
    StatusChangeEvent, StatusTransition
)
from src.beast_mode.observatory.ai_consultation.models import (
    DoctorStatus, DoctorStatusReason, BudgetStatus
)
from src.beast_mode.observatory.ai_consultation.feature_flags import feature_flags, FeatureFlag
from src.beast_mode.observatory.ai_consultation.health_checker import ComponentHealth


class TestStatusBroadcaster:
    """Test StatusBroadcaster class"""
    
    @pytest.fixture
    async def broadcaster(self):
        """Create test broadcaster instance"""
        broadcaster = StatusBroadcaster(
            redis_url=None,  # No Redis for unit tests
            channel_prefix="test_ai_consultation",
            max_connections=10,
            message_ttl=60,
            ping_interval=5
        )
        
        # Enable feature flags
        await feature_flags.set_flag(FeatureFlag.WEBSOCKET_BROADCASTING.value, True)
        
        yield broadcaster
        
        # Cleanup
        await broadcaster.cleanup()
    
    @pytest.mark.asyncio
    async def test_initialization(self, broadcaster):
        """Test broadcaster initialization"""
        await broadcaster.initialize()
        
        # Should detect Observatory WebSocket (mocked)
        assert broadcaster._observatory_websocket_detected is True
        assert broadcaster.channel_prefix.startswith("ai_consultation_")
    
    @pytest.mark.asyncio
    async def test_connection_registration(self, broadcaster):
        """Test WebSocket connection registration"""
        await broadcaster.initialize()
        
        # Mock WebSocket handler
        mock_handler = AsyncMock()
        mock_handler.send_text = AsyncMock()
        
        # Register connection
        success = await broadcaster.register_connection(
            "conn_1",
            mock_handler,
            user_id="user_123",
            metadata={"ip": "127.0.0.1"}
        )
        
        assert success is True
        assert "conn_1" in broadcaster._connections
        assert broadcaster._connections["conn_1"].user_id == "user_123"
        assert broadcaster._stats['connections_active'] == 1
        
        # Should send welcome message
        mock_handler.send_text.assert_called_once()
        welcome_call = mock_handler.send_text.call_args[0][0]
        welcome_data = json.loads(welcome_call)
        assert welcome_data['event_type'] == 'connection_established'
    
    @pytest.mark.asyncio
    async def test_connection_limits(self, broadcaster):
        """Test connection limit enforcement"""
        broadcaster.max_connections = 2
        await broadcaster.initialize()
        
        mock_handler = AsyncMock()
        mock_handler.send_text = AsyncMock()
        
        # Register up to limit
        success1 = await broadcaster.register_connection("conn_1", mock_handler)
        success2 = await broadcaster.register_connection("conn_2", mock_handler)
        success3 = await broadcaster.register_connection("conn_3", mock_handler)
        
        assert success1 is True
        assert success2 is True
        assert success3 is False  # Should be rejected
        assert len(broadcaster._connections) == 2
    
    @pytest.mark.asyncio
    async def test_channel_subscription(self, broadcaster):
        """Test channel subscription management"""
        await broadcaster.initialize()
        
        mock_handler = AsyncMock()
        mock_handler.send_text = AsyncMock()
        
        # Register connection
        await broadcaster.register_connection("conn_1", mock_handler)
        
        # Subscribe to channel
        success = await broadcaster.subscribe_to_channel("conn_1", BroadcastChannel.DOCTOR_STATUS.value)
        assert success is True
        
        connection = broadcaster._connections["conn_1"]
        assert BroadcastChannel.DOCTOR_STATUS.value in connection.subscribed_channels
        
        # Should send subscription confirmation
        assert mock_handler.send_text.call_count >= 2  # Welcome + subscription confirmation
    
    @pytest.mark.asyncio
    async def test_status_change_broadcast(self, broadcaster):
        """Test broadcasting status changes"""
        await broadcaster.initialize()
        
        # Set up multiple connections
        handlers = []
        for i in range(3):
            handler = AsyncMock()
            handler.send_text = AsyncMock()
            handlers.append(handler)
            
            await broadcaster.register_connection(f"conn_{i}", handler)
            await broadcaster.subscribe_to_channel(f"conn_{i}", BroadcastChannel.DOCTOR_STATUS.value)
        
        # Create status change event
        event = StatusChangeEvent(
            timestamp=datetime.utcnow(),
            old_status=False,
            new_status=True,
            reason=DoctorStatusReason.MANUAL,
            transition_type=StatusTransition.MANUAL_ENABLE,
            triggered_by="admin",
            cost_data={"daily_usage": 5.0},
            metadata={"test": True}
        )
        
        # Broadcast event
        await broadcaster.broadcast_status_change(event)
        
        # All subscribed connections should receive the message
        for handler in handlers:
            # Should have welcome message + status change message
            assert handler.send_text.call_count >= 2
            
            # Check the status change message
            calls = handler.send_text.call_args_list
            status_message = None
            for call in calls:
                data = json.loads(call[0][0])
                if data['event_type'] == 'status_changed':
                    status_message = data
                    break
            
            assert status_message is not None
            assert status_message['channel'] == BroadcastChannel.DOCTOR_STATUS.value
            assert status_message['data']['old_status'] is False
            assert status_message['data']['new_status'] is True
            assert status_message['data']['reason'] == 'manual'
    
    @pytest.mark.asyncio
    async def test_budget_update_broadcast(self, broadcaster):
        """Test broadcasting budget updates"""
        await broadcaster.initialize()
        
        mock_handler = AsyncMock()
        mock_handler.send_text = AsyncMock()
        
        await broadcaster.register_connection("conn_1", mock_handler)
        await broadcaster.subscribe_to_channel("conn_1", BroadcastChannel.BUDGET_STATUS.value)
        
        # Create budget status
        budget = BudgetStatus(
            daily_budget=10.0,
            monthly_budget=100.0,
            daily_spent=5.0,
            monthly_spent=25.0,
            daily_remaining=5.0,
            monthly_remaining=75.0,
            daily_percentage=0.5,
            monthly_percentage=0.25,
            daily_exhausted=False,
            monthly_exhausted=False,
            daily_warning=False,
            monthly_warning=False,
            daily_critical=False,
            monthly_critical=False,
            cost_per_token=0.0001,
            last_updated=datetime.utcnow()
        )
        
        # Broadcast budget update
        await broadcaster.broadcast_budget_update(budget)
        
        # Check message was sent
        calls = mock_handler.send_text.call_args_list
        budget_message = None
        for call in calls:
            data = json.loads(call[0][0])
            if data['event_type'] == 'budget_updated':
                budget_message = data
                break
        
        assert budget_message is not None
        assert budget_message['channel'] == BroadcastChannel.BUDGET_STATUS.value
        assert budget_message['data']['daily_spent'] == 5.0
        assert budget_message['data']['monthly_spent'] == 25.0
    
    @pytest.mark.asyncio
    async def test_connection_cleanup(self, broadcaster):
        """Test connection cleanup for stale connections"""
        await broadcaster.initialize()
        
        mock_handler = AsyncMock()
        mock_handler.send_text = AsyncMock()
        
        # Register connection
        await broadcaster.register_connection("conn_1", mock_handler)
        
        # Simulate stale connection (old last_ping)
        connection = broadcaster._connections["conn_1"]
        connection.last_ping = datetime.utcnow() - timedelta(minutes=10)
        
        # Run cleanup
        await broadcaster._cleanup_connections()
        
        # Connection should be removed
        assert "conn_1" not in broadcaster._connections
        assert broadcaster._stats['connections_active'] == 0
    
    @pytest.mark.asyncio
    async def test_feature_flag_disabled(self, broadcaster):
        """Test behavior when WebSocket broadcasting is disabled"""
        # Disable feature flag
        await feature_flags.set_flag(FeatureFlag.WEBSOCKET_BROADCASTING.value, False)
        
        await broadcaster.initialize()
        
        mock_handler = AsyncMock()
        
        # Should not allow connection registration
        success = await broadcaster.register_connection("conn_1", mock_handler)
        assert success is False
    
    @pytest.mark.asyncio
    async def test_fallback_mode(self, broadcaster):
        """Test fallback mode behavior"""
        # Force fallback mode
        broadcaster._fallback_mode = True
        
        await broadcaster.initialize()
        
        # Create status change event
        event = StatusChangeEvent(
            timestamp=datetime.utcnow(),
            old_status=False,
            new_status=True,
            reason=DoctorStatusReason.MANUAL,
            transition_type=StatusTransition.MANUAL_ENABLE,
            triggered_by="admin"
        )
        
        # Should not raise error in fallback mode
        await broadcaster.broadcast_status_change(event)
    
    @pytest.mark.asyncio
    async def test_message_queuing_on_failure(self, broadcaster):
        """Test message queuing when sending fails"""
        await broadcaster.initialize()
        
        # Mock handler that fails
        mock_handler = AsyncMock()
        mock_handler.send_text = AsyncMock(side_effect=Exception("Connection lost"))
        
        await broadcaster.register_connection("conn_1", mock_handler)
        await broadcaster.subscribe_to_channel("conn_1", BroadcastChannel.DOCTOR_STATUS.value)
        
        # Create status change event
        event = StatusChangeEvent(
            timestamp=datetime.utcnow(),
            old_status=False,
            new_status=True,
            reason=DoctorStatusReason.MANUAL,
            transition_type=StatusTransition.MANUAL_ENABLE,
            triggered_by="admin"
        )
        
        # Broadcast should not raise error
        await broadcaster.broadcast_status_change(event)
        
        # Message should be queued
        assert len(broadcaster._message_queue["conn_1"]) > 0
    
    @pytest.mark.asyncio
    async def test_connection_stats(self, broadcaster):
        """Test connection statistics"""
        await broadcaster.initialize()
        
        mock_handler = AsyncMock()
        mock_handler.send_text = AsyncMock()
        
        # Register connections and subscribe to different channels
        await broadcaster.register_connection("conn_1", mock_handler)
        await broadcaster.subscribe_to_channel("conn_1", BroadcastChannel.DOCTOR_STATUS.value)
        
        await broadcaster.register_connection("conn_2", mock_handler)
        await broadcaster.subscribe_to_channel("conn_2", BroadcastChannel.BUDGET_STATUS.value)
        
        # Get stats
        stats = await broadcaster.get_connection_stats()
        
        assert stats['connections_active'] == 2
        assert stats['connections_by_channel'][BroadcastChannel.DOCTOR_STATUS.value] == 1
        assert stats['connections_by_channel'][BroadcastChannel.BUDGET_STATUS.value] == 1
        assert stats['fallback_mode'] is False
    
    @pytest.mark.asyncio
    async def test_health_check(self, broadcaster):
        """Test health check functionality"""
        await broadcaster.initialize()
        
        health = await broadcaster.health_check()
        
        assert isinstance(health, ComponentHealth)
        assert health.component == "status_broadcaster"
        assert health.status in ["healthy", "degraded", "unhealthy"]
        assert "active_connections" in health.metadata
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, broadcaster):
        """Test concurrent broadcasting operations"""
        await broadcaster.initialize()
        
        # Set up multiple connections
        handlers = []
        for i in range(5):
            handler = AsyncMock()
            handler.send_text = AsyncMock()
            handlers.append(handler)
            
            await broadcaster.register_connection(f"conn_{i}", handler)
            await broadcaster.subscribe_to_channel(f"conn_{i}", BroadcastChannel.DOCTOR_STATUS.value)
        
        # Create multiple events
        events = []
        for i in range(10):
            event = StatusChangeEvent(
                timestamp=datetime.utcnow(),
                old_status=i % 2 == 0,
                new_status=i % 2 == 1,
                reason=DoctorStatusReason.MANUAL,
                transition_type=StatusTransition.MANUAL_ENABLE,
                triggered_by=f"user_{i}"
            )
            events.append(event)
        
        # Broadcast all events concurrently
        tasks = [broadcaster.broadcast_status_change(event) for event in events]
        await asyncio.gather(*tasks)
        
        # All handlers should have received all messages
        for handler in handlers:
            # Should have welcome message + 10 status change messages
            assert handler.send_text.call_count >= 11


class TestGlobalBroadcaster:
    """Test global broadcaster functions"""
    
    @pytest.mark.asyncio
    async def test_global_functions(self):
        """Test global broadcaster functions"""
        with patch('src.beast_mode.observatory.ai_consultation.status_broadcaster.status_broadcaster') as mock_broadcaster:
            mock_broadcaster.initialize = AsyncMock()
            mock_broadcaster.cleanup = AsyncMock()
            
            # Test initialize_broadcaster
            await initialize_broadcaster()
            mock_broadcaster.initialize.assert_called_once()
            
            # Test cleanup_broadcaster
            await cleanup_broadcaster()
            mock_broadcaster.cleanup.assert_called_once()


class TestWebSocketMessage:
    """Test WebSocketMessage class"""
    
    def test_message_serialization(self):
        """Test message serialization to dict"""
        message = WebSocketMessage(
            channel="test_channel",
            event_type="test_event",
            data={"key": "value"},
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            message_id="test_id"
        )
        
        result = message.to_dict()
        
        assert result['channel'] == "test_channel"
        assert result['event_type'] == "test_event"
        assert result['data'] == {"key": "value"}
        assert result['timestamp'] == "2024-01-01T12:00:00"
        assert result['message_id'] == "test_id"


if __name__ == "__main__":
    pytest.main([__file__])