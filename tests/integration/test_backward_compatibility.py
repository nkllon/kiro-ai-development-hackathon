"""
Comprehensive Backward Compatibility Tests

Validates that all existing functionality works identically after refactoring.
Tests both the old daemon client and new unified client interfaces.
"""

import pytest
import asyncio
import time
from unittest.mock import patch, AsyncMock, Mock
from datetime import datetime

from src.beast_mode.messaging.daemon_client import BeastModeClient as DaemonClient
from src.beast_mode.messaging.unified_client import BeastModeClient as UnifiedClient
from src.beast_mode.messaging.models import BeastModeMessage, MessageType
from src.beast_mode.messaging.transport import TransportFactory


class TestBackwardCompatibility:
    """Test backward compatibility between old and new implementations"""
    
    @pytest.fixture
    def mock_redis_available(self):
        """Mock Redis availability"""
        with patch('src.beast_mode.messaging.redis_foundation.REDIS_AVAILABLE', True):
            with patch('src.beast_mode.messaging.shared_state.REDIS_AVAILABLE', True):
                yield
    
    @pytest.fixture
    def mock_daemon(self):
        """Mock daemon for testing"""
        daemon = Mock()
        daemon.start_daemon.return_value = True
        daemon.stop_daemon.return_value = None
        daemon.send_message.return_value = None
        daemon.check_mail.return_value = []
        daemon.announce_presence.return_value = None
        daemon.send_spore.return_value = None
        daemon.get_status.return_value = {
            'is_running': True,
            'is_connected': True,
            'inbox_count': 0,
            'outbox_count': 0,
            'stats': {'messages_sent': 0, 'messages_received': 0}
        }
        daemon.get_unread_count.return_value = 0
        return daemon
    
    def test_daemon_client_interface_preserved(self, mock_daemon):
        """Test that original daemon client interface is preserved"""
        with patch('src.beast_mode.messaging.daemon_client.BeastModeDaemon') as mock_daemon_class:
            mock_daemon_class.return_value = mock_daemon
            
            # Create daemon client (old interface)
            client = DaemonClient('test_agent')
            
            # Test all original methods exist and work
            assert hasattr(client, 'start')
            assert hasattr(client, 'stop')
            assert hasattr(client, 'send_message')
            assert hasattr(client, 'check_messages')
            assert hasattr(client, 'process_messages')
            assert hasattr(client, 'register_handler')
            assert hasattr(client, 'get_status')
            assert hasattr(client, 'send_spore')
            
            # Test method signatures are unchanged
            result = client.start()
            assert isinstance(result, bool)
            
            client.stop()  # Should not raise
            
            message = BeastModeMessage(
                type=MessageType.SIMPLE_MESSAGE,
                source='test',
                payload={'text': 'test'}
            )
            client.send_message(message)  # Should not raise
            
            messages = client.check_messages()
            assert isinstance(messages, list)
            
            client.process_messages()  # Should not raise
            
            def handler(msg):
                pass
            
            client.register_handler(MessageType.SIMPLE_MESSAGE, handler)  # Should not raise
            
            status = client.get_status()
            assert isinstance(status, dict)
            
            client.send_spore({'test': 'data'})  # Should not raise
    
    @pytest.mark.asyncio
    async def test_unified_client_backward_compatibility(self, mock_redis_available):
        """Test that unified client provides backward compatibility"""
        with patch('src.beast_mode.messaging.unified_client.TransportFactory') as mock_factory:
            with patch('src.beast_mode.messaging.unified_client.BeastModeSharedState') as mock_state_class:
                # Set up mocks
                mock_transport = AsyncMock()
                mock_transport.initialize.return_value = True
                mock_transport.start_daemon.return_value = True
                mock_transport.stop_daemon.return_value = None
                mock_transport.send_message.return_value = True
                mock_transport.subscribe.return_value = True
                mock_transport.get_status.return_value = {'connected': True}
                mock_transport.get_capabilities.return_value = {'reliable_delivery': True}
                
                mock_shared_state = AsyncMock()
                mock_shared_state.initialize.return_value = True
                mock_shared_state.update_agent_state.return_value = True
                mock_shared_state.remove_agent_state.return_value = True
                mock_shared_state.increment_counter.return_value = 1
                mock_shared_state.shutdown.return_value = None
                
                mock_factory.create_transport.return_value = mock_transport
                mock_state_class.return_value = mock_shared_state
                
                # Create unified client
                client = UnifiedClient('test_agent')
                
                # Test backward compatibility methods exist
                assert hasattr(client, 'send_spore')
                assert hasattr(client, 'announce_presence')
                
                # Test they work without raising
                client.send_spore({'test': 'data'})
                client.announce_presence()
    
    @pytest.mark.asyncio
    async def test_message_format_compatibility(self, mock_redis_available):
        """Test that message formats remain compatible"""
        # Test that BeastModeMessage can be created with same parameters
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source='test_agent',
            payload={'text': 'test message'}
        )
        
        # Test all expected fields exist
        assert hasattr(message, 'id')
        assert hasattr(message, 'type')
        assert hasattr(message, 'source')
        assert hasattr(message, 'target')
        assert hasattr(message, 'payload')
        assert hasattr(message, 'timestamp')
        assert hasattr(message, 'priority')
        assert hasattr(message, 'correlation_id')
        
        # Test message can be serialized/deserialized
        message_dict = message.model_dump()
        assert isinstance(message_dict, dict)
        
        # Test message can be reconstructed
        reconstructed = BeastModeMessage(**message_dict)
        assert reconstructed.type == message.type
        assert reconstructed.source == message.source
        assert reconstructed.payload == message.payload
    
    def test_message_types_preserved(self):
        """Test that all message types are preserved"""
        # Test that all expected message types exist
        expected_types = [
            'SIMPLE_MESSAGE',
            'PROMPT_REQUEST',
            'PROMPT_RESPONSE',
            'AGENT_DISCOVERY',
            'AGENT_RESPONSE',
            'HELP_WANTED',
            'HELP_RESPONSE',
            'SPORE_DELIVERY',
            'SPORE_REQUEST',
            'SPORE_SPAWN',
            'TECHNICAL_EXCHANGE',
            'SYSTEM_HEALTH',
            'OFFICE_HOURS_ANNOUNCEMENT',
            'COLLABORATION_REQUEST',
            'COLLABORATION_RESPONSE',
            'COLLABORATION_START',
            'COLLABORATION_END',
            'COLLABORATION_UPDATE'
        ]
        
        for type_name in expected_types:
            assert hasattr(MessageType, type_name)
            assert isinstance(getattr(MessageType, type_name), str)
    
    def test_transport_factory_registration(self):
        """Test that transport factory works as expected"""
        # Test that redis transport is registered
        available = TransportFactory.get_available_transports()
        assert 'redis' in available
        
        # Test that transport can be created
        transport = TransportFactory.create_transport('redis', agent_id='test')
        assert transport is not None
        assert hasattr(transport, 'initialize')
        assert hasattr(transport, 'send_message')
        assert hasattr(transport, 'subscribe')
        assert hasattr(transport, 'start_daemon')
        assert hasattr(transport, 'stop_daemon')
        assert hasattr(transport, 'get_status')
        assert hasattr(transport, 'get_capabilities')
    
    @pytest.mark.asyncio
    async def test_configuration_compatibility(self, mock_redis_available):
        """Test that existing configuration patterns still work"""
        # Test that clients can be created with same parameters as before
        with patch('src.beast_mode.messaging.daemon_client.BeastModeDaemon') as mock_daemon_class:
            mock_daemon = Mock()
            mock_daemon.start_daemon.return_value = True
            mock_daemon_class.return_value = mock_daemon
            
            # Test daemon client with various configurations
            client1 = DaemonClient('agent1')
            client2 = DaemonClient('agent2', redis_url='redis://localhost:6379')
            client3 = DaemonClient('agent3', channel='custom_channel')
            client4 = DaemonClient('agent4', max_queue_size=500)
            
            # All should work without errors
            assert client1.agent_id == 'agent1'
            assert client2.agent_id == 'agent2'
            assert client3.agent_id == 'agent3'
            assert client4.agent_id == 'agent4'
    
    @pytest.mark.asyncio
    async def test_performance_no_regression(self, mock_redis_available):
        """Test that performance hasn't regressed significantly"""
        with patch('src.beast_mode.messaging.unified_client.TransportFactory') as mock_factory:
            with patch('src.beast_mode.messaging.unified_client.BeastModeSharedState') as mock_state_class:
                # Set up fast mocks
                mock_transport = AsyncMock()
                mock_transport.initialize.return_value = True
                mock_transport.start_daemon.return_value = True
                mock_transport.send_message.return_value = True
                mock_transport.subscribe.return_value = True
                
                mock_shared_state = AsyncMock()
                mock_shared_state.initialize.return_value = True
                mock_shared_state.update_agent_state.return_value = True
                mock_shared_state.increment_counter.return_value = 1
                
                mock_factory.create_transport.return_value = mock_transport
                mock_state_class.return_value = mock_shared_state
                
                # Test client startup time
                client = UnifiedClient('perf_test')
                
                start_time = time.time()
                await client.start()
                startup_time = time.time() - start_time
                
                # Should start quickly (under 1 second with mocks)
                assert startup_time < 1.0
                
                # Test message sending performance
                message = BeastModeMessage(
                    type=MessageType.SIMPLE_MESSAGE,
                    source='perf_test',
                    payload={'text': 'performance test'}
                )
                
                start_time = time.time()
                for _ in range(100):
                    await client.send_message(message)
                send_time = time.time() - start_time
                
                # Should send 100 messages quickly (under 1 second with mocks)
                assert send_time < 1.0
                
                await client.stop()
    
    @pytest.mark.asyncio
    async def test_error_handling_compatibility(self, mock_redis_available):
        """Test that error handling behaves consistently"""
        with patch('src.beast_mode.messaging.unified_client.TransportFactory') as mock_factory:
            with patch('src.beast_mode.messaging.unified_client.BeastModeSharedState') as mock_state_class:
                # Set up failing mocks
                mock_transport = AsyncMock()
                mock_transport.initialize.return_value = False  # Fail initialization
                
                mock_shared_state = AsyncMock()
                mock_shared_state.initialize.return_value = True
                
                mock_factory.create_transport.return_value = mock_transport
                mock_state_class.return_value = mock_shared_state
                
                client = UnifiedClient('error_test')
                
                # Should handle initialization failure gracefully
                result = await client.start()
                assert result is False
                assert not client.is_started
                
                # Should handle operations on non-started client
                message = BeastModeMessage(
                    type=MessageType.SIMPLE_MESSAGE,
                    source='error_test',
                    payload={'text': 'test'}
                )
                
                result = await client.send_message(message)
                assert result is False
    
    def test_import_compatibility(self):
        """Test that all expected imports still work"""
        # Test that all expected classes can be imported
        from src.beast_mode.messaging.models import BeastModeMessage, MessageType, AgentCapabilities
        from src.beast_mode.messaging.transport import BeastModeTransport, TransportFactory
        from src.beast_mode.messaging.daemon_client import BeastModeDaemon, BeastModeClient
        from src.beast_mode.messaging.unified_client import BeastModeClient as UnifiedClient
        from src.beast_mode.messaging.shared_state import BeastModeSharedState
        
        # All imports should succeed without errors
        assert BeastModeMessage is not None
        assert MessageType is not None
        assert AgentCapabilities is not None
        assert BeastModeTransport is not None
        assert TransportFactory is not None
        assert BeastModeDaemon is not None
        assert BeastModeClient is not None
        assert UnifiedClient is not None
        assert BeastModeSharedState is not None
    
    @pytest.mark.asyncio
    async def test_example_compatibility(self, mock_redis_available):
        """Test that existing example patterns still work"""
        with patch('src.beast_mode.messaging.daemon_client.BeastModeDaemon') as mock_daemon_class:
            mock_daemon = Mock()
            mock_daemon.start_daemon.return_value = True
            mock_daemon.check_mail.return_value = []
            mock_daemon.get_status.return_value = {'is_running': True}
            mock_daemon_class.return_value = mock_daemon
            
            # Test pattern from existing examples
            client = DaemonClient('example_agent')
            
            # Start client
            success = client.start()
            assert success
            
            # Register handler
            received_messages = []
            
            def message_handler(message):
                received_messages.append(message)
            
            client.register_handler(MessageType.SIMPLE_MESSAGE, message_handler)
            
            # Send message
            test_message = BeastModeMessage(
                type=MessageType.SIMPLE_MESSAGE,
                source='example_agent',
                payload={'text': 'Hello, Beast Mode!'}
            )
            
            client.send_message(test_message)
            
            # Process messages
            client.process_messages()
            
            # Check status
            status = client.get_status()
            assert isinstance(status, dict)
            
            # Send spore
            client.send_spore({
                'pattern_name': 'example_pattern',
                'description': 'An example spore',
                'code': 'print("Hello from spore!")'
            })
            
            # Stop client
            client.stop()
            
            # All operations should complete without errors


