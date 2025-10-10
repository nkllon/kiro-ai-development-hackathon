"""
Real-Time Chat Engine

Provides real-time AI consultation chat with WebSocket integration and brownfield compatibility.
Manages chat sessions without interfering with existing Observatory WebSocket infrastructure.
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import weakref
from concurrent.futures import ThreadPoolExecutor

from .models import (
    ConsultationQuery, ConsultationResult, QueryPriority, ProcessingMode
)
from .request_processor import (
    get_request_processor, ContextInjectionMode, ProcessedRequest
)
from .consultation_router import get_consultation_router, RoutingDecision
from .doctor_status_manager import get_doctor_status
from .security_manager import SecurityContext, check_permission, ResourceType
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker
from .exceptions import ConsultationError, ValidationError, ProcessingError
from .health_checker import ComponentHealth

logger = logging.getLogger(__name__)


class ChatSessionState(str, Enum):
    """Chat session states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PROCESSING = "processing"
    WAITING = "waiting"
    PAUSED = "paused"
    CLOSING = "closing"
    CLOSED = "closed"
    ERROR = "error"


class MessageType(str, Enum):
    """WebSocket message types for chat"""
    CHAT_MESSAGE = "chat_message"
    CHAT_RESPONSE = "chat_response"
    CHAT_STATUS = "chat_status"
    CHAT_ERROR = "chat_error"
    CHAT_TYPING = "chat_typing"
    CHAT_COST_UPDATE = "chat_cost_update"
    CHAT_SESSION_START = "chat_session_start"
    CHAT_SESSION_END = "chat_session_end"
    CHAT_HEARTBEAT = "chat_heartbeat"


class ChatMessageRole(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    """Individual chat message"""
    message_id: str
    session_id: str
    role: ChatMessageRole
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for WebSocket transmission"""
        return {
            'message_id': self.message_id,
            'session_id': self.session_id,
            'role': self.role.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class ChatSession:
    """Real-time chat session"""
    session_id: str
    user_id: str
    security_context: SecurityContext
    state: ChatSessionState
    created_at: datetime
    last_activity: datetime
    messages: List[ChatMessage]
    websocket_connections: Set[Any]  # WeakSet would be better but this works
    total_cost: float
    message_count: int
    processing_time_total: float
    context_injection_mode: ContextInjectionMode
    session_metadata: Dict[str, Any]
    
    def __post_init__(self):
        """Initialize after creation"""
        # Use WeakSet for WebSocket connections to avoid memory leaks
        self.websocket_connections = weakref.WeakSet()
    
    def add_message(self, message: ChatMessage) -> None:
        """Add message to session"""
        self.messages.append(message)
        self.message_count += 1
        self.last_activity = datetime.utcnow()
    
    def add_websocket(self, websocket: Any) -> None:
        """Add WebSocket connection to session"""
        self.websocket_connections.add(websocket)
    
    def remove_websocket(self, websocket: Any) -> None:
        """Remove WebSocket connection from session"""
        try:
            self.websocket_connections.discard(websocket)
        except Exception:
            pass  # WeakSet may have already removed it
    
    def get_active_connections(self) -> List[Any]:
        """Get list of active WebSocket connections"""
        return list(self.websocket_connections)
    
    def update_cost(self, additional_cost: float) -> None:
        """Update session cost"""
        self.total_cost += additional_cost
        self.last_activity = datetime.utcnow()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired"""
        timeout = timedelta(minutes=timeout_minutes)
        return datetime.utcnow() - self.last_activity > timeout
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'message_count': self.message_count,
            'total_cost': self.total_cost,
            'processing_time_total': self.processing_time_total,
            'context_injection_mode': self.context_injection_mode.value,
            'active_connections': len(self.get_active_connections()),
            'session_metadata': self.session_metadata
        }


