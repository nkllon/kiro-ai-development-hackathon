"""
Integration tests for Status Broadcasting and Persistence

Tests the complete integration of status management, broadcasting, and persistence
with brownfield safety features.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.beast_mode.observatory.ai_consultation.doctor_status_manager import DoctorStatusManager
from src.beast_mode.observatory.ai_consultation.status_broadcaster import StatusBroadcaster, BroadcastChannel
from src.beast_mode.observatory.ai_consultation.status_persistence import StatusPersistence
from src.beast_mode.observatory.ai_consultation.feature_flags import feature_flags, FeatureFlag
from src.beast_mode.observatory.ai_consultation.models import DoctorStatusReason


class TestStatusIntegration:
    """Integration tests for complete status system"""
    
    @pytest.fixture
    async def integrated_status_system(self):
        """Set up complete integrated status system"""
        # Create components
        status_manager = DoctorStatusManager(daily_budget=10.0, monthly_budget=100.0)
        broadcaster = StatusBroadcaster(redis_url=None, channel_prefix="test_integration")
        persistence = StatusPersistence(redis_url=None, key_prefix="test_integration")
        
        # Enable all feature flags
        flags_to_enable = [
            FeatureFlag.DOCTOR_STATUS_MANAGEMENT,
            FeatureFlag.WEBSOCKET_BROADCASTING,
            FeatureFlag.REDIS_PERSISTENCE,
            FeatureFlag.COST_TRACKING,
            FeatureFlag.BUDGET_ENFORCEMENT
        ]
        
        for flag in flags_to_enable:
            await feature_flags.set_flag(flag.value, True)
        
        # Initialize components
        await status_manager.initialize()
        await broadcaster.initialize()
        await persistence.initialize()
        
        yield {
            'status_manager': status_manager,
            'broadcaster': broadcaster,
            'persistence': persistence
        }
        
        # Cleanup
        await status_manager.cleanup()
        await broadcaster.cleanup()
        await persistence.cleanup()
    
    @pytest.mark.asyncio
    async def test_status_change_full_pipeline(self, integrated_status_system):
        """Test complete status change pipeline with broadcasting and persistence"""
        status_manager = integrated_status_system['status_manager']
        broadcaster = integrated_status_system['broadcaster']
        persistence = integrated_status_system['persistence']
        
        # Set up WebSocket connection to receive broadcasts
        received_messages = []
        
        async def mock_websocket_handler(message_data):
            received_messages.append(json.loads(message_data))
        
        # Register WebSocket connection
        await broadcaster.register_connection("test_conn", mock_websocket_handler, user_id="test_user")
        await broadcaster.subscribe_to_channel("test_conn", BroadcastChannel.DOCTOR_STATUS.value)
        
        # Change status manually
        await status_manager.set_status_manual(True, "admin_user")
        
        # Give time for async operations
        await asyncio.sleep(0.1)
        
        # Verify status was persisted
        persisted_status = await persistence.get_doctor_status()
        assert persisted_status is not None
        assert persisted_status.is_available is True
        assert persisted_status.reason == DoctorStatusReason.MANUAL
        
        # Verify status change was broadcasted
        status_messages = [msg for msg in received_messages if msg.get('event_type') == 'status_changed']
        assert len(status_messages) >= 1
        
        status_message = status_messages[0]
        assert status_message['data']['new_status'] is True
        assert status_message['data']['reason'] == 'manual'
        assert status_message['data']['triggered_by'] == 'admin_user'
        
        # Verify event was stored in persistence
        recent_events = await persistence.get_recent_events(limit=5)
        assert len(recent_events) >= 1
        
        latest_event = recent_events[0]
        assert latest_event['new_status'] is True
        assert latest_event['reason'] == 'manual'
        assert latest_event['triggered_by'] == 'admin_user'
    
    @pytest.mark.asyncio
    async def test_budget_tracking_with_broadcasting(self, integrated_status_system):
        """Test budget tracking with real-time broadcasting"""
        status_manager = integrated_status_system['status_manager']
        broadcaster = integrated_status_system['broadcaster']
        persistence = integrated_status_system['persistence']
        
        # Set up WebSocket connection for budget updates
        received_messages = []
        
        async def mock_websocket_handler(message_data):
            received_messages.append(json.loads(message_data))
        
        await broadcaster.register_connection("budget_conn", mock_websocket_handler)
        await broadcaster.subscribe_to_channel("budget_conn", BroadcastChannel.BUDGET_STATUS.value)
        
        # Track some costs
        await status_manager.track_cost("session_1", 1000, 2.0)
        await status_manager.track_cost("session_2", 1500, 3.0)
        
        # Give time for async operations
        await asyncio.sleep(0.1)
        
        # Verify budget was persisted
        persisted_budget = await persistence.get_budget_status()
        assert persisted_budget is not None
        assert persisted_budget.daily_spent == 5.0
        assert persisted_budget.monthly_spent == 5.0
        
        # Verify budget updates were broadcasted
        budget_messages = [msg for msg in received_messages if msg.get('event_type') == 'budget_updated']
        assert len(budget_messages) >= 2  # One for each cost tracking
        
        # Check latest budget message
        latest_budget = budget_messages[-1]
        assert latest_budget['data']['daily_spent'] == 5.0
        assert latest_budget['data']['monthly_spent'] == 5.0
    
    @pytest.mark.asyncio
    async def test_budget_exhaustion_with_status_change(self, integrated_status_system):
        """Test automatic status change when budget is exhausted"""
        status_manager = integrated_status_system['status_manager']
        broadcaster = integrated_status_system['broadcaster']
        
        # Set up WebSocket connections for both status and budget
        received_messages = []
        
        async def mock_websocket_handler(message_data):
            received_messages.append(json.loads(message_data))
        
        await broadcaster.register_connection("full_conn", mock_websocket_handler)
        await broadcaster.subscribe_to_channel("full_conn", BroadcastChannel.DOCTOR_STATUS.value)
        await broadcaster.subscribe_to_channel("full_conn", BroadcastChannel.BUDGET_STATUS.value)
        
        # Set status to available first
        await status_manager.set_status_manual(True, "admin")
        
        # Exhaust budget
        await status_manager.track_cost("expensive_session", 100000, 15.0)
        
        # Give time for async operations
        await asyncio.sleep(0.1)
        
        # Verify status changed to unavailable
        current_status = await status_manager.get_status()
        assert current_status.is_available is False
        assert current_status.reason == DoctorStatusReason.BUDGET_EXHAUSTED
        
        # Verify both status and budget messages were sent
        status_messages = [msg for msg in received_messages if msg.get('event_type') == 'status_changed']
        budget_messages = [msg for msg in received_messages if msg.get('event_type') == 'budget_updated']
        
        assert len(status_messages) >= 2  # Manual enable + budget exhaustion
        assert len(budget_messages) >= 1  # Budget update
        
        # Check final status message
        final_status = [msg for msg in status_messages if msg['data']['reason'] == 'budget_exhausted']
        assert len(final_status) >= 1
        assert final_status[0]['data']['new_status'] is False
    
    @pytest.mark.asyncio
    async def test_multiple_websocket_connections(self, integrated_status_system):
        """Test broadcasting to multiple WebSocket connections"""
        broadcaster = integrated_status_system['broadcaster']
        status_manager = integrated_status_system['status_manager']
        
        # Set up multiple WebSocket connections
        connection_messages = {}
        
        for i in range(3):
            conn_id = f"conn_{i}"
            messages = []
            connection_messages[conn_id] = messages
            
            async def make_handler(msg_list):
                async def handler(message_data):
                    msg_list.append(json.loads(message_data))
                return handler
            
            handler = await make_handler(messages)
            await broadcaster.register_connection(conn_id, handler, user_id=f"user_{i}")
            await broadcaster.subscribe_to_channel(conn_id, BroadcastChannel.DOCTOR_STATUS.value)
        
        # Change status
        await status_manager.set_status_manual(True, "broadcast_test")
        
        # Give time for async operations
        await asyncio.sleep(0.1)
        
        # Verify all connections received the message
        for conn_id, messages in connection_messages.items():
            status_messages = [msg for msg in messages if msg.get('event_type') == 'status_changed']
            assert len(status_messages) >= 1
            
            status_msg = status_messages[0]
            assert status_msg['data']['new_status'] is True
            assert status_msg['data']['triggered_by'] == 'broadcast_test'
    
    @pytest.mark.asyncio
    async def test_persistence_fallback_mode(self, integrated_status_system):
        """Test system behavior when persistence is in fallback mode"""
        status_manager = integrated_status_system['status_manager']
        persistence = integrated_status_system['persistence']
        
        # Force persistence into fallback mode
        persistence._fallback_mode = True
        
        # Change status
        await status_manager.set_status_manual(True, "fallback_test")
        
        # Give time for async operations
        await asyncio.sleep(0.1)
        
        # Verify status was still persisted (in fallback storage)
        persisted_status = await persistence.get_doctor_status()
        assert persisted_status is not None
        assert persisted_status.is_available is True
        assert persisted_status.reason == DoctorStatusReason.MANUAL
        
        # Verify events were stored in fallback
        recent_events = await persistence.get_recent_events()
        assert len(recent_events) >= 1
    
    @pytest.mark.asyncio
    async def test_broadcaster_fallback_mode(self, integrated_status_system):
        """Test system behavior when broadcaster is in fallback mode"""
        status_manager = integrated_status_system['status_manager']
        broadcaster = integrated_status_system['broadcaster']
        
        # Force broadcaster into fallback mode
        broadcaster._fallback_mode = True
        
        # Change status (should not raise error)
        await status_manager.set_status_manual(True, "fallback_broadcast_test")
        
        # System should continue to function
        current_status = await status_manager.get_status()
        assert current_status.is_available is True
        assert current_status.reason == DoctorStatusReason.MANUAL
    
    @pytest.mark.asyncio
    async def test_feature_flag_integration(self, integrated_status_system):
        """Test feature flag integration across all components"""
        status_manager = integrated_status_system['status_manager']
        broadcaster = integrated_status_system['broadcaster']
        
        # Disable WebSocket broadcasting
        await feature_flags.set_flag(FeatureFlag.WEBSOCKET_BROADCASTING.value, False)
        
        # Try to register connection (should fail)
        mock_handler = AsyncMock()
        success = await broadcaster.register_connection("test_disabled", mock_handler)
        assert success is False
        
        # Disable status management
        await feature_flags.set_flag(FeatureFlag.DOCTOR_STATUS_MANAGEMENT.value, False)
        
        # Status should become unavailable
        current_status = await status_manager.get_status()
        assert current_status.is_available is False
        assert current_status.reason == DoctorStatusReason.FEATURE_DISABLED
    
    @pytest.mark.asyncio
    async def test_session_data_persistence(self, integrated_status_system):
        """Test session data persistence functionality"""
        persistence = integrated_status_system['persistence']
        
        # Store session data
        session_data = {
            "user_id": "test_user",
            "start_time": datetime.utcnow().isoformat(),
            "cost": 5.5,
            "tokens": 5500,
            "queries": 3
        }
        
        success = await persistence.store_session_data("session_123", session_data)
        assert success is True
        
        # Retrieve session data
        retrieved = await persistence.get_session_data("session_123")
        assert retrieved is not None
        assert retrieved["user_id"] == "test_user"
        assert retrieved["cost"] == 5.5
        assert retrieved["tokens"] == 5500
        
        # Delete session data
        success = await persistence.delete_session_data("session_123")
        assert success is True
        
        # Should be gone
        retrieved = await persistence.get_session_data("session_123")
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_system_health_monitoring(self, integrated_status_system):
        """Test system health monitoring integration"""
        status_manager = integrated_status_system['status_manager']
        broadcaster = integrated_status_system['broadcaster']
        persistence = integrated_status_system['persistence']
        
        # Check health of all components
        status_health = await status_manager.health_check()
        broadcaster_health = await broadcaster.health_check()
        persistence_health = await persistence.health_check()
        
        # All should be healthy or degraded (not unhealthy)
        assert status_health.status in ["healthy", "degraded"]
        assert broadcaster_health.status in ["healthy", "degraded"]
        assert persistence_health.status in ["healthy", "degraded"]
        
        # Test system health integration
        await status_manager.set_system_health(False, "Test error")
        
        current_status = await status_manager.get_status()
        assert current_status.is_available is False
        assert current_status.reason == DoctorStatusReason.SYSTEM_ERROR
        
        # Restore health
        await status_manager.set_system_health(True)
        
        current_status = await status_manager.get_status()
        assert current_status.is_available is True
        assert current_status.reason == DoctorStatusReason.AUTOMATIC


if __name__ == "__main__":
    pytest.main([__file__])