class TestRegressionPrevention:
    """Tests to prevent regression of specific functionality"""
    
    def test_message_id_generation(self):
        """Test that message IDs are still generated correctly"""
        message1 = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source='test',
            payload={}
        )
        
        message2 = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source='test',
            payload={}
        )
        
        # IDs should be unique
        assert message1.id != message2.id
        assert len(message1.id) > 0
        assert len(message2.id) > 0
    
    def test_timestamp_generation(self):
        """Test that timestamps are still generated correctly"""
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source='test',
            payload={}
        )
        
        assert message.timestamp is not None
        assert isinstance(message.timestamp, datetime)
    
    def test_priority_defaults(self):
        """Test that message priority defaults work correctly"""
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source='test',
            payload={}
        )
        
        assert message.priority == 5  # Default priority
        
        # Test custom priority
        high_priority = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source='test',
            payload={},
            priority=1
        )
        
        assert high_priority.priority == 1
    
    def test_payload_flexibility(self):
        """Test that payloads can contain various data types"""
        complex_payload = {
            'text': 'Hello',
            'number': 42,
            'list': [1, 2, 3],
            'nested': {'key': 'value'},
            'boolean': True,
            'null_value': None
        }
        
        message = BeastModeMessage(
            type=MessageType.TECHNICAL_EXCHANGE,
            source='test',
            payload=complex_payload
        )
        
        assert message.payload == complex_payload
        
        # Test serialization/deserialization
        message_dict = message.model_dump()
        reconstructed = BeastModeMessage(**message_dict)
        assert reconstructed.payload == complex_payload