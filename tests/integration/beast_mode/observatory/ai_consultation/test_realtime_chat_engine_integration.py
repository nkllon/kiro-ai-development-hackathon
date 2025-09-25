"""
Integration tests for RealTimeChatEngine
Tests chat engine integration with routing, processing, and Observatory systems.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from src.beast_mode.observatory.ai_consultation.realtime_chat_engine import (
    RealTimeChatEngine, ChatSessionState, MessageType, ContextInjectionMode, get_chat_engine
)
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationQuery, QueryPriority, ObservatoryContext
)
from src.beast_mode.observatory.ai_consultation.security_manager import (
    SecurityContext, PermissionLevel
)
from src.beast_mode.observatory.ai_consultation.consultation_router import RoutingDecision
from src.beast_mode.observatory.ai_consultation.feature_flags import FeatureFlag


class MockWebSocket:
    """Enhanced mock WebSocket for integration testing"""
    def __init__(self, websocket_id: str = "integration_ws"):
        self.websocket_id = websocket_id
        self.sent_messages = []
        self.closed = False
        self.connection_active = True
    
    async def send(self, message: str):
        """Mock send method"""
        if self.connection_active and not self.closed:
            self.sent_messages.append(message)
        else:
            raise ConnectionError("WebSocket connection closed")
    
    def close(self):
        """Mock close method"""
        self.closed = True
        self.connection_active = False
    
    def get_messages_by_type(self, message_type: str) -> list:
        """Get messages of specific type"""
        import json
        messages = []
        for msg in self.sent_messages:
            try:
                parsed = json.loads(msg) if isinstance(msg, str) else msg
                if parsed.get('type') == message_type:
                    messages.append(parsed)
            except:
                pass
        return messages


class TestRealTimeChatEngineIntegration:
    """Integration tests for RealTimeChatEngine"""
    
    @pytest.fixture
    async def chat_engine(self):
        """Create chat engine with realistic configuration"""
        engine = RealTimeChatEngine(
            session_timeout_minutes=15,
            max_concurrent_sessions=5,
            max_messages_per_session=25,
            cleanup_interval_minutes=2,
            heartbeat_interval_seconds=10,
            max_message_length=5000
        )
        await engine.initialize()
        return engine
    
    @pytest.fixture
    def security_context(self):
        """Create security context for testing"""
        return SecurityContext(
            user_id="integration-test-user",
            session_id="integration-test-session",
            permission_level=PermissionLevel.USER,
            authenticated=True,
            session_start=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
    
    @pytest.fixture
    def observatory_context(self):
        """Create Observatory context for testing"""
        context = ObservatoryContext(
            system_status="healthy",
            active_alerts=2,
            metrics_summary={
                "count": 180,
                "healthy": 165,
                "warning": 12,
                "critical": 3,
                "cpu_avg": 68.5,
                "memory_avg": 72.1,
                "response_time_avg": 0.52
            },
            recent_events=[
                {
                    "timestamp": "2024-01-01T11:00:00Z",
                    "type": "alert",
                    "severity": "warning",
                    "message": "High CPU usage on web-server-02"
                },
                {
                    "timestamp": "2024-01-01T10:55:00Z",
                    "type": "info",
                    "message": "Scheduled maintenance completed"
                }
            ],
            data_sensitivity="medium"
        )
        context.get_token_estimate = MagicMock(return_value=280)
        return context
    
    def create_mock_websocket(self, ws_id: str = None) -> MockWebSocket:
        """Create mock WebSocket for testing"""
        return MockWebSocket(ws_id or f"ws_{datetime.utcnow().timestamp()}")
    
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status')
    async def test_full_session_lifecycle_integration(
        self, 
        mock_get_status, 
        mock_permission, 
        mock_flags,
        chat_engine, 
        security_context
    ):
        """Test complete session lifecycle with all integrations"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_get_status.return_value = mock_status
        
        websocket = self.create_mock_websocket("lifecycle_test")
        
        # Create session
        session = await chat_engine.create_session(
            "integration-user", security_context, websocket, ContextInjectionMode.FULL
        )
        
        assert session.state == ChatSessionState.ACTIVE
        assert session.session_id in chat_engine.active_sessions
        assert "integration-user" in chat_engine.user_sessions
        
        # Verify session start message was sent
        start_messages = websocket.get_messages_by_type(MessageType.CHAT_SESSION_START.value)
        assert len(start_messages) > 0
        
        # Close session
        success = await chat_engine.close_session(session.session_id, "test_complete")
        assert success
        
        # Verify session end message was sent
        end_messages = websocket.get_messages_by_type(MessageType.CHAT_SESSION_END.value)
        assert len(end_messages) > 0
        
        # Verify cleanup
        assert session.session_id not in chat_engine.active_sessions
        assert "integration-user" not in chat_engine.user_sessions
    
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_consultation_router')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_request_processor')
    async def test_message_processing_integration(
        self, 
        mock_get_processor, 
        mock_get_router,
        mock_get_status, 
        mock_permission, 
        mock_flags,
        chat_engine, 
        security_context,
        observatory_context
    ):
        """Test message processing with full integration stack"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_get_status.return_value = mock_status
        
        # Mock router
        mock_router = AsyncMock()
        mock_routing_result = MagicMock()
        mock_routing_result.decision = RoutingDecision.REAL_TIME
        mock_routing_result.reason.value = "doctor_available"
        mock_routing_result.cost_estimate = 0.25
        mock_router.route_consultation.return_value = mock_routing_result
        mock_get_router.return_value = mock_router
        
        # Mock processor
        mock_processor = AsyncMock()
        mock_processed_request = MagicMock()
        mock_processed_request.processed_query_text = "What alerts are currently active?"
        mock_processed_request.original_query.query_text = "What alerts are currently active?"
        mock_processed_request.injected_context = observatory_context
        mock_processed_request.system_prompt = "You are an AI assistant for Observatory monitoring."
        mock_processor.process_request.return_value = mock_processed_request
        mock_get_processor.return_value = mock_processor
        
        websocket = self.create_mock_websocket("message_test")
        
        # Create session
        session = await chat_engine.create_session(
            "message-user", security_context, websocket, ContextInjectionMode.FULL
        )
        
        # Send chat message
        chat_message = {
            'type': MessageType.CHAT_MESSAGE.value,
            'session_id': session.session_id,
            'content': 'What alerts are currently active?'
        }
        
        await chat_engine.handle_websocket_message(websocket, chat_message)
        
        # Verify routing was called
        mock_router.route_consultation.assert_called_once()
        
        # Verify processing was called
        mock_processor.process_request.assert_called_once()
        
        # Verify response was sent
        response_messages = websocket.get_messages_by_type(MessageType.CHAT_RESPONSE.value)
        assert len(response_messages) > 0
        
        # Verify cost update was sent
        cost_messages = websocket.get_messages_by_type(MessageType.CHAT_COST_UPDATE.value)
        assert len(cost_messages) > 0
        
        # Verify session was updated
        assert session.total_cost == 0.25
        assert session.message_count >= 1
        assert session.state == ChatSessionState.ACTIVE
    
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_consultation_router')
    async def test_routing_failure_integration(
        self, 
        mock_get_router,
        mock_get_status, 
        mock_permission, 
        mock_flags,
        chat_engine, 
        security_context
    ):
        """Test handling when routing fails or rejects request"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_get_status.return_value = mock_status
        
        # Mock router to reject request
        mock_router = AsyncMock()
        mock_routing_result = MagicMock()
        mock_routing_result.decision = RoutingDecision.REJECT
        mock_routing_result.reason.value = "system_overloaded"
        mock_routing_result.cost_estimate = None
        mock_router.route_consultation.return_value = mock_routing_result
        mock_get_router.return_value = mock_router
        
        websocket = self.create_mock_websocket("routing_fail_test")
        
        # Create session
        session = await chat_engine.create_session(
            "routing-user", security_context, websocket
        )
        
        # Send chat message
        chat_message = {
            'type': MessageType.CHAT_MESSAGE.value,
            'session_id': session.session_id,
            'content': 'This should be rejected'
        }
        
        await chat_engine.handle_websocket_message(websocket, chat_message)
        
        # Verify error message was sent
        error_messages = websocket.get_messages_by_type(MessageType.CHAT_ERROR.value)
        assert len(error_messages) > 0
        assert "temporarily unavailable" in error_messages[0]['error'].lower()
        
        # Session should still be active
        assert session.state == ChatSessionState.ACTIVE
    
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status')
    async def test_multiple_websocket_connections_integration(
        self, 
        mock_get_status, 
        mock_permission, 
        mock_flags,
        chat_engine, 
        security_context
    ):
        """Test multiple WebSocket connections to same session"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_get_status.return_value = mock_status
        
        websocket1 = self.create_mock_websocket("multi_ws_1")
        websocket2 = self.create_mock_websocket("multi_ws_2")
        
        # Create session with first WebSocket
        session = await chat_engine.create_session(
            "multi-ws-user", security_context, websocket1
        )
        
        # Add second WebSocket
        success = await chat_engine.add_websocket_to_session(session.session_id, websocket2)
        assert success
        
        # Both WebSockets should receive messages
        assert len(session.get_active_connections()) == 2
        
        # Send heartbeat to session
        await chat_engine._send_to_session(session, {
            'type': MessageType.CHAT_HEARTBEAT.value,
            'session_id': session.session_id,
            'status': 'test'
        })
        
        # Both WebSockets should have received the message
        assert len(websocket1.sent_messages) > 0
        assert len(websocket2.sent_messages) > 0
        
        # Remove one WebSocket
        success = await chat_engine.remove_websocket_from_session(session.session_id, websocket1)
        assert success
        assert len(session.get_active_connections()) == 1
    
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status')
    async def test_session_timeout_integration(
        self, 
        mock_get_status, 
        mock_permission, 
        mock_flags,
        chat_engine, 
        security_context
    ):
        """Test session timeout and cleanup integration"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_get_status.return_value = mock_status
        
        websocket = self.create_mock_websocket("timeout_test")
        
        # Create session
        session = await chat_engine.create_session(
            "timeout-user", security_context, websocket
        )
        
        # Manually set session as expired
        session.last_activity = datetime.utcnow() - timedelta(minutes=20)
        
        # Run cleanup
        await chat_engine._cleanup_expired_sessions()
        
        # Session should be removed
        assert session.session_id not in chat_engine.active_sessions
        assert "timeout-user" not in chat_engine.user_sessions
        
        # End message should have been sent
        end_messages = websocket.get_messages_by_type(MessageType.CHAT_SESSION_END.value)
        assert len(end_messages) > 0
        assert end_messages[0]['reason'] == "expired"
    
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status')
    async def test_concurrent_sessions_integration(
        self, 
        mock_get_status, 
        mock_permission, 
        mock_flags,
        chat_engine, 
        security_context
    ):
        """Test multiple concurrent sessions"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_get_status.return_value = mock_status
        
        # Create multiple sessions
        sessions = []
        websockets = []
        
        for i in range(3):
            websocket = self.create_mock_websocket(f"concurrent_ws_{i}")
            websockets.append(websocket)
            
            session = await chat_engine.create_session(
                f"concurrent-user-{i}", security_context, websocket
            )
            sessions.append(session)
        
        # All sessions should be active
        assert len(chat_engine.active_sessions) == 3
        assert chat_engine.stats['active_sessions'] == 3
        
        # Each user should have one session
        for i in range(3):
            user_sessions = await chat_engine.get_user_sessions(f"concurrent-user-{i}")
            assert len(user_sessions) == 1
            assert user_sessions[0]['session_id'] == sessions[i].session_id
        
        # Close all sessions
        for session in sessions:
            await chat_engine.close_session(session.session_id, "test_complete")
        
        # All sessions should be closed
        assert len(chat_engine.active_sessions) == 0
        assert chat_engine.stats['active_sessions'] == 0
    
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags')
    async def test_feature_flag_integration(self, mock_flags, chat_engine, security_context):
        """Test feature flag integration"""
        websocket = self.create_mock_websocket("feature_test")
        
        # Test with real-time chat disabled
        def feature_enabled(flag):
            if flag == FeatureFlag.REAL_TIME_CHAT:
                return False
            return True
        
        mock_flags.is_enabled.side_effect = feature_enabled
        
        # Should fail to create session
        with pytest.raises(Exception, match="Real-time chat is disabled"):
            await chat_engine.create_session(
                "feature-user", security_context, websocket
            )
        
        # Test with feature enabled
        mock_flags.is_enabled.return_value = True
        
        with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission') as mock_permission:
            with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status') as mock_get_status:
                mock_permission.return_value = True
                
                mock_status = MagicMock()
                mock_status.is_available = True
                mock_get_status.return_value = mock_status
                
                # Should succeed
                session = await chat_engine.create_session(
                    "feature-user", security_context, websocket
                )
                assert session.state == ChatSessionState.ACTIVE
    
    async def test_websocket_failure_handling_integration(self, chat_engine):
        """Test handling WebSocket connection failures"""
        # Create a failing WebSocket
        class FailingWebSocket:
            def __init__(self):
                self.sent_messages = []
                self.should_fail = False
            
            async def send(self, message):
                if self.should_fail:
                    raise ConnectionError("WebSocket connection failed")
                self.sent_messages.append(message)
        
        failing_ws = FailingWebSocket()
        
        with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission') as mock_permission:
                with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status') as mock_get_status:
                    # Setup mocks
                    mock_flags.is_enabled.return_value = True
                    mock_permission.return_value = True
                    
                    mock_status = MagicMock()
                    mock_status.is_available = True
                    mock_get_status.return_value = mock_status
                    
                    security_context = SecurityContext(
                        user_id="fail-test-user",
                        session_id="fail-test-session",
                        permission_level=PermissionLevel.USER,
                        authenticated=True,
                        session_start=datetime.utcnow(),
                        last_activity=datetime.utcnow()
                    )
                    
                    # Create session
                    session = await chat_engine.create_session(
                        "fail-user", security_context, failing_ws
                    )
                    
                    # Make WebSocket fail
                    failing_ws.should_fail = True
                    
                    # Try to send message - should handle failure gracefully
                    await chat_engine._send_to_session(session, {
                        'type': MessageType.CHAT_HEARTBEAT.value,
                        'session_id': session.session_id,
                        'status': 'test'
                    })
                    
                    # Session should still exist but WebSocket should be removed
                    assert session.session_id in chat_engine.active_sessions
    
    async def test_heartbeat_integration(self, chat_engine):
        """Test heartbeat functionality integration"""
        with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission') as mock_permission:
                with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status') as mock_get_status:
                    # Setup mocks
                    mock_flags.is_enabled.return_value = True
                    mock_permission.return_value = True
                    
                    mock_status = MagicMock()
                    mock_status.is_available = True
                    mock_get_status.return_value = mock_status
                    
                    security_context = SecurityContext(
                        user_id="heartbeat-user",
                        session_id="heartbeat-session",
                        permission_level=PermissionLevel.USER,
                        authenticated=True,
                        session_start=datetime.utcnow(),
                        last_activity=datetime.utcnow()
                    )
                    
                    websocket = self.create_mock_websocket("heartbeat_test")
                    
                    # Create session
                    session = await chat_engine.create_session(
                        "heartbeat-user", security_context, websocket
                    )
                    
                    old_activity = session.last_activity
                    
                    # Send heartbeat message
                    heartbeat_message = {
                        'type': MessageType.CHAT_HEARTBEAT.value,
                        'session_id': session.session_id
                    }
                    
                    await chat_engine.handle_websocket_message(websocket, heartbeat_message)
                    
                    # Should update last activity
                    assert session.last_activity > old_activity
                    
                    # Should send heartbeat response
                    heartbeat_responses = websocket.get_messages_by_type(MessageType.CHAT_HEARTBEAT.value)
                    assert len(heartbeat_responses) > 0
    
    async def test_performance_under_load_integration(self, chat_engine):
        """Test chat engine performance under load"""
        with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission') as mock_permission:
                with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status') as mock_get_status:
                    # Setup mocks
                    mock_flags.is_enabled.return_value = True
                    mock_permission.return_value = True
                    
                    mock_status = MagicMock()
                    mock_status.is_available = True
                    mock_get_status.return_value = mock_status
                    
                    security_context = SecurityContext(
                        user_id="load-test-user",
                        session_id="load-test-session",
                        permission_level=PermissionLevel.USER,
                        authenticated=True,
                        session_start=datetime.utcnow(),
                        last_activity=datetime.utcnow()
                    )
                    
                    # Create multiple sessions concurrently
                    tasks = []
                    for i in range(5):  # Within max_concurrent_sessions limit
                        websocket = self.create_mock_websocket(f"load_ws_{i}")
                        task = chat_engine.create_session(
                            f"load-user-{i}", security_context, websocket
                        )
                        tasks.append(task)
                    
                    # All should complete successfully
                    sessions = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    successful_sessions = [s for s in sessions if not isinstance(s, Exception)]
                    assert len(successful_sessions) == 5
                    
                    # All sessions should be active
                    assert len(chat_engine.active_sessions) == 5
                    
                    # Clean up
                    for session in successful_sessions:
                        await chat_engine.close_session(session.session_id, "load_test_complete")
    
    async def test_statistics_integration(self, chat_engine):
        """Test statistics tracking integration"""
        initial_stats = await chat_engine.get_chat_stats()
        initial_sessions = initial_stats['chat_stats']['sessions_created']
        
        with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission') as mock_permission:
                with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status') as mock_get_status:
                    # Setup mocks
                    mock_flags.is_enabled.return_value = True
                    mock_permission.return_value = True
                    
                    mock_status = MagicMock()
                    mock_status.is_available = True
                    mock_get_status.return_value = mock_status
                    
                    security_context = SecurityContext(
                        user_id="stats-user",
                        session_id="stats-session",
                        permission_level=PermissionLevel.USER,
                        authenticated=True,
                        session_start=datetime.utcnow(),
                        last_activity=datetime.utcnow()
                    )
                    
                    # Create and close a session
                    websocket = self.create_mock_websocket("stats_test")
                    session = await chat_engine.create_session(
                        "stats-user", security_context, websocket
                    )
                    
                    await chat_engine.close_session(session.session_id, "stats_test")
                    
                    # Check updated statistics
                    final_stats = await chat_engine.get_chat_stats()
                    
                    assert final_stats['chat_stats']['sessions_created'] == initial_sessions + 1
                    assert final_stats['chat_stats']['sessions_closed'] >= 1
                    assert 'avg_session_duration_minutes' in final_stats['chat_stats']
                    
                    # Check configuration is reported
                    assert 'configuration' in final_stats
                    assert final_stats['configuration']['session_timeout_minutes'] == 15
                    assert final_stats['configuration']['max_concurrent_sessions'] == 5


class TestGlobalChatEngineIntegration:
    """Test global chat engine instance integration"""
    
    async def test_singleton_behavior_integration(self):
        """Test that global chat engine maintains singleton behavior"""
        engine1 = await get_chat_engine()
        engine2 = await get_chat_engine()
        
        assert engine1 is engine2
        
        # Test state persistence across calls
        initial_sessions = engine1.stats['sessions_created']
        
        with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission') as mock_permission:
                with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status') as mock_get_status:
                    # Setup mocks
                    mock_flags.is_enabled.return_value = True
                    mock_permission.return_value = True
                    
                    mock_status = MagicMock()
                    mock_status.is_available = True
                    mock_get_status.return_value = mock_status
                    
                    security_context = SecurityContext(
                        user_id="singleton-user",
                        session_id="singleton-session",
                        permission_level=PermissionLevel.USER,
                        authenticated=True,
                        session_start=datetime.utcnow(),
                        last_activity=datetime.utcnow()
                    )
                    
                    websocket = MockWebSocket("singleton_test")
                    
                    # Create session with first instance
                    session = await engine1.create_session(
                        "singleton-user", security_context, websocket
                    )
                    
                    # Get third instance
                    engine3 = await get_chat_engine()
                    
                    # Should see the session created by engine1
                    assert engine3.stats['sessions_created'] == initial_sessions + 1
                    assert session.session_id in engine3.active_sessions


if __name__ == "__main__":
    pytest.main([__file__])