class RealTimeChatEngine:
    """
    Real-time chat engine with WebSocket integration
    
    Features:
    - WebSocket-based real-time communication
    - Session management with timeout and cleanup
    - Integration with Observatory context and routing
    - Cost tracking and budget enforcement
    - Circuit breaker protection
    - Brownfield compatibility with existing Observatory WebSockets
    """
    
    def __init__(
        self,
        session_timeout_minutes: int = 30,
        max_concurrent_sessions: int = 50,
        max_messages_per_session: int = 100,
        cleanup_interval_minutes: int = 5,
        heartbeat_interval_seconds: int = 30,
        max_message_length: int = 10000
    ):
        self.session_timeout_minutes = session_timeout_minutes
        self.max_concurrent_sessions = max_concurrent_sessions
        self.max_messages_per_session = max_messages_per_session
        self.cleanup_interval_minutes = cleanup_interval_minutes
        self.heartbeat_interval_seconds = heartbeat_interval_seconds
        self.max_message_length = max_message_length
        
        # Active sessions
        self.active_sessions: Dict[str, ChatSession] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids
        
        # WebSocket message handlers
        self.message_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            'sessions_created': 0,
            'sessions_closed': 0,
            'messages_processed': 0,
            'messages_failed': 0,
            'total_cost': 0.0,
            'avg_session_duration_minutes': 0.0,
            'active_sessions': 0,
            'websocket_connections': 0
        }
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
    
    async def initialize(self) -> None:
        """Initialize the chat engine"""
        try:
            logger.info("Initializing Real-Time Chat Engine")
            
            # Check if real-time chat is enabled
            if not await feature_flags.is_enabled(FeatureFlag.REAL_TIME_CHAT):
                logger.info("Real-time chat is disabled via feature flag")
                return
            
            # Register message handlers
            self._register_message_handlers()
            
            # Start background tasks
            await self._start_background_tasks()
            
            logger.info("Real-Time Chat Engine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Real-Time Chat Engine: {e}")
            # Don't raise - should degrade gracefully
    
    def _register_message_handlers(self) -> None:
        """Register WebSocket message handlers"""
        self.message_handlers = {
            MessageType.CHAT_MESSAGE.value: self._handle_chat_message,
            MessageType.CHAT_HEARTBEAT.value: self._handle_heartbeat,
            MessageType.CHAT_SESSION_START.value: self._handle_session_start,
            MessageType.CHAT_SESSION_END.value: self._handle_session_end,
        }
    
    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""
        try:
            # Start session cleanup task
            self.cleanup_task = asyncio.create_task(self._session_cleanup_loop())
            
            # Start heartbeat task
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
        except Exception as e:
            logger.error(f"Failed to start background tasks: {e}")
    
    @with_circuit_breaker('chat_session_creation')
    async def create_session(
        self,
        user_id: str,
        security_context: SecurityContext,
        websocket: Any,
        context_mode: ContextInjectionMode = ContextInjectionMode.FULL,
        session_metadata: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """Create a new chat session"""
        try:
            # Check if real-time chat is enabled
            if not await feature_flags.is_enabled(FeatureFlag.REAL_TIME_CHAT):
                raise ProcessingError("Real-time chat is disabled")
            
            # Check user permissions
            has_permission = await check_permission(
                security_context,
                ResourceType.SYSTEM_STATUS  # Basic permission for chat
            )
            if not has_permission:
                raise ValidationError("User does not have permission for real-time chat")
            
            # Check session limits
            if len(self.active_sessions) >= self.max_concurrent_sessions:
                raise ProcessingError("Maximum concurrent sessions reached")
            
            # Check user session limit (max 3 sessions per user)
            user_session_count = len(self.user_sessions.get(user_id, set()))
            if user_session_count >= 3:
                raise ProcessingError("Maximum sessions per user reached")
            
            # Check doctor availability
            doctor_status = await get_doctor_status()
            if not doctor_status.is_available:
                raise ProcessingError(f"Doctor is not available: {doctor_status.reason.value}")
            
            # Create session
            session_id = f"chat_{user_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                security_context=security_context,
                state=ChatSessionState.INITIALIZING,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                messages=[],
                websocket_connections=weakref.WeakSet(),
                total_cost=0.0,
                message_count=0,
                processing_time_total=0.0,
                context_injection_mode=context_mode,
                session_metadata=session_metadata or {}
            )
            
            # Add WebSocket connection
            session.add_websocket(websocket)
            
            # Register session
            self.active_sessions[session_id] = session
            
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
            self.user_sessions[user_id].add(session_id)
            
            # Update statistics
            self.stats['sessions_created'] += 1
            self.stats['active_sessions'] = len(self.active_sessions)
            
            # Set session to active
            session.state = ChatSessionState.ACTIVE
            
            # Send session start message
            await self._send_to_session(session, {
                'type': MessageType.CHAT_SESSION_START.value,
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'context_mode': context_mode.value,
                'message': 'Chat session started. How can I help you today?'
            })
            
            logger.info(f"Created chat session {session_id} for user {user_id}")
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create chat session for user {user_id}: {e}")
            raise
    
    async def close_session(
        self,
        session_id: str,
        reason: str = "user_requested"
    ) -> bool:
        """Close a chat session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            session.state = ChatSessionState.CLOSING
            
            # Send session end message
            await self._send_to_session(session, {
                'type': MessageType.CHAT_SESSION_END.value,
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'reason': reason,
                'session_summary': {
                    'duration_minutes': (datetime.utcnow() - session.created_at).total_seconds() / 60,
                    'message_count': session.message_count,
                    'total_cost': session.total_cost
                }
            })
            
            # Clean up session
            await self._cleanup_session(session_id)
            
            logger.info(f"Closed chat session {session_id}, reason: {reason}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to close session {session_id}: {e}")
            return False
    
    async def add_websocket_to_session(
        self,
        session_id: str,
        websocket: Any
    ) -> bool:
        """Add WebSocket connection to existing session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            session.add_websocket(websocket)
            self.stats['websocket_connections'] = sum(
                len(s.get_active_connections()) for s in self.active_sessions.values()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add WebSocket to session {session_id}: {e}")
            return False
    
    async def remove_websocket_from_session(
        self,
        session_id: str,
        websocket: Any
    ) -> bool:
        """Remove WebSocket connection from session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            session.remove_websocket(websocket)
            
            # If no more connections, close session
            if len(session.get_active_connections()) == 0:
                await self.close_session(session_id, "no_connections")
            
            self.stats['websocket_connections'] = sum(
                len(s.get_active_connections()) for s in self.active_sessions.values()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove WebSocket from session {session_id}: {e}")
            return False
    
    async def handle_websocket_message(
        self,
        websocket: Any,
        message_data: Dict[str, Any]
    ) -> None:
        """Handle incoming WebSocket message"""
        try:
            message_type = message_data.get('type')
            if not message_type:
                await self._send_error(websocket, "Missing message type")
                return
            
            # Check if this is a chat message
            if message_type not in self.message_handlers:
                # Not a chat message, ignore (brownfield compatibility)
                return
            
            # Handle the message
            handler = self.message_handlers[message_type]
            await handler(websocket, message_data)
            
        except Exception as e:
            logger.error(f"Failed to handle WebSocket message: {e}")
            await self._send_error(websocket, f"Message handling failed: {str(e)}")
    
    async def _handle_chat_message(
        self,
        websocket: Any,
        message_data: Dict[str, Any]
    ) -> None:
        """Handle incoming chat message"""
        try:
            session_id = message_data.get('session_id')
            content = message_data.get('content', '').strip()
            
            if not session_id or not content:
                await self._send_error(websocket, "Missing session_id or content")
                return
            
            session = self.active_sessions.get(session_id)
            if not session:
                await self._send_error(websocket, "Session not found")
                return
            
            # Validate message
            if len(content) > self.max_message_length:
                await self._send_error(websocket, "Message too long")
                return
            
            if session.message_count >= self.max_messages_per_session:
                await self._send_error(websocket, "Maximum messages per session reached")
                return
            
            # Set session to processing
            session.state = ChatSessionState.PROCESSING
            
            # Send typing indicator
            await self._send_to_session(session, {
                'type': MessageType.CHAT_TYPING.value,
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'typing': True
            })
            
            # Create user message
            user_message = ChatMessage(
                message_id=f"msg_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                session_id=session_id,
                role=ChatMessageRole.USER,
                content=content,
                timestamp=datetime.utcnow(),
                metadata={}
            )
            
            session.add_message(user_message)
            
            # Process the message
            await self._process_chat_message(session, user_message)
            
        except Exception as e:
            logger.error(f"Failed to handle chat message: {e}")
            await self._send_error(websocket, f"Chat message processing failed: {str(e)}")
    
    async def _process_chat_message(
        self,
        session: ChatSession,
        user_message: ChatMessage
    ) -> None:
        """Process chat message and generate response"""
        try:
            start_time = time.time()
            
            # Create consultation query
            query = ConsultationQuery(
                query_id=user_message.message_id,
                user_id=session.user_id,
                query_text=user_message.content,
                priority=QueryPriority.HIGH,  # Real-time chat gets high priority
                timestamp=user_message.timestamp
            )
            
            # Route the query
            router = await get_consultation_router()
            routing_result = await router.route_consultation(
                query, session.security_context
            )
            
            if routing_result.decision != RoutingDecision.REAL_TIME:
                # Should not happen for active chat sessions, but handle gracefully
                await self._send_to_session(session, {
                    'type': MessageType.CHAT_ERROR.value,
                    'session_id': session.session_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'error': f"Chat temporarily unavailable: {routing_result.reason.value}",
                    'suggested_action': 'Please try again in a few moments'
                })
                session.state = ChatSessionState.ACTIVE
                return
            
            # Process the request
            processor = await get_request_processor()
            processed_request = await processor.process_request(
                query,
                session.security_context,
                session.context_injection_mode
            )
            
            # Generate AI response (mock for now - will be implemented in next task)
            response_content = await self._generate_ai_response(processed_request)
            
            # Create assistant message
            assistant_message = ChatMessage(
                message_id=f"msg_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                session_id=session.session_id,
                role=ChatMessageRole.ASSISTANT,
                content=response_content,
                timestamp=datetime.utcnow(),
                metadata={
                    'processing_time_ms': (time.time() - start_time) * 1000,
                    'cost_estimate': routing_result.cost_estimate,
                    'context_mode': session.context_injection_mode.value
                }
            )
            
            session.add_message(assistant_message)
            
            # Update session cost
            if routing_result.cost_estimate:
                session.update_cost(routing_result.cost_estimate)
            
            # Update processing time
            session.processing_time_total += (time.time() - start_time)
            
            # Send response
            await self._send_to_session(session, {
                'type': MessageType.CHAT_RESPONSE.value,
                'session_id': session.session_id,
                'message': assistant_message.to_dict(),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Send cost update
            await self._send_to_session(session, {
                'type': MessageType.CHAT_COST_UPDATE.value,
                'session_id': session.session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'total_cost': session.total_cost,
                'message_cost': routing_result.cost_estimate
            })
            
            # Update statistics
            self.stats['messages_processed'] += 1
            self.stats['total_cost'] += routing_result.cost_estimate or 0
            
            # Set session back to active
            session.state = ChatSessionState.ACTIVE
            
        except Exception as e:
            logger.error(f"Failed to process chat message: {e}")
            self.stats['messages_failed'] += 1
            
            await self._send_to_session(session, {
                'type': MessageType.CHAT_ERROR.value,
                'session_id': session.session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'error': 'Failed to process message',
                'details': str(e)
            })
            
            session.state = ChatSessionState.ACTIVE
    
    async def _generate_ai_response(self, processed_request: ProcessedRequest) -> str:
        """Generate AI response using LLM service"""
        try:
            from .llm_service import get_llm_service
            
            llm_service = await get_llm_service()
            
            # Generate response using LLM service
            response = await llm_service.generate_response(
                processed_request=processed_request,
                stream=False,
                timeout=15.0  # Shorter timeout for real-time chat
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            # Fallback to simple response
            return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."
    
    async def _handle_heartbeat(
        self,
        websocket: Any,
        message_data: Dict[str, Any]
    ) -> None:
        """Handle heartbeat message"""
        try:
            session_id = message_data.get('session_id')
            if session_id and session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.last_activity = datetime.utcnow()
                
                # Send heartbeat response
                await self._send_websocket_message(websocket, {
                    'type': MessageType.CHAT_HEARTBEAT.value,
                    'session_id': session_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'status': 'alive'
                })
                
        except Exception as e:
            logger.error(f"Failed to handle heartbeat: {e}")
    
    async def _handle_session_start(
        self,
        websocket: Any,
        message_data: Dict[str, Any]
    ) -> None:
        """Handle session start request"""
        # This would typically be handled by create_session, but included for completeness
        pass
    
    async def _handle_session_end(
        self,
        websocket: Any,
        message_data: Dict[str, Any]
    ) -> None:
        """Handle session end request"""
        try:
            session_id = message_data.get('session_id')
            if session_id:
                await self.close_session(session_id, "user_requested")
                
        except Exception as e:
            logger.error(f"Failed to handle session end: {e}")
    
    async def _send_to_session(
        self,
        session: ChatSession,
        message: Dict[str, Any]
    ) -> None:
        """Send message to all WebSocket connections in session"""
        try:
            connections = session.get_active_connections()
            if not connections:
                return
            
            # Send to all active connections
            tasks = [
                self._send_websocket_message(conn, message)
                for conn in connections
            ]
            
            # Use gather with return_exceptions to handle individual connection failures
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log any failures
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(f"Failed to send message to WebSocket connection: {result}")
                    # Remove failed connection
                    try:
                        session.remove_websocket(connections[i])
                    except Exception:
                        pass
                        
        except Exception as e:
            logger.error(f"Failed to send message to session {session.session_id}: {e}")
    
    async def _send_websocket_message(
        self,
        websocket: Any,
        message: Dict[str, Any]
    ) -> None:
        """Send message to individual WebSocket connection"""
        try:
            # This is a mock implementation - in real usage, this would use the actual WebSocket send method
            # For example: await websocket.send(json.dumps(message))
            
            # For now, we'll just log the message
            logger.debug(f"Sending WebSocket message: {message}")
            
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            raise
    
    async def _send_error(
        self,
        websocket: Any,
        error_message: str
    ) -> None:
        """Send error message to WebSocket"""
        try:
            await self._send_websocket_message(websocket, {
                'type': MessageType.CHAT_ERROR.value,
                'timestamp': datetime.utcnow().isoformat(),
                'error': error_message
            })
            
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
    
    async def _session_cleanup_loop(self) -> None:
        """Background task to clean up expired sessions"""
        try:
            while True:
                await asyncio.sleep(self.cleanup_interval_minutes * 60)
                await self._cleanup_expired_sessions()
                
        except asyncio.CancelledError:
            logger.info("Session cleanup loop cancelled")
        except Exception as e:
            logger.error(f"Session cleanup loop error: {e}")
    
    async def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions"""
        try:
            expired_sessions = []
            
            for session_id, session in self.active_sessions.items():
                if session.is_expired(self.session_timeout_minutes):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                await self.close_session(session_id, "expired")
                
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
    
    async def _heartbeat_loop(self) -> None:
        """Background task to send heartbeats"""
        try:
            while True:
                await asyncio.sleep(self.heartbeat_interval_seconds)
                await self._send_heartbeats()
                
        except asyncio.CancelledError:
            logger.info("Heartbeat loop cancelled")
        except Exception as e:
            logger.error(f"Heartbeat loop error: {e}")
    
    async def _send_heartbeats(self) -> None:
        """Send heartbeat to all active sessions"""
        try:
            for session in self.active_sessions.values():
                if session.state == ChatSessionState.ACTIVE:
                    await self._send_to_session(session, {
                        'type': MessageType.CHAT_HEARTBEAT.value,
                        'session_id': session.session_id,
                        'timestamp': datetime.utcnow().isoformat(),
                        'status': 'ping'
                    })
                    
        except Exception as e:
            logger.error(f"Failed to send heartbeats: {e}")
    
    async def _cleanup_session(self, session_id: str) -> None:
        """Clean up session resources"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return
            
            # Update statistics
            session_duration = (datetime.utcnow() - session.created_at).total_seconds() / 60
            self._update_avg_session_duration(session_duration)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            # Remove from user sessions
            if session.user_id in self.user_sessions:
                self.user_sessions[session.user_id].discard(session_id)
                if not self.user_sessions[session.user_id]:
                    del self.user_sessions[session.user_id]
            
            # Update statistics
            self.stats['sessions_closed'] += 1
            self.stats['active_sessions'] = len(self.active_sessions)
            self.stats['websocket_connections'] = sum(
                len(s.get_active_connections()) for s in self.active_sessions.values()
            )
            
            session.state = ChatSessionState.CLOSED
            
        except Exception as e:
            logger.error(f"Failed to cleanup session {session_id}: {e}")
    
    def _update_avg_session_duration(self, duration_minutes: float) -> None:
        """Update average session duration"""
        try:
            sessions_closed = self.stats['sessions_closed']
            if sessions_closed > 0:
                current_avg = self.stats['avg_session_duration_minutes']
                self.stats['avg_session_duration_minutes'] = (
                    (current_avg * (sessions_closed - 1) + duration_minutes) / sessions_closed
                )
            else:
                self.stats['avg_session_duration_minutes'] = duration_minutes
                
        except Exception as e:
            logger.error(f"Failed to update average session duration: {e}")
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return None
            
            return session.to_dict()
            
        except Exception as e:
            logger.error(f"Failed to get session info for {session_id}: {e}")
            return None
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user"""
        try:
            session_ids = self.user_sessions.get(user_id, set())
            sessions = []
            
            for session_id in session_ids:
                session = self.active_sessions.get(session_id)
                if session:
                    sessions.append(session.to_dict())
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get user sessions for {user_id}: {e}")
            return []
    
    async def get_chat_stats(self) -> Dict[str, Any]:
        """Get current chat engine statistics"""
        try:
            return {
                'chat_stats': self.stats.copy(),
                'configuration': {
                    'session_timeout_minutes': self.session_timeout_minutes,
                    'max_concurrent_sessions': self.max_concurrent_sessions,
                    'max_messages_per_session': self.max_messages_per_session,
                    'cleanup_interval_minutes': self.cleanup_interval_minutes,
                    'heartbeat_interval_seconds': self.heartbeat_interval_seconds,
                    'max_message_length': self.max_message_length
                },
                'current_state': {
                    'active_sessions': len(self.active_sessions),
                    'total_websocket_connections': sum(
                        len(s.get_active_connections()) for s in self.active_sessions.values()
                    ),
                    'users_with_sessions': len(self.user_sessions)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get chat stats: {e}")
            return {'error': str(e)}
    
    async def get_health_status(self) -> ComponentHealth:
        """Get chat engine health status"""
        try:
            # Calculate health metrics
            active_sessions = len(self.active_sessions)
            session_utilization = active_sessions / self.max_concurrent_sessions
            
            success_rate = (
                self.stats['messages_processed'] / 
                max(1, self.stats['messages_processed'] + self.stats['messages_failed'])
            )
            
            # Determine health status
            if success_rate < 0.8:
                status = "critical"
                error_message = f"Low message success rate: {success_rate:.1%}"
            elif session_utilization > 0.9:
                status = "degraded"
                error_message = f"High session utilization: {session_utilization:.1%}"
            elif active_sessions == 0 and self.stats['sessions_created'] > 0:
                status = "degraded"
                error_message = "No active sessions"
            else:
                status = "healthy"
                error_message = None
            
            return ComponentHealth(
                component="realtime_chat_engine",
                status=status,
                response_time=0.0,  # Not applicable for chat engine
                error_message=error_message,
                metadata={
                    'active_sessions': active_sessions,
                    'session_utilization': session_utilization,
                    'success_rate': success_rate,
                    'total_cost': self.stats['total_cost'],
                    'avg_session_duration_minutes': self.stats['avg_session_duration_minutes']
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="realtime_chat_engine",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )
    
    async def shutdown(self) -> None:
        """Shutdown the chat engine"""
        try:
            logger.info("Shutting down Real-Time Chat Engine")
            
            # Cancel background tasks
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            # Close all active sessions
            session_ids = list(self.active_sessions.keys())
            for session_id in session_ids:
                await self.close_session(session_id, "shutdown")
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=False)
            
            logger.info("Real-Time Chat Engine shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during chat engine shutdown: {e}")


# Global chat engine instance
_chat_engine: Optional[RealTimeChatEngine] = None


async def get_chat_engine() -> RealTimeChatEngine:
    """Get the global chat engine instance"""
    global _chat_engine
    
    if _chat_engine is None:
        _chat_engine = RealTimeChatEngine()
        await _chat_engine.initialize()
    
    return _chat_engine