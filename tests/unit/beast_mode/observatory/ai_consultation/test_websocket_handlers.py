"""
Unit tests for WebSocket Handlers
Tests WebSocket connection management, message handling, and broadcasting functionality.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from fastapi import WebSocket
from fastapi.websockets import WebSocketState

from src.beast_mode.observatory.ai_consultation.websocket_handlers import (
    WebSocketConnectionManager, doctor_status_websocket_handler, 
    chat_websocket_handler, get_connection_manager
)
from src.beast_mode.observatory.ai_consultation.security_manager import SecurityContext
from src.beast_mode.observatory.ai_consultation.doctor_status_manager import DoctorStatus


class TestWebSocketConnectionManager:
    """Test WebSocketConnectionManager functionality"""
    
    @pytest.fixture
    def connection_manager(self):
        """Create connection manager for testing"""
        return WebSocketConnectionManager()
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket connection"""
        mock_ws = MagicMock(spec=WebSocket)
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()
        mock_ws.close = AsyncMock()
        mock_ws.client_state = WebSocketState.CONNECTED
        return mock_ws
    
    @pytest.fixture
    def mock_doctor_status(self):
        """Create mock doctor status"""
        return DoctorStatus(
            is_available=True,
            current_load=25,
            max_capacity=100,
            average_response_time=2.5,
            total_consultations=150,
            cost_today=12.50,
            last_updated=datetime.utcnow(),
            health_status="healthy",
            message="All systems operational",
            uptime_seconds=3600.0
        )
    
    async def test_connect_status_client_success(self, connection_manager, mock_websocket):
        """Test successful status client connection"""
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.get_doctor_status') as mock_get_status:
                mock_flags.is_enabled.return_value = True
                mock_get_status.return_value = MagicMock()
                
                result = await connection_manager.connect_status_client(mock_websocket, "test-user")
                
                assert result == True
                assert mock_websocket in connection_manager.status_connections
                assert connection_manager.metrics['total_connections'] == 1
                assert connection_manager.metrics['active_status_connections'] == 1
                mock_websocket.accept.assert_called_once()
    
    async def test_connect_status_client_disabled(self, connection_manager, mock_websocket):
        """Test status client connection when feature is disabled"""
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = False
            
            result = await connection_manager.connect_status_client(mock_websocket, "test-user")
            
            assert result == False
            assert mock_websocket not in connection_manager.status_connections
            mock_websocket.close.assert_called_once_with(code=1008, reason="Status updates disabled")
    
    async def test_connect_chat_client_success(self, connection_manager, mock_websocket):
        """Test successful chat client connection"""
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.check_permission') as mock_check_perm:
                mock_flags.is_enabled.return_value = True
                mock_check_perm.return_value = True
                
                security_context = SecurityContext(
                    user_id="test-user",
                    permissions=["consultation:chat"],
                    session_id="test-session"
                )
                
                result = await connection_manager.connect_chat_client(
                    mock_websocket, "test-session", "test-user", security_context
                )
                
                assert result == True
                assert "test-session" in connection_manager.chat_connections
                assert connection_manager.chat_connections["test-session"] == mock_websocket
                assert connection_manager.metrics['total_connections'] == 1
                assert connection_manager.metrics['active_chat_connections'] == 1
                mock_websocket.accept.assert_called_once()
    
    async def test_connect_chat_client_insufficient_permissions(self, connection_manager, mock_websocket):
        """Test chat client connection with insufficient permissions"""
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.check_permission') as mock_check_perm:
                mock_flags.is_enabled.return_value = True
                mock_check_perm.return_value = False  # Insufficient permissions
                
                security_context = SecurityContext(
                    user_id="test-user",
                    permissions=[],
                    session_id="test-session"
                )
                
                result = await connection_manager.connect_chat_client(
                    mock_websocket, "test-session", "test-user", security_context
                )
                
                assert result == False
                assert "test-session" not in connection_manager.chat_connections
                mock_websocket.close.assert_called_once_with(code=1008, reason="Insufficient permissions")
    
    async def test_connect_chat_client_replaces_existing(self, connection_manager, mock_websocket):
        """Test chat client connection replaces existing session"""
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            # Create first connection
            old_websocket = MagicMock(spec=WebSocket)
            old_websocket.client_state = WebSocketState.CONNECTED
            old_websocket.close = AsyncMock()
            connection_manager.chat_connections["test-session"] = old_websocket
            
            # Connect new client with same session ID
            result = await connection_manager.connect_chat_client(
                mock_websocket, "test-session", "test-user"
            )
            
            assert result == True
            assert connection_manager.chat_connections["test-session"] == mock_websocket
            old_websocket.close.assert_called_once()
    
    async def test_disconnect_client(self, connection_manager, mock_websocket):
        """Test client disconnection"""
        # Add client to status connections
        connection_manager.status_connections.add(mock_websocket)
        connection_manager.connection_metadata[mock_websocket] = {
            'type': 'status',
            'user_id': 'test-user',
            'connected_at': datetime.utcnow()
        }
        
        await connection_manager.disconnect_client(mock_websocket, "Test disconnect")
        
        assert mock_websocket not in connection_manager.status_connections
        assert connection_manager.metrics['connections_dropped'] == 1
        mock_websocket.close.assert_called_once_with(code=1000, reason="Test disconnect")
    
    async def test_broadcast_status_update(self, connection_manager, mock_doctor_status):
        """Test status update broadcasting"""
        # Add multiple status connections
        mock_ws1 = MagicMock(spec=WebSocket)
        mock_ws1.send_text = AsyncMock()
        mock_ws1.client_state = WebSocketState.CONNECTED
        
        mock_ws2 = MagicMock(spec=WebSocket)
        mock_ws2.send_text = AsyncMock()
        mock_ws2.client_state = WebSocketState.CONNECTED
        
        connection_manager.status_connections.add(mock_ws1)
        connection_manager.status_connections.add(mock_ws2)
        
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.get_doctor_status') as mock_get_status:
            mock_get_status.return_value = mock_doctor_status
            
            clients_notified = await connection_manager.broadcast_status_update(force=True)
            
            assert clients_notified == 2
            assert connection_manager.metrics['broadcast_count'] == 1
            mock_ws1.send_text.assert_called_once()
            mock_ws2.send_text.assert_called_once()
    
    async def test_broadcast_status_update_rate_limited(self, connection_manager, mock_doctor_status):
        """Test status update broadcasting with rate limiting"""
        # Set recent broadcast time
        connection_manager.last_status_broadcast = datetime.utcnow()
        connection_manager.status_broadcast_interval = 10.0  # 10 seconds
        
        # Add a status connection
        mock_ws = MagicMock(spec=WebSocket)
        connection_manager.status_connections.add(mock_ws)
        
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.get_doctor_status') as mock_get_status:
            mock_get_status.return_value = mock_doctor_status
            
            # Should be rate limited
            clients_notified = await connection_manager.broadcast_status_update(force=False)
            
            assert clients_notified == 0
            assert connection_manager.metrics['broadcast_count'] == 0
    
    async def test_broadcast_status_update_with_failures(self, connection_manager, mock_doctor_status):
        """Test status update broadcasting with some connection failures"""
        # Add connections - one good, one bad
        good_ws = MagicMock(spec=WebSocket)
        good_ws.send_text = AsyncMock()
        good_ws.client_state = WebSocketState.CONNECTED
        
        bad_ws = MagicMock(spec=WebSocket)
        bad_ws.send_text = AsyncMock(side_effect=Exception("Connection lost"))
        bad_ws.client_state = WebSocketState.CONNECTED
        bad_ws.close = AsyncMock()
        
        connection_manager.status_connections.add(good_ws)
        connection_manager.status_connections.add(bad_ws)
        connection_manager.connection_metadata[bad_ws] = {'type': 'status'}
        
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.get_doctor_status') as mock_get_status:
            mock_get_status.return_value = mock_doctor_status
            
            clients_notified = await connection_manager.broadcast_status_update(force=True)
            
            assert clients_notified == 1  # Only good connection succeeded
            assert bad_ws not in connection_manager.status_connections  # Bad connection removed
            bad_ws.close.assert_called_once()
    
    async def test_send_chat_message_success(self, connection_manager):
        """Test sending message to chat session"""
        mock_ws = MagicMock(spec=WebSocket)
        mock_ws.send_text = AsyncMock()
        mock_ws.client_state = WebSocketState.CONNECTED
        
        connection_manager.chat_connections["test-session"] = mock_ws
        connection_manager.connection_metadata[mock_ws] = {
            'type': 'chat',
            'session_id': 'test-session'
        }
        
        message = {'type': 'chat_response', 'content': 'Test response'}
        result = await connection_manager.send_chat_message("test-session", message)
        
        assert result == True
        assert connection_manager.metrics['messages_sent'] == 1
        mock_ws.send_text.assert_called_once()
    
    async def test_send_chat_message_no_session(self, connection_manager):
        """Test sending message to non-existent session"""
        message = {'type': 'chat_response', 'content': 'Test response'}
        result = await connection_manager.send_chat_message("nonexistent-session", message)
        
        assert result == False
    
    async def test_send_chat_message_failure(self, connection_manager):
        """Test sending message with WebSocket failure"""
        mock_ws = MagicMock(spec=WebSocket)
        mock_ws.send_text = AsyncMock(side_effect=Exception("Send failed"))
        mock_ws.client_state = WebSocketState.CONNECTED
        
        connection_manager.chat_connections["test-session"] = mock_ws
        
        message = {'type': 'chat_response', 'content': 'Test response'}
        result = await connection_manager.send_chat_message("test-session", message)
        
        assert result == False
        assert connection_manager.metrics['messages_failed'] == 1
    
    async def test_handle_status_message_get_status(self, connection_manager, mock_websocket, mock_doctor_status):
        """Test handling get_status message"""
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.get_doctor_status') as mock_get_status:
            mock_get_status.return_value = mock_doctor_status
            
            message = {'type': 'get_status'}
            await connection_manager.handle_status_message(mock_websocket, message)
            
            mock_websocket.send_text.assert_called_once()
            # Verify the sent message contains status data
            sent_data = mock_websocket.send_text.call_args[0][0]
            assert 'status_update' in sent_data
            assert 'is_available' in sent_data
    
    async def test_handle_status_message_ping(self, connection_manager, mock_websocket):
        """Test handling ping message"""
        message = {'type': 'ping'}
        await connection_manager.handle_status_message(mock_websocket, message)
        
        mock_websocket.send_text.assert_called_once()
        sent_data = mock_websocket.send_text.call_args[0][0]
        assert 'pong' in sent_data
    
    async def test_handle_status_message_unknown(self, connection_manager, mock_websocket):
        """Test handling unknown message type"""
        message = {'type': 'unknown_type'}
        
        # Should not raise exception
        await connection_manager.handle_status_message(mock_websocket, message)
        
        # Should not send any response
        mock_websocket.send_text.assert_not_called()
    
    async def test_handle_chat_message_ping(self, connection_manager, mock_websocket):
        """Test handling chat ping message"""
        message = {'type': 'ping'}
        await connection_manager.handle_chat_message(mock_websocket, message)
        
        mock_websocket.send_text.assert_called_once()
        sent_data = mock_websocket.send_text.call_args[0][0]
        assert 'pong' in sent_data
    
    async def test_handle_chat_message_chat(self, connection_manager, mock_websocket):
        """Test handling chat message"""
        connection_manager.connection_metadata[mock_websocket] = {
            'type': 'chat',
            'session_id': 'test-session',
            'user_id': 'test-user'
        }
        
        message = {'type': 'chat_message', 'content': 'Hello doctor'}
        
        # Should not raise exception (integration with chat engine would be added later)
        await connection_manager.handle_chat_message(mock_websocket, message)
    
    async def test_cleanup_stale_connections(self, connection_manager):
        """Test cleanup of stale connections"""
        # Add stale connection
        stale_ws = MagicMock(spec=WebSocket)
        stale_ws.close = AsyncMock()
        stale_ws.client_state = WebSocketState.CONNECTED
        
        connection_manager.status_connections.add(stale_ws)
        connection_manager.connection_metadata[stale_ws] = {
            'type': 'status',
            'connected_at': datetime.utcnow() - timedelta(minutes=10),  # Stale
            'last_ping': datetime.utcnow() - timedelta(minutes=10)
        }
        
        # Add fresh connection
        fresh_ws = MagicMock(spec=WebSocket)
        connection_manager.status_connections.add(fresh_ws)
        connection_manager.connection_metadata[fresh_ws] = {
            'type': 'status',
            'connected_at': datetime.utcnow(),
            'last_ping': datetime.utcnow()
        }
        
        cleaned_count = await connection_manager.cleanup_stale_connections()
        
        assert cleaned_count == 1
        assert stale_ws not in connection_manager.status_connections
        assert fresh_ws in connection_manager.status_connections
        stale_ws.close.assert_called_once()
    
    def test_get_connection_stats(self, connection_manager):
        """Test connection statistics retrieval"""
        # Add some connections
        mock_ws1 = MagicMock()
        mock_ws2 = MagicMock()
        
        connection_manager.status_connections.add(mock_ws1)
        connection_manager.chat_connections["session-1"] = mock_ws2
        
        # Set some metrics
        connection_manager.metrics['messages_sent'] = 50
        connection_manager.metrics['messages_failed'] = 2
        connection_manager.metrics['broadcast_count'] = 10
        
        stats = connection_manager.get_connection_stats()
        
        assert stats['active_connections']['status'] == 1
        assert stats['active_connections']['chat'] == 1
        assert stats['active_connections']['total'] == 2
        assert stats['metrics']['messages_sent'] == 50
        assert stats['metrics']['messages_failed'] == 2
        assert stats['metrics']['broadcast_count'] == 10
    
    async def test_get_health_status_healthy(self, connection_manager):
        """Test health status when system is healthy"""
        # Set good metrics
        connection_manager.metrics['messages_sent'] = 100
        connection_manager.metrics['messages_failed'] = 2
        
        health = await connection_manager.get_health_status()
        
        assert health.component == "websocket_manager"
        assert health.status == "healthy"
        assert health.error_message is None
        assert health.metadata['messages_sent'] == 100
        assert health.metadata['messages_failed'] == 2
    
    async def test_get_health_status_high_failure_rate(self, connection_manager):
        """Test health status with high message failure rate"""
        # Set high failure rate
        connection_manager.metrics['messages_sent'] = 10
        connection_manager.metrics['messages_failed'] = 5  # 50% failure rate
        
        health = await connection_manager.get_health_status()
        
        assert health.status == "degraded"
        assert "high message failure rate" in health.error_message.lower()
    
    async def test_get_health_status_high_connection_count(self, connection_manager):
        """Test health status with high connection count"""
        # Add many mock connections
        for i in range(1001):  # Exceed threshold of 1000
            mock_ws = MagicMock()
            connection_manager.status_connections.add(mock_ws)
        
        health = await connection_manager.get_health_status()
        
        assert health.status == "degraded"
        assert "high connection count" in health.error_message.lower()


