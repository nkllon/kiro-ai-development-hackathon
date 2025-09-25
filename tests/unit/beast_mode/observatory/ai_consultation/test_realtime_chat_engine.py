"""
Unit tests for RealTimeChatEngine
Tests chat session management, WebSocket integration, and brownfield compatibility.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

from src.beast_mode.observatory.ai_consultation.realtime_chat_engine import (
    RealTimeChatEngine, ChatSession, ChatMessage, ChatSessionState, 
    MessageType, ChatMessageRole, ContextInjectionMode, get_chat_engine
)
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationQuery, QueryPriority
)
from src.beast_mode.observatory.ai_consultation.security_manager import (
    SecurityContext, PermissionLevel
)
from src.beast_mode.observatory.ai_consultation.exceptions import (
    ValidationError, ProcessingError
)


class MockWebSocket:
    """Mock WebSocket for testing"""
    def __init__(self, websocket_id: str = "mock_ws"):
        self.websocket_id = websocket_id
        self.sent_messages = []
        self.closed = False
    
    async def send(self, message: str):
        """Mock send method"""
        if not self.closed:
            self.sent_messages.append(message)
    
    def close(self):
        """Mock close method"""
        self.closed = True


class TestChatMessage:
    """Test ChatMessage functionality"""
    
    def test_chat_message_creation(self):
        """Test creating a chat message"""
        message = ChatMessage(
            message_id="test-msg-123",
            session_id="test-session",
            role=ChatMessageRole.USER,
            content="Hello, how are you?",
            timestamp=datetime.utcnow(),
            metadata={"test": "data"}
        )
        
        assert message.message_id == "test-msg-123"
        assert message.session_id == "test-session"
        assert message.role == ChatMessageRole.USER
        assert message.content == "Hello, how are you?"
        assert message.metadata["test"] == "data"
    
    def test_chat_message_to_dict(self):
        """Test converting chat message to dictionary"""
        timestamp = datetime.utcnow()
        message = ChatMessage(
            message_id="test-msg-123",
            session_id="test-session",
            role=ChatMessageRole.ASSISTANT,
            content="I'm doing well, thank you!",
            timestamp=timestamp,
            metadata={"cost": 0.05}
        )
        
        message_dict = message.to_dict()
        
        assert message_dict['message_id'] == "test-msg-123"
        assert message_dict['session_id'] == "test-session"
        assert message_dict['role'] == "assistant"
        assert message_dict['content'] == "I'm doing well, thank you!"
        assert message_dict['timestamp'] == timestamp.isoformat()
        assert message_dict['metadata']['cost'] == 0.05


class TestChatSession:
    """Test ChatSession functionality"""
    
    @pytest.fixture
    def sample_security_context(self):
        """Create sample security context"""
        return SecurityContext(
            user_id="test-user",
            session_id="test-session",
            permission_level=PermissionLevel.USER,
            authenticated=True,
            session_start=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
    
    def test_chat_session_creation(self, sample_security_context):
        """Test creating a chat session"""
        session = ChatSession(
            session_id="test-session-123",
            user_id="test-user",
            security_context=sample_security_context,
            state=ChatSessionState.ACTIVE,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            messages=[],
            websocket_connections=set(),
            total_cost=0.0,
            message_count=0,
            processing_time_total=0.0,
            context_injection_mode=ContextInjectionMode.FULL,
            session_metadata={}
        )
        
        assert session.session_id == "test-session-123"
        assert session.user_id == "test-user"
        assert session.state == ChatSessionState.ACTIVE
        assert session.total_cost == 0.0
        assert session.message_count == 0
        assert len(session.messages) == 0
    
    def test_add_message(self, sample_security_context):
        """Test adding message to session"""
        session = ChatSession(
            session_id="test-session",
            user_id="test-user",
            security_context=sample_security_context,
            state=ChatSessionState.ACTIVE,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            messages=[],
            websocket_connections=set(),
            total_cost=0.0,
            message_count=0,
            processing_time_total=0.0,
            context_injection_mode=ContextInjectionMode.FULL,
            session_metadata={}
        )
        
        message = ChatMessage(
            message_id="test-msg",
            session_id="test-session",
            role=ChatMessageRole.USER,
            content="Test message",
            timestamp=datetime.utcnow(),
            metadata={}
        )
        
        initial_activity = session.last_activity
        session.add_message(message)
        
        assert len(session.messages) == 1
        assert session.message_count == 1
        assert session.messages[0] == message
        assert session.last_activity > initial_activity
    
    def test_websocket_management(self, sample_security_context):
        """Test WebSocket connection management"""
        session = ChatSession(
            session_id="test-session",
            user_id="test-user",
            security_context=sample_security_context,
            state=ChatSessionState.ACTIVE,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            messages=[],
            websocket_connections=set(),
            total_cost=0.0,
            message_count=0,
            processing_time_total=0.0,
            context_injection_mode=ContextInjectionMode.FULL,
            session_metadata={}
        )
        
        ws1 = MockWebSocket("ws1")
        ws2 = MockWebSocket("ws2")
        
        # Add WebSockets
        session.add_websocket(ws1)
        session.add_websocket(ws2)
        
        connections = session.get_active_connections()
        assert len(connections) == 2
        assert ws1 in connections
        assert ws2 in connections
        
        # Remove WebSocket
        session.remove_websocket(ws1)
        connections = session.get_active_connections()
        assert len(connections) == 1
        assert ws2 in connections
        assert ws1 not in connections
    
    def test_cost_update(self, sample_security_context):
        """Test updating session cost"""
        session = ChatSession(
            session_id="test-session",
            user_id="test-user",
            security_context=sample_security_context,
            state=ChatSessionState.ACTIVE,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            messages=[],
            websocket_connections=set(),
            total_cost=0.0,
            message_count=0,
            processing_time_total=0.0,
            context_injection_mode=ContextInjectionMode.FULL,
            session_metadata={}
        )
        
        initial_cost = session.total_cost
        initial_activity = session.last_activity
        
        session.update_cost(0.25)
        
        assert session.total_cost == initial_cost + 0.25
        assert session.last_activity > initial_activity
    
    def test_session_expiration(self, sample_security_context):
        """Test session expiration check"""
        # Create session with old last_activity
        old_time = datetime.utcnow() - timedelta(minutes=45)
        
        session = ChatSession(
            session_id="test-session",
            user_id="test-user",
            security_context=sample_security_context,
            state=ChatSessionState.ACTIVE,
            created_at=old_time,
            last_activity=old_time,
            messages=[],
            websocket_connections=set(),
            total_cost=0.0,
            message_count=0,
            processing_time_total=0.0,
            context_injection_mode=ContextInjectionMode.FULL,
            session_metadata={}
        )
        
        # Should be expired with 30 minute timeout
        assert session.is_expired(30)
        
        # Should not be expired with 60 minute timeout
        assert not session.is_expired(60)
    
    def test_session_to_dict(self, sample_security_context):
        """Test converting session to dictionary"""
        session = ChatSession(
            session_id="test-session",
            user_id="test-user",
            security_context=sample_security_context,
            state=ChatSessionState.ACTIVE,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            messages=[],
            websocket_connections=set(),
            total_cost=1.25,
            message_count=5,
            processing_time_total=2.5,
            context_injection_mode=ContextInjectionMode.SUMMARY,
            session_metadata={"test": "data"}
        )
        
        session_dict = session.to_dict()
        
        assert session_dict['session_id'] == "test-session"
        assert session_dict['user_id'] == "test-user"
        assert session_dict['state'] == "active"
        assert session_dict['total_cost'] == 1.25
        assert session_dict['message_count'] == 5
        assert session_dict['processing_time_total'] == 2.5
        assert session_dict['context_injection_mode'] == "summary"
        assert session_dict['session_metadata']['test'] == "data"


class TestRealTimeChatEngine:
    """Test RealTimeChatEngine functionality"""
    
    @pytest.fixture
    async def chat_engine(self):
        """Create chat engine instance for testing"""
        engine = RealTimeChatEngine(
            session_timeout_minutes=30,
            max_concurrent_sessions=10,
            max_messages_per_session=50,
            cleanup_interval_minutes=5,
            heartbeat_interval_seconds=30,
            max_message_length=1000
        )
        await engine.initialize()
        return engine
    
    @pytest.fixture
    def sample_security_context(self):
        """Create sample security context"""
        return SecurityContext(
            user_id="test-user",
            session_id="test-session",
            permission_level=PermissionLevel.USER,
            authenticated=True,
            session_start=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket"""
        return MockWebSocket("test-ws")
    
    async def test_engine_initialization(self, chat_engine):
        """Test chat engine initializes correctly"""
        assert chat_engine.session_timeout_minutes == 30
        assert chat_engine.max_concurrent_sessions == 10
        assert chat_engine.max_messages_per_session == 50
        assert len(chat_engine.active_sessions) == 0
        assert len(chat_engine.user_sessions) == 0
        assert chat_engine.stats['sessions_created'] == 0
        assert len(chat_engine.message_handlers) > 0
    
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status')
    async def test_create_session_success(
        self, 
        mock_get_status, 
        mock_permission, 
        mock_flags,
        chat_engine, 
        sample_security_context, 
        mock_websocket
    ):
        """Test successful session creation"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_get_status.return_value = mock_status
        
        session = await chat_engine.create_session(
            "test-user", sample_security_context, mock_websocket
        )
        
        assert isinstance(session, ChatSession)
        assert session.user_id == "test-user"
        assert session.state == ChatSessionState.ACTIVE
        assert session.session_id in chat_engine.active_sessions
        assert "test-user" in chat_engine.user_sessions
        assert chat_engine.stats['sessions_created'] == 1
        assert chat_engine.stats['active_sessions'] == 1
    
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags')
    async def test_create_session_feature_disabled(
        self, 
        mock_flags,
        chat_engine, 
        sample_security_context, 
        mock_websocket
    ):
        """Test session creation when feature is disabled"""
        mock_flags.is_enabled.return_value = False
        
        with pytest.raises(ProcessingError, match="Real-time chat is disabled"):
            await chat_engine.create_session(
                "test-user", sample_security_context, mock_websocket
            )
    
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission')
    async def test_create_session_permission_denied(
        self, 
        mock_permission, 
        mock_flags,
        chat_engine, 
        sample_security_context, 
        mock_websocket
    ):
        """Test session creation when user lacks permissions"""
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = False
        
        with pytest.raises(ValidationError, match="does not have permission"):
            await chat_engine.create_session(
                "test-user", sample_security_context, mock_websocket
            )
    
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status')
    async def test_create_session_doctor_unavailable(
        self, 
        mock_get_status, 
        mock_permission, 
        mock_flags,
        chat_engine, 
        sample_security_context, 
        mock_websocket
    ):
        """Test session creation when doctor is unavailable"""
        mock_flags.is_enabled.return_value = True
        mock_permission.return_value = True
        
        mock_status = MagicMock()
        mock_status.is_available = False
        mock_status.reason.value = "budget_exhausted"
        mock_get_status.return_value = mock_status
        
        with pytest.raises(ProcessingError, match="Doctor is not available"):
            await chat_engine.create_session(
                "test-user", sample_security_context, mock_websocket
            )
    
    async def test_create_session_max_concurrent_reached(
        self, 
        chat_engine, 
        sample_security_context
    ):
        """Test session creation when max concurrent sessions reached"""
        # Fill up to max capacity
        chat_engine.max_concurrent_sessions = 2
        
        with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.check_permission') as mock_permission:
                with patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_doctor_status') as mock_get_status:
                    # Setup mocks
                    mock_flags.is_enabled.return_value = True
                    mock_permission.return_value = True
                    
                    mock_status = MagicMock()
                    mock_status.is_available = True
                    mock_get_status.return_value = mock_status
                    
                    # Create sessions up to limit
                    for i in range(2):
                        ws = MockWebSocket(f"ws{i}")
                        await chat_engine.create_session(f"user{i}", sample_security_context, ws)
                    
                    # Next session should fail
                    ws_overflow = MockWebSocket("ws_overflow")
                    with pytest.raises(ProcessingError, match="Maximum concurrent sessions reached"):
                        await chat_engine.create_session("user_overflow", sample_security_context, ws_overflow)
    
    async def test_close_session(self, chat_engine):
        """Test closing a session"""
        # Create a mock session
        session = ChatSession(
            session_id="test-session",
            user_id="test-user",
            security_context=MagicMock(),
            state=ChatSessionState.ACTIVE,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            messages=[],
            websocket_connections=set(),
            total_cost=0.0,
            message_count=0,
            processing_time_total=0.0,
            context_injection_mode=ContextInjectionMode.FULL,
            session_metadata={}
        )
        
        chat_engine.active_sessions["test-session"] = session
        chat_engine.user_sessions["test-user"] = {"test-session"}
        
        success = await chat_engine.close_session("test-session", "test_close")
        
        assert success
        assert "test-session" not in chat_engine.active_sessions
        assert "test-user" not in chat_engine.user_sessions
        assert chat_engine.stats['sessions_closed'] == 1
    
    async def test_websocket_management(self, chat_engine):
        """Test WebSocket connection management"""
        # Create a mock session
        session = ChatSession(
            session_id="test-session",
            user_id="test-user",
            security_context=MagicMock(),
            state=ChatSessionState.ACTIVE,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            messages=[],
            websocket_connections=set(),
            total_cost=0.0,
            message_count=0,
            processing_time_total=0.0,
            context_injection_mode=ContextInjectionMode.FULL,
            session_metadata={}
        )
        
        chat_engine.active_sessions["test-session"] = session
        
        ws1 = MockWebSocket("ws1")
        ws2 = MockWebSocket("ws2")
        
        # Add WebSockets
        success1 = await chat_engine.add_websocket_to_session("test-session", ws1)
        success2 = await chat_engine.add_websocket_to_session("test-session", ws2)
        
        assert success1
        assert success2
        assert len(session.get_active_connections()) == 2
        
        # Remove WebSocket
        success3 = await chat_engine.remove_websocket_from_session("test-session", ws1)
        assert success3
        assert len(session.get_active_connections()) == 1
    
    async def test_websocket_message_handling(self, chat_engine, mock_websocket):
        """Test WebSocket message handling"""
        # Test non-chat message (should be ignored for brownfield compatibility)
        non_chat_message = {
            'type': 'observatory_metric_update',
            'data': {'cpu': 75}
        }
        
        # Should not raise exception
        await chat_engine.handle_websocket_message(mock_websocket, non_chat_message)
        
        # Test invalid message
        invalid_message = {}
        
        await chat_engine.handle_websocket_message(mock_websocket, invalid_message)
        # Should send error message
        assert len(mock_websocket.sent_messages) > 0
    
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_consultation_router')
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine.get_request_processor')
    async def test_chat_message_processing(
        self, 
        mock_get_processor, 
        mock_get_router,
        chat_engine
    ):
        """Test processing chat messages"""
        # Setup mocks
        mock_router = AsyncMock()
        mock_routing_result = MagicMock()
        mock_routing_result.decision = "real_time"
        mock_routing_result.cost_estimate = 0.15
        mock_router.route_consultation.return_value = mock_routing_result
        mock_get_router.return_value = mock_router
        
        mock_processor = AsyncMock()
        mock_processed_request = MagicMock()
        mock_processed_request.processed_query_text = "What is the system status?"
        mock_processed_request.original_query.query_text = "What is the system status?"
        mock_processor.process_request.return_value = mock_processed_request
        mock_get_processor.return_value = mock_processor
        
        # Create session
        session = ChatSession(
            session_id="test-session",
            user_id="test-user",
            security_context=MagicMock(),
            state=ChatSessionState.ACTIVE,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            messages=[],
            websocket_connections=set(),
            total_cost=0.0,
            message_count=0,
            processing_time_total=0.0,
            context_injection_mode=ContextInjectionMode.FULL,
            session_metadata={}
        )
        
        chat_engine.active_sessions["test-session"] = session
        
        # Create user message
        user_message = ChatMessage(
            message_id="test-msg",
            session_id="test-session",
            role=ChatMessageRole.USER,
            content="What is the system status?",
            timestamp=datetime.utcnow(),
            metadata={}
        )
        
        # Process message
        await chat_engine._process_chat_message(session, user_message)
        
        # Verify processing
        assert session.message_count >= 1  # User message added
        assert session.total_cost == 0.15
        assert session.state == ChatSessionState.ACTIVE
        assert chat_engine.stats['messages_processed'] == 1
    
    async def test_ai_response_generation(self, chat_engine):
        """Test AI response generation (mock implementation)"""
        mock_request = MagicMock()
        mock_request.processed_query_text = "What is the system status?"
        mock_request.original_query.query_text = "What is the system status?"
        
        response = await chat_engine._generate_ai_response(mock_request)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "system" in response.lower()
    
    async def test_heartbeat_handling(self, chat_engine, mock_websocket):
        """Test heartbeat message handling"""
        # Create session
        session = ChatSession(
            session_id="test-session",
            user_id="test-user",
            security_context=MagicMock(),
            state=ChatSessionState.ACTIVE,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow() - timedelta(minutes=5),
            messages=[],
            websocket_connections=set(),
            total_cost=0.0,
            message_count=0,
            processing_time_total=0.0,
            context_injection_mode=ContextInjectionMode.FULL,
            session_metadata={}
        )
        
        chat_engine.active_sessions["test-session"] = session
        old_activity = session.last_activity
        
        # Handle heartbeat
        heartbeat_message = {
            'type': MessageType.CHAT_HEARTBEAT.value,
            'session_id': 'test-session'
        }
        
        await chat_engine._handle_heartbeat(mock_websocket, heartbeat_message)
        
        # Should update last activity
        assert session.last_activity > old_activity
    
    async def test_session_cleanup(self, chat_engine):
        """Test expired session cleanup"""
        # Create expired session
        old_time = datetime.utcnow() - timedelta(minutes=45)
        expired_session = ChatSession(
            session_id="expired-session",
            user_id="test-user",
            security_context=MagicMock(),
            state=ChatSessionState.ACTIVE,
            created_at=old_time,
            last_activity=old_time,
            messages=[],
            websocket_connections=set(),
            total_cost=0.0,
            message_count=0,
            processing_time_total=0.0,
            context_injection_mode=ContextInjectionMode.FULL,
            session_metadata={}
        )
        
        chat_engine.active_sessions["expired-session"] = expired_session
        chat_engine.user_sessions["test-user"] = {"expired-session"}
        
        # Run cleanup
        await chat_engine._cleanup_expired_sessions()
        
        # Session should be removed
        assert "expired-session" not in chat_engine.active_sessions
        assert "test-user" not in chat_engine.user_sessions
    
    async def test_session_info_retrieval(self, chat_engine):
        """Test getting session information"""
        # Create session
        session = ChatSession(
            session_id="info-session",
            user_id="test-user",
            security_context=MagicMock(),
            state=ChatSessionState.ACTIVE,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            messages=[],
            websocket_connections=set(),
            total_cost=1.50,
            message_count=10,
            processing_time_total=5.0,
            context_injection_mode=ContextInjectionMode.SUMMARY,
            session_metadata={"test": "data"}
        )
        
        chat_engine.active_sessions["info-session"] = session
        
        # Get session info
        info = await chat_engine.get_session_info("info-session")
        
        assert info is not None
        assert info['session_id'] == "info-session"
        assert info['user_id'] == "test-user"
        assert info['total_cost'] == 1.50
        assert info['message_count'] == 10
        
        # Test non-existent session
        no_info = await chat_engine.get_session_info("non-existent")
        assert no_info is None
    
    async def test_user_sessions_retrieval(self, chat_engine):
        """Test getting all sessions for a user"""
        # Create multiple sessions for user
        for i in range(3):
            session = ChatSession(
                session_id=f"user-session-{i}",
                user_id="multi-user",
                security_context=MagicMock(),
                state=ChatSessionState.ACTIVE,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                messages=[],
                websocket_connections=set(),
                total_cost=float(i),
                message_count=i * 5,
                processing_time_total=float(i),
                context_injection_mode=ContextInjectionMode.FULL,
                session_metadata={}
            )
            
            chat_engine.active_sessions[f"user-session-{i}"] = session
        
        chat_engine.user_sessions["multi-user"] = {"user-session-0", "user-session-1", "user-session-2"}
        
        # Get user sessions
        sessions = await chat_engine.get_user_sessions("multi-user")
        
        assert len(sessions) == 3
        for session_info in sessions:
            assert session_info['user_id'] == "multi-user"
            assert 'session_id' in session_info
    
    async def test_chat_statistics(self, chat_engine):
        """Test getting chat statistics"""
        # Set some test statistics
        chat_engine.stats['sessions_created'] = 10
        chat_engine.stats['messages_processed'] = 50
        chat_engine.stats['total_cost'] = 5.25
        
        stats = await chat_engine.get_chat_stats()
        
        assert 'chat_stats' in stats
        assert 'configuration' in stats
        assert 'current_state' in stats
        
        assert stats['chat_stats']['sessions_created'] == 10
        assert stats['chat_stats']['messages_processed'] == 50
        assert stats['chat_stats']['total_cost'] == 5.25
        
        assert stats['configuration']['session_timeout_minutes'] == 30
        assert stats['configuration']['max_concurrent_sessions'] == 10
    
    async def test_health_status_healthy(self, chat_engine):
        """Test health status when engine is healthy"""
        # Set good statistics
        chat_engine.stats['messages_processed'] = 100
        chat_engine.stats['messages_failed'] = 5
        
        health = await chat_engine.get_health_status()
        
        assert health.component == "realtime_chat_engine"
        assert health.status == "healthy"
        assert health.error_message is None
        assert 'success_rate' in health.metadata
        assert health.metadata['success_rate'] > 0.8
    
    async def test_health_status_degraded(self, chat_engine):
        """Test health status when engine is degraded"""
        # Fill sessions to near capacity
        chat_engine.max_concurrent_sessions = 10
        for i in range(10):
            session = ChatSession(
                session_id=f"session-{i}",
                user_id=f"user-{i}",
                security_context=MagicMock(),
                state=ChatSessionState.ACTIVE,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                messages=[],
                websocket_connections=set(),
                total_cost=0.0,
                message_count=0,
                processing_time_total=0.0,
                context_injection_mode=ContextInjectionMode.FULL,
                session_metadata={}
            )
            chat_engine.active_sessions[f"session-{i}"] = session
        
        health = await chat_engine.get_health_status()
        
        assert health.component == "realtime_chat_engine"
        assert health.status == "degraded"
        assert "utilization" in health.error_message.lower()
    
    async def test_health_status_critical(self, chat_engine):
        """Test health status when engine is critical"""
        # Set poor statistics
        chat_engine.stats['messages_processed'] = 100
        chat_engine.stats['messages_failed'] = 50  # High failure rate
        
        health = await chat_engine.get_health_status()
        
        assert health.component == "realtime_chat_engine"
        assert health.status == "critical"
        assert "success rate" in health.error_message.lower()
    
    async def test_engine_shutdown(self, chat_engine):
        """Test chat engine shutdown"""
        # Create some sessions
        for i in range(3):
            session = ChatSession(
                session_id=f"shutdown-session-{i}",
                user_id=f"user-{i}",
                security_context=MagicMock(),
                state=ChatSessionState.ACTIVE,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                messages=[],
                websocket_connections=set(),
                total_cost=0.0,
                message_count=0,
                processing_time_total=0.0,
                context_injection_mode=ContextInjectionMode.FULL,
                session_metadata={}
            )
            chat_engine.active_sessions[f"shutdown-session-{i}"] = session
        
        assert len(chat_engine.active_sessions) == 3
        
        # Shutdown
        await chat_engine.shutdown()
        
        # All sessions should be closed
        assert len(chat_engine.active_sessions) == 0


class TestGlobalChatEngine:
    """Test global chat engine functions"""
    
    @patch('src.beast_mode.observatory.ai_consultation.realtime_chat_engine._chat_engine', None)
    async def test_get_chat_engine(self):
        """Test getting global chat engine instance"""
        engine1 = await get_chat_engine()
        engine2 = await get_chat_engine()
        
        assert engine1 is engine2  # Should be singleton
        assert isinstance(engine1, RealTimeChatEngine)


if __name__ == "__main__":
    pytest.main([__file__])