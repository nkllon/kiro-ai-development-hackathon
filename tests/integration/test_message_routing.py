"""
Integration tests for Beast Mode message routing system
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.beast_mode.messaging.models import BeastModeMessage, MessageType, AgentCapabilities
from src.beast_mode.messaging.message_router import StandardMessageRouter, MessageTypeRegistry, message_type_registry
from src.beast_mode.messaging.message_handlers import MessageValidationError
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule



class TestStandardMessageRouter(ReflectiveModule):
    """Test StandardMessageRouter integration"""
    
    def test_initialization(self):
        """Test router initialization with callbacks"""
        callbacks = {
            'on_simple_message': Mock(),
            'on_prompt_request': Mock(),
            'on_agent_discovery': Mock()
        }
        
        router = StandardMessageRouter(
            agent_id="test_agent",
            capabilities=["python", "testing"],
            callbacks=callbacks
        )
        
        assert router.agent_id == "test_agent"
        assert router.capabilities == ["python", "testing"]
        assert router.callbacks == callbacks
        
        # Check that all standard message types are supported
        supported_types = router.get_supported_types()
        expected_types = [
            MessageType.SIMPLE_MESSAGE,
            MessageType.PROMPT_REQUEST,
            MessageType.PROMPT_RESPONSE,
            MessageType.AGENT_DISCOVERY,
            MessageType.AGENT_RESPONSE,
            MessageType.HELP_WANTED,
            MessageType.HELP_RESPONSE,
            MessageType.SPORE_DELIVERY,
            MessageType.SPORE_REQUEST,
            MessageType.TECHNICAL_EXCHANGE,
            MessageType.SYSTEM_HEALTH
        ]
        
        for msg_type in expected_types:
            assert msg_type in supported_types
    
    @pytest.mark.asyncio
    async def test_process_simple_message(self):
        """Test processing simple message"""
        callback_mock = Mock()
        callbacks = {'on_simple_message': callback_mock}
        
        router = StandardMessageRouter(
            agent_id="test_agent",
            callbacks=callbacks
        )
        
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="sender",
            payload={"content": "Hello world"}
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 0  # Simple messages don't generate responses
        callback_mock.assert_called_once_with("sender", "Hello world")
        
        # Check message was stored in history
        history = router.get_message_history(limit=1)
        assert len(history['received']) == 1
        assert history['received'][0].id == message.id
    
    @pytest.mark.asyncio
    async def test_process_prompt_request(self):
        """Test processing prompt request"""
        def prompt_processor(prompt):
            return f"Processed: {prompt}"
        
        callbacks = {'on_prompt_request': prompt_processor}
        
        router = StandardMessageRouter(
            agent_id="test_agent",
            callbacks=callbacks
        )
        
        message = BeastModeMessage(
            type=MessageType.PROMPT_REQUEST,
            source="sender",
            payload={"prompt": "What is 2+2?"}
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 1
        response = responses[0]
        
        assert response.type == MessageType.PROMPT_RESPONSE
        assert response.source == "test_agent"
        assert response.target == "sender"
        assert response.payload["response"] == "Processed: What is 2+2?"
        assert response.payload["original_prompt"] == "What is 2+2?"
        assert response.correlation_id == message.id
    
    @pytest.mark.asyncio
    async def test_process_agent_discovery(self):
        """Test processing agent discovery"""
        discovery_callback = Mock()
        callbacks = {'on_agent_discovery': discovery_callback}
        
        router = StandardMessageRouter(
            agent_id="test_agent",
            capabilities=["python", "testing"],
            callbacks=callbacks
        )
        
        # Create discovery message
        sender_caps = AgentCapabilities(
            agent_id="sender_agent",
            capabilities=["java", "docker"]
        )
        
        message = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="sender_agent",
            payload={"agent_capabilities": sender_caps.model_dump()}
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 1
        response = responses[0]
        
        assert response.type == MessageType.AGENT_RESPONSE
        assert response.source == "test_agent"
        assert response.target == "sender_agent"
        
        # Check our capabilities in response
        response_caps = AgentCapabilities(**response.payload["agent_capabilities"])
        assert response_caps.agent_id == "test_agent"
        assert response_caps.capabilities == ["python", "testing"]
        
        # Check callback was called
        discovery_callback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_help_wanted_can_help(self):
        """Test processing help wanted when we can help"""
        router = StandardMessageRouter(
            agent_id="test_agent",
            capabilities=["python", "testing", "docker"]
        )
        
        message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="needy_agent",
            payload={
                "required_capabilities": ["python", "docker"],
                "description": "Need help with Python Docker setup",
                "request_id": "help_123"
            }
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 1
        response = responses[0]
        
        assert response.type == MessageType.HELP_RESPONSE
        assert response.source == "test_agent"
        assert response.target == "needy_agent"
        assert response.payload["can_help"] is True
        assert response.payload["request_id"] == "help_123"
        assert set(response.payload["matching_capabilities"]) == {"python", "docker"}
        assert response.payload["confidence_score"] == 1.0
    
    @pytest.mark.asyncio
    async def test_process_help_wanted_cannot_help(self):
        """Test processing help wanted when we cannot help"""
        router = StandardMessageRouter(
            agent_id="test_agent",
            capabilities=["java", "spring"]  # Different capabilities
        )
        
        message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="needy_agent",
            payload={
                "required_capabilities": ["python", "docker"],
                "description": "Need help with Python Docker setup"
            }
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 0  # No response when we can't help
    
    @pytest.mark.asyncio
    async def test_process_spore_delivery(self):
        """Test processing spore delivery"""
        spore_callback = Mock()
        callbacks = {'on_spore_delivery': spore_callback}
        
        router = StandardMessageRouter(
            agent_id="test_agent",
            callbacks=callbacks
        )
        
        message = BeastModeMessage(
            type=MessageType.SPORE_DELIVERY,
            source="spore_sender",
            payload={
                "spore_name": "optimization_spore",
                "spore_content": "def optimize(): pass",
                "metadata": {"version": "1.0"}
            }
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 0  # Spore delivery doesn't generate response
        
        # Check callback was called
        spore_callback.assert_called_once()
        args = spore_callback.call_args[0]
        assert args[0] == "spore_sender"
        assert args[1] == "optimization_spore"
        assert args[2]["content"] == "def optimize(): pass"
        assert args[2]["metadata"] == {"version": "1.0"}
    
    @pytest.mark.asyncio
    async def test_process_spore_request(self):
        """Test processing spore request"""
        def spore_provider(spore_name):
            if spore_name == "test_spore":
                return {
                    "content": "def test(): pass",
                    "metadata": {"version": "1.0"}
                }
            return None
        
        callbacks = {'on_spore_request': spore_provider}
        
        router = StandardMessageRouter(
            agent_id="test_agent",
            callbacks=callbacks
        )
        
        message = BeastModeMessage(
            type=MessageType.SPORE_REQUEST,
            source="requester",
            payload={"spore_name": "test_spore"}
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 1
        response = responses[0]
        
        assert response.type == MessageType.SPORE_DELIVERY
        assert response.source == "test_agent"
        assert response.target == "requester"
        assert response.payload["spore_name"] == "test_spore"
        assert response.payload["spore_content"] == "def test(): pass"
    
    def test_track_sent_message(self):
        """Test tracking sent messages"""
        router = StandardMessageRouter(agent_id="test_agent")
        
        message = BeastModeMessage(
            type=MessageType.PROMPT_REQUEST,
            source="test_agent",
            target="other_agent",
            payload={"prompt": "Test"}
        )
        
        router.track_sent_message(message)
        
        assert message.id in router.sent_messages
        assert router.sent_messages[message.id] == message
    
    def test_update_capabilities(self):
        """Test updating capabilities"""
        router = StandardMessageRouter(
            agent_id="test_agent",
            capabilities=["python"]
        )
        
        new_capabilities = ["python", "docker", "kubernetes"]
        router.update_capabilities(new_capabilities)
        
        assert router.capabilities == new_capabilities
        
        # Check that handlers were updated (test with help handler)
        help_handlers = router.handlers.get(MessageType.HELP_WANTED, [])
        assert len(help_handlers) > 0
        
        for handler in help_handlers:
            if hasattr(handler, 'capabilities'):
                assert handler.capabilities == new_capabilities
    
    def test_set_callback(self):
        """Test setting callbacks"""
        router = StandardMessageRouter(agent_id="test_agent")
        
        new_callback = Mock()
        router.set_callback('on_simple_message', new_callback)
        
        assert router.callbacks['on_simple_message'] == new_callback
    
    def test_get_message_history(self):
        """Test getting message history"""
        router = StandardMessageRouter(agent_id="test_agent")
        
        # Add some messages to history
        sent_msg = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="test_agent",
            payload={"content": "Sent"}
        )
        
        received_msg = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="other_agent",
            payload={"content": "Received"}
        )
        
        router.track_sent_message(sent_msg)
        router.received_messages.append(received_msg)
        
        history = router.get_message_history()
        
        assert len(history['sent']) == 1
        assert len(history['received']) == 1
        assert history['sent'][0].id == sent_msg.id
        assert history['received'][0].id == received_msg.id
        
        # Test with limit
        limited_history = router.get_message_history(limit=0)
        assert len(limited_history['sent']) == 0
        assert len(limited_history['received']) == 0
    
    def test_get_correlation_info(self):
        """Test getting correlation information"""
        router = StandardMessageRouter(agent_id="test_agent")
        
        # Create request and response
        request = BeastModeMessage(
            type=MessageType.PROMPT_REQUEST,
            source="test_agent",
            payload={"prompt": "Test"}
        )
        
        response = BeastModeMessage(
            type=MessageType.PROMPT_RESPONSE,
            source="other_agent",
            payload={"response": "Answer"},
            correlation_id=request.id
        )
        
        router.track_sent_message(request)
        router.received_messages.append(response)
        
        # Get correlation info for request
        request_info = router.get_correlation_info(request.id)
        assert request_info is not None
        assert request_info['type'] == 'sent'
        assert request_info['original_message'].id == request.id
        assert len(request_info['related_messages']) == 1
        assert request_info['related_messages'][0].id == response.id
        
        # Get correlation info for response
        response_info = router.get_correlation_info(response.id)
        assert response_info is not None
        assert response_info['type'] == 'received'
        assert response_info['received_message'].id == response.id
        assert response_info['original_message'].id == request.id
    
    def test_validate_message_compatibility(self):
        """Test message compatibility validation"""
        router = StandardMessageRouter(agent_id="test_agent")
        
        # Valid message
        valid_data = {
            "type": "simple_message",
            "source": "sender",
            "payload": {"content": "Hello"}
        }
        
        result = router.validate_message_compatibility(valid_data)
        assert result['is_valid'] is True
        assert result['is_legacy'] is False
        assert len(result['errors']) == 0
        
        # Invalid message
        invalid_data = {
            "type": "simple_message"
            # Missing source
        }
        
        result = router.validate_message_compatibility(invalid_data)
        assert result['is_valid'] is False
        assert len(result['errors']) > 0
    
    def test_create_test_message(self):
        """Test creating test messages"""
        router = StandardMessageRouter(agent_id="test_agent")
        
        # Test simple message
        simple_msg = router.create_test_message(
            MessageType.SIMPLE_MESSAGE,
            content="Test content"
        )
        assert simple_msg.type == MessageType.SIMPLE_MESSAGE
        assert simple_msg.payload["content"] == "Test content"
        
        # Test prompt request
        prompt_msg = router.create_test_message(
            MessageType.PROMPT_REQUEST,
            prompt="Test prompt"
        )
        assert prompt_msg.type == MessageType.PROMPT_REQUEST
        assert prompt_msg.payload["prompt"] == "Test prompt"
        
        # Test help wanted
        help_msg = router.create_test_message(
            MessageType.HELP_WANTED,
            required_capabilities=["python"],
            description="Need help"
        )
        assert help_msg.type == MessageType.HELP_WANTED
        assert help_msg.payload["required_capabilities"] == ["python"]
        assert help_msg.payload["description"] == "Need help"
    
    def test_get_handler_info(self):
        """Test getting handler information"""
        router = StandardMessageRouter(
            agent_id="test_agent",
            capabilities=["python", "testing"]
        )
        
        info = router.get_handler_info()
        
        assert info['agent_id'] == "test_agent"
        assert info['capabilities'] == ["python", "testing"]
        assert 'handlers_by_type' in info
        assert 'total_handlers' in info
        assert 'callback_status' in info
        
        # Check that all message types have handlers
        expected_types = [t.value for t in MessageType]
        for msg_type in expected_types:
            assert msg_type in info['handlers_by_type']
    
    @pytest.mark.asyncio
    async def test_message_history_trimming(self):
        """Test that message history is trimmed to prevent memory growth"""
        router = StandardMessageRouter(agent_id="test_agent")
        router.max_history = 3  # Set small limit for testing
        
        # Add more messages than the limit
        for i in range(5):
            message = BeastModeMessage(
                type=MessageType.SIMPLE_MESSAGE,
                source="sender",
                payload={"content": f"Message {i}"}
            )
            await router.process_message(message)
        
        # Check that history was trimmed
        history = router.get_message_history()
        assert len(history['received']) <= router.max_history
        
        # Check that the most recent messages are kept
        last_message = history['received'][-1]
        assert last_message.payload["content"] == "Message 4"


class TestMessageTypeRegistry(ReflectiveModule):
    """Test MessageTypeRegistry"""
    
    def test_initialization(self):
        """Test registry initialization"""
        registry = MessageTypeRegistry()
        
        # Check that all message types are registered
        for msg_type in MessageType:
            assert msg_type in registry.type_info
    
    def test_get_type_info(self):
        """Test getting type information"""
        registry = MessageTypeRegistry()
        
        # Test known type
        info = registry.get_type_info(MessageType.PROMPT_REQUEST)
        assert info['description'] is not None
        assert 'required_fields' in info
        assert 'optional_fields' in info
        assert info['response_type'] == MessageType.PROMPT_RESPONSE
        
        # Test unknown type (shouldn't happen with enum, but test anyway)
        fake_type = "fake_type"
        info = registry.get_type_info(fake_type)
        assert info == {}
    
    def test_validate_payload(self):
        """Test payload validation"""
        registry = MessageTypeRegistry()
        
        # Valid prompt request payload
        valid_payload = {"prompt": "Test prompt", "context": "test"}
        result = registry.validate_payload(MessageType.PROMPT_REQUEST, valid_payload)
        
        assert result['is_valid'] is True
        assert len(result['missing_fields']) == 0
        
        # Invalid prompt request payload (missing required field)
        invalid_payload = {"context": "test"}  # Missing 'prompt'
        result = registry.validate_payload(MessageType.PROMPT_REQUEST, invalid_payload)
        
        assert result['is_valid'] is False
        assert 'prompt' in result['missing_fields']
        
        # Payload with extra fields
        extra_payload = {"prompt": "Test", "extra_field": "value"}
        result = registry.validate_payload(MessageType.PROMPT_REQUEST, extra_payload)
        
        assert result['is_valid'] is True
        assert 'extra_field' in result['extra_fields']
    
    def test_get_all_types(self):
        """Test getting all types"""
        registry = MessageTypeRegistry()
        
        all_types = registry.get_all_types()
        
        # Should include all MessageType enum values
        for msg_type in MessageType:
            assert msg_type in all_types
    
    def test_get_types_with_responses(self):
        """Test getting types that expect responses"""
        registry = MessageTypeRegistry()
        
        response_types = registry.get_types_with_responses()
        
        # Check known request/response pairs
        assert MessageType.PROMPT_REQUEST in response_types
        assert response_types[MessageType.PROMPT_REQUEST] == MessageType.PROMPT_RESPONSE
        
        assert MessageType.AGENT_DISCOVERY in response_types
        assert response_types[MessageType.AGENT_DISCOVERY] == MessageType.AGENT_RESPONSE
        
        # Check that response types themselves are not in the dict
        assert MessageType.PROMPT_RESPONSE not in response_types
        assert MessageType.AGENT_RESPONSE not in response_types
    
    def test_global_registry_instance(self):
        """Test that global registry instance exists"""
        assert message_type_registry is not None
        assert isinstance(message_type_registry, MessageTypeRegistry)
        
        # Test that it works
        info = message_type_registry.get_type_info(MessageType.SIMPLE_MESSAGE)
        assert info is not None
        assert 'description' in info


class TestMessageRoutingIntegration(ReflectiveModule):
    """Test complete message routing integration"""
    
    @pytest.mark.asyncio
    async def test_full_conversation_flow(self):
        """Test a complete conversation flow between agents"""
        # Create two routers representing different agents
        agent1_callbacks = {
            'on_prompt_request': lambda prompt: f"Agent1 processed: {prompt}"
        }
        
        agent2_callbacks = {
            'on_prompt_response': Mock()
        }
        
        agent1_router = StandardMessageRouter(
            agent_id="agent1",
            capabilities=["processing"],
            callbacks=agent1_callbacks
        )
        
        agent2_router = StandardMessageRouter(
            agent_id="agent2",
            capabilities=["requesting"],
            callbacks=agent2_callbacks
        )
        
        # Agent2 sends prompt request to Agent1
        request = BeastModeMessage(
            type=MessageType.PROMPT_REQUEST,
            source="agent2",
            target="agent1",
            payload={"prompt": "What is the meaning of life?"}
        )
        
        # Agent1 processes the request
        responses = await agent1_router.process_message(request)
        
        assert len(responses) == 1
        response = responses[0]
        
        # Agent2 receives the response
        await agent2_router.process_message(response)
        
        # Check that Agent2's callback was called
        agent2_callbacks['on_prompt_response'].assert_called_once()
        
        # Check correlation
        correlation_info = agent1_router.get_correlation_info(request.id)
        assert correlation_info is not None
        assert correlation_info['type'] == 'received'
    
    @pytest.mark.asyncio
    async def test_help_system_integration(self):
        """Test help system integration"""
        # Helper agent with Python capabilities
        helper_router = StandardMessageRouter(
            agent_id="helper_agent",
            capabilities=["python", "debugging"]
        )
        
        # Requester agent
        requester_callbacks = {'on_help_response': Mock()}
        requester_router = StandardMessageRouter(
            agent_id="requester_agent",
            capabilities=["frontend"],
            callbacks=requester_callbacks
        )
        
        # Requester sends help wanted
        help_request = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="requester_agent",
            payload={
                "required_capabilities": ["python", "debugging"],
                "description": "Need help debugging Python code",
                "request_id": "help_001"
            }
        )
        
        # Helper processes the request
        responses = await helper_router.process_message(help_request)
        
        assert len(responses) == 1
        help_response = responses[0]
        
        assert help_response.type == MessageType.HELP_RESPONSE
        assert help_response.payload["can_help"] is True
        assert help_response.payload["confidence_score"] == 1.0
        
        # Requester receives the response
        await requester_router.process_message(help_response)
        
        # Check that callback was called
        requester_callbacks['on_help_response'].assert_called_once()
    
    @pytest.mark.asyncio
    async def test_spore_sharing_integration(self):
        """Test spore sharing integration"""
        # Spore provider
        def spore_provider(spore_name):
            spores = {
                "optimization_spore": {
                    "content": "def optimize(data): return sorted(data)",
                    "metadata": {"version": "1.0", "author": "provider"}
                }
            }
            return spores.get(spore_name)
        
        provider_callbacks = {'on_spore_request': spore_provider}
        provider_router = StandardMessageRouter(
            agent_id="provider_agent",
            callbacks=provider_callbacks
        )
        
        # Spore receiver
        receiver_callbacks = {'on_spore_delivery': Mock()}
        receiver_router = StandardMessageRouter(
            agent_id="receiver_agent",
            callbacks=receiver_callbacks
        )
        
        # Receiver requests spore
        spore_request = BeastModeMessage(
            type=MessageType.SPORE_REQUEST,
            source="receiver_agent",
            target="provider_agent",
            payload={"spore_name": "optimization_spore"}
        )
        
        # Provider processes request
        responses = await provider_router.process_message(spore_request)
        
        assert len(responses) == 1
        spore_delivery = responses[0]
        
        assert spore_delivery.type == MessageType.SPORE_DELIVERY
        assert spore_delivery.payload["spore_name"] == "optimization_spore"
        assert "def optimize" in spore_delivery.payload["spore_content"]
        
        # Receiver gets the spore
        await receiver_router.process_message(spore_delivery)
        
        # Check that callback was called
        receiver_callbacks['on_spore_delivery'].assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling in message routing"""
        # Create router with callback that raises exception
        def failing_callback(source, content):
            raise Exception("Callback failed")
        
        callbacks = {'on_simple_message': failing_callback}
        router = StandardMessageRouter(
            agent_id="test_agent",
            callbacks=callbacks
        )
        
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="sender",
            payload={"content": "Hello"}
        )
        
        # Should not raise exception, but handle gracefully
        responses = await router.process_message(message)
        
        assert len(responses) == 0
        
        # Check that error was tracked in stats
        stats = router.get_handler_stats()

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

        assert stats['router_stats']['handler_errors'] > 0