class TestWebSocketHandlers:
    """Test WebSocket handler functions"""
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket for handler testing"""
        mock_ws = MagicMock(spec=WebSocket)
        mock_ws.accept = AsyncMock()
        mock_ws.receive_text = AsyncMock()
        mock_ws.send_text = AsyncMock()
        mock_ws.close = AsyncMock()
        mock_ws.client_state = WebSocketState.CONNECTED
        return mock_ws
    
    async def test_doctor_status_websocket_handler_success(self, mock_websocket):
        """Test successful doctor status WebSocket handler"""
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.connection_manager') as mock_manager:
            mock_manager.connect_status_client = AsyncMock(return_value=True)
            mock_manager.handle_status_message = AsyncMock()
            mock_manager.disconnect_client = AsyncMock()
            
            # Mock WebSocket message sequence
            mock_websocket.receive_text.side_effect = [
                '{"type": "get_status"}',
                '{"type": "ping"}',
                Exception("WebSocket disconnected")  # Simulate disconnect
            ]
            
            # Run handler (should handle disconnect gracefully)
            await doctor_status_websocket_handler(mock_websocket, "test-user")
            
            mock_manager.connect_status_client.assert_called_once_with(mock_websocket, "test-user")
            assert mock_manager.handle_status_message.call_count == 2
            mock_manager.disconnect_client.assert_called_once()
    
    async def test_doctor_status_websocket_handler_connection_failed(self, mock_websocket):
        """Test doctor status WebSocket handler when connection fails"""
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.connection_manager') as mock_manager:
            mock_manager.connect_status_client = AsyncMock(return_value=False)
            mock_manager.disconnect_client = AsyncMock()
            
            # Run handler
            await doctor_status_websocket_handler(mock_websocket, "test-user")
            
            mock_manager.connect_status_client.assert_called_once()
            # Should not try to receive messages if connection failed
            mock_websocket.receive_text.assert_not_called()
    
    async def test_chat_websocket_handler_success(self, mock_websocket):
        """Test successful chat WebSocket handler"""
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.connection_manager') as mock_manager:
            mock_manager.connect_chat_client = AsyncMock(return_value=True)
            mock_manager.handle_chat_message = AsyncMock()
            mock_manager.disconnect_client = AsyncMock()
            
            # Mock WebSocket message sequence
            mock_websocket.receive_text.side_effect = [
                '{"type": "chat_message", "content": "Hello"}',
                '{"type": "ping"}',
                Exception("WebSocket disconnected")  # Simulate disconnect
            ]
            
            security_context = SecurityContext(
                user_id="test-user",
                permissions=["consultation:chat"],
                session_id="test-session"
            )
            
            # Run handler
            await chat_websocket_handler(
                mock_websocket, "test-session", "test-user", security_context
            )
            
            mock_manager.connect_chat_client.assert_called_once_with(
                mock_websocket, "test-session", "test-user", security_context
            )
            assert mock_manager.handle_chat_message.call_count == 2
            mock_manager.disconnect_client.assert_called_once()
    
    async def test_chat_websocket_handler_connection_failed(self, mock_websocket):
        """Test chat WebSocket handler when connection fails"""
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.connection_manager') as mock_manager:
            mock_manager.connect_chat_client = AsyncMock(return_value=False)
            mock_manager.disconnect_client = AsyncMock()
            
            # Run handler
            await chat_websocket_handler(mock_websocket, "test-session", "test-user")
            
            mock_manager.connect_chat_client.assert_called_once()
            # Should not try to receive messages if connection failed
            mock_websocket.receive_text.assert_not_called()
    
    async def test_websocket_handler_invalid_json(self, mock_websocket):
        """Test WebSocket handler with invalid JSON messages"""
        with patch('src.beast_mode.observatory.ai_consultation.websocket_handlers.connection_manager') as mock_manager:
            mock_manager.connect_status_client = AsyncMock(return_value=True)
            mock_manager.handle_status_message = AsyncMock()
            mock_manager.disconnect_client = AsyncMock()
            
            # Mock invalid JSON message
            mock_websocket.receive_text.side_effect = [
                'invalid json',
                Exception("WebSocket disconnected")
            ]
            
            # Should handle invalid JSON gracefully
            await doctor_status_websocket_handler(mock_websocket, "test-user")
            
            # Should not call handle_status_message for invalid JSON
            mock_manager.handle_status_message.assert_not_called()


class TestGlobalConnectionManager:
    """Test global connection manager instance"""
    
    def test_get_connection_manager_singleton(self):
        """Test that get_connection_manager returns singleton"""
        manager1 = get_connection_manager()
        manager2 = get_connection_manager()
        
        assert manager1 is manager2
        assert isinstance(manager1, WebSocketConnectionManager)


if __name__ == "__main__":
    pytest.main([__file__])