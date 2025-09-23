"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.441760
"""






import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock
import asyncio

from src.beast_mode.messaging.models import BeastModeMessage, MessageType, AgentCapabilities
from src.beast_mode.messaging.message_handlers import (
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    SimpleMessageHandler, PromptRequestHandler, PromptResponseHandler,
    AgentDiscoveryHandler, AgentResponseHandler, HelpWantedHandler,
    HelpResponseHandler, SporeDeliveryHandler, SporeRequestHandler,
    TechnicalExchangeHandler, SystemHealthHandler, MessageRouter,
    MessageValidationError, MessageCompatibilityError
)


class TestSimpleMessageHandler(ReflectiveModule):
    """Test SimpleMessageHandler"""
    
    def test_supported_types(self):
        """Test supported message types"""
        handler = SimpleMessageHandler("test_agent")
        assert handler.get_supported_types() == [MessageType.SIMPLE_MESSAGE]
    
    def test_can_handle(self):
        """Test can_handle method"""
        handler = SimpleMessageHandler("test_agent")
        
        simple_msg = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="sender",
            payload={"content": "Hello"}
        )
        
        prompt_msg = BeastModeMessage(
            type=MessageType.PROMPT_REQUEST,
            source="sender",
            payload={"prompt": "Test"}
        )
        
        assert handler.can_handle(simple_msg) is True
        assert handler.can_handle(prompt_msg) is False
    
    @pytest.mark.asyncio
    async def test_handle_message(self):
        """Test message handling"""
        callback_mock = Mock()
        handler = SimpleMessageHandler("test_agent", message_callback=callback_mock)
        
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="sender",
            payload={"content": "Hello world"}
        )
        
        result = await handler._handle_with_stats(message)
        
        assert result is None  # Simple messages don't generate responses
        callback_mock.assert_called_once_with("sender", "Hello world")
        assert handler.handled_count == 1
    
    @pytest.mark.asyncio
    async def test_handle_message_no_callback(self):
        """Test handling without callback"""
        handler = SimpleMessageHandler("test_agent")
        
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="sender",
            payload={"content": "Hello"}
        )
        
        result = await handler._handle_with_stats(message)
        assert result is None
        assert handler.handled_count == 1


class TestPromptRequestHandler(ReflectiveModule):
    """Test PromptRequestHandler"""
    
    def test_supported_types(self):
        """Test supported message types"""
        handler = PromptRequestHandler("test_agent")
        assert handler.get_supported_types() == [MessageType.PROMPT_REQUEST]
    
    def test_validate_message(self):
        """Test message validation"""
        handler = PromptRequestHandler("test_agent")
        
        # Valid message
        valid_msg = BeastModeMessage(
            type=MessageType.PROMPT_REQUEST,
            source="sender",
            payload={"prompt": "Test prompt"}
        )
        handler.validate_message(valid_msg)  # Should not raise
        
        # Invalid message - missing prompt
        invalid_msg = BeastModeMessage(
            type=MessageType.PROMPT_REQUEST,
            source="sender",
            payload={}
        )
        
        with pytest.raises(MessageValidationError):
            handler.validate_message(invalid_msg)
    
    @pytest.mark.asyncio
    async def test_handle_message_with_processor(self):
        """Test handling with prompt processor"""
        processor_mock = Mock(return_value="Processed response")
        handler = PromptRequestHandler("test_agent", prompt_processor=processor_mock)
        
        message = BeastModeMessage(
            type=MessageType.PROMPT_REQUEST,
            source="sender",
            payload={"prompt": "Test prompt"}
        )
        
        result = await handler.handle_message(message)
        
        assert result is not None
        assert result.type == MessageType.PROMPT_RESPONSE
        assert result.source == "test_agent"
        assert result.target == "sender"
        assert result.payload["response"] == "Processed response"
        assert result.payload["original_prompt"] == "Test prompt"
        assert result.correlation_id == message.id
        
        processor_mock.assert_called_once_with("Test prompt")
    
    @pytest.mark.asyncio
    async def test_handle_message_without_processor(self):
        """Test handling without processor"""
        handler = PromptRequestHandler("test_agent")
        
        message = BeastModeMessage(
            type=MessageType.PROMPT_REQUEST,
            source="sender",
            payload={"prompt": "Test prompt"}
        )
        
        result = await handler.handle_message(message)
        
        assert result is not None
        assert result.type == MessageType.PROMPT_RESPONSE
        assert result.payload["response"] == "Prompt received"


class TestAgentDiscoveryHandler(ReflectiveModule):
    """Test AgentDiscoveryHandler"""
    
    def test_supported_types(self):
        """Test supported message types"""
        handler = AgentDiscoveryHandler("test_agent", ["python", "testing"])
        assert handler.get_supported_types() == [MessageType.AGENT_DISCOVERY]
    
    def test_validate_message(self):
        """Test message validation"""
        handler = AgentDiscoveryHandler("test_agent", ["python"])
        
        # Valid message
        caps = AgentCapabilities(agent_id="sender", capabilities=["java"])
        valid_msg = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="sender",
            payload={"agent_capabilities": caps.model_dump()}
        )
        handler.validate_message(valid_msg)  # Should not raise
        
        # Invalid message - missing capabilities
        invalid_msg = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="sender",
            payload={}
        )
        
        with pytest.raises(MessageValidationError):
            handler.validate_message(invalid_msg)
    
    @pytest.mark.asyncio
    async def test_handle_message(self):
        """Test discovery message handling"""
        callback_mock = Mock()
        handler = AgentDiscoveryHandler(
            "test_agent", 
            ["python", "testing"],
            discovery_callback=callback_mock
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
        
        result = await handler.handle_message(message)
        
        # Should generate response
        assert result is not None
        assert result.type == MessageType.AGENT_RESPONSE
        assert result.source == "test_agent"
        assert result.target == "sender_agent"
        assert result.correlation_id == message.id
        
        # Check our capabilities in response
        response_caps = AgentCapabilities(**result.payload["agent_capabilities"])
        assert response_caps.agent_id == "test_agent"
        assert response_caps.capabilities == ["python", "testing"]
        
        # Check callback was called
        callback_mock.assert_called_once()
        args = callback_mock.call_args[0]
        assert args[0] == "sender_agent"
        assert isinstance(args[1], AgentCapabilities)


class TestHelpWantedHandler(ReflectiveModule):
    """Test HelpWantedHandler"""
    
    def test_supported_types(self):
        """Test supported message types"""
        handler = HelpWantedHandler("test_agent", ["python"])
        assert handler.get_supported_types() == [MessageType.HELP_WANTED]
    
    def test_validate_message(self):
        """Test message validation"""
        handler = HelpWantedHandler("test_agent", ["python"])
        
        # Valid message
        valid_msg = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="sender",
            payload={
                "required_capabilities": ["python"],
                "description": "Need help with Python"
            }
        )
        handler.validate_message(valid_msg)  # Should not raise
        
        # Invalid - missing required_capabilities
        invalid_msg1 = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="sender",
            payload={"description": "Need help"}
        )
        
        with pytest.raises(MessageValidationError):
            handler.validate_message(invalid_msg1)
        
        # Invalid - missing description
        invalid_msg2 = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="sender",
            payload={"required_capabilities": ["python"]}
        )
        
        with pytest.raises(MessageValidationError):
            handler.validate_message(invalid_msg2)
    
    @pytest.mark.asyncio
    async def test_handle_message_can_help(self):
        """Test handling when we can help"""
        handler = HelpWantedHandler("test_agent", ["python", "testing", "docker"])
        
        message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="needy_agent",
            payload={
                "required_capabilities": ["python", "docker"],
                "description": "Need help with Python Docker setup"
            }
        )
        
        result = await handler.handle_message(message)
        
        assert result is not None
        assert result.type == MessageType.HELP_RESPONSE
        assert result.source == "test_agent"
        assert result.target == "needy_agent"
        assert result.payload["can_help"] is True
        assert result.payload["matching_capabilities"] == ["python", "docker"]
        assert result.payload["confidence_score"] == 1.0  # 2/2 capabilities match
    
    @pytest.mark.asyncio
    async def test_handle_message_cannot_help(self):
        """Test handling when we cannot help"""
        handler = HelpWantedHandler("test_agent", ["java", "spring"])
        
        message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="needy_agent",
            payload={
                "required_capabilities": ["python", "docker"],
                "description": "Need help with Python Docker setup"
            }
        )
        
        result = await handler.handle_message(message)
        
        assert result is None  # No response when we can't help
    
    @pytest.mark.asyncio
    async def test_handle_message_with_callback(self):
        """Test handling with custom callback"""
        callback_mock = Mock(return_value=True)
        handler = HelpWantedHandler(
            "test_agent", 
            ["java"],  # Don't have required capabilities
            help_callback=callback_mock
        )
        
        message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="needy_agent",
            payload={
                "required_capabilities": ["python"],
                "description": "Need Python help"
            }
        )
        
        result = await handler.handle_message(message)
        
        # Callback overrides capability check
        assert result is not None
        assert result.payload["can_help"] is True
        
        callback_mock.assert_called_once_with(
            "needy_agent", 
            ["python"], 
            "Need Python help"
        )


class TestSporeDeliveryHandler(ReflectiveModule):
    """Test SporeDeliveryHandler"""
    
    def test_supported_types(self):
        """Test supported message types"""
        handler = SporeDeliveryHandler("test_agent")
        assert handler.get_supported_types() == [MessageType.SPORE_DELIVERY]
    
    def test_validate_message(self):
        """Test message validation"""
        handler = SporeDeliveryHandler("test_agent")
        
        # Valid message
        valid_msg = BeastModeMessage(
            type=MessageType.SPORE_DELIVERY,
            source="sender",
            payload={
                "spore_name": "test_spore",
                "spore_content": "spore content here"
            }
        )
        handler.validate_message(valid_msg)  # Should not raise
        
        # Invalid - missing spore_name
        invalid_msg1 = BeastModeMessage(
            type=MessageType.SPORE_DELIVERY,
            source="sender",
            payload={"spore_content": "content"}
        )
        
        with pytest.raises(MessageValidationError):
            handler.validate_message(invalid_msg1)
        
        # Invalid - missing spore_content
        invalid_msg2 = BeastModeMessage(
            type=MessageType.SPORE_DELIVERY,
            source="sender",
            payload={"spore_name": "test"}
        )
        
        with pytest.raises(MessageValidationError):
            handler.validate_message(invalid_msg2)
    
    @pytest.mark.asyncio
    async def test_handle_message(self):
        """Test spore delivery handling"""
        callback_mock = Mock()
        handler = SporeDeliveryHandler("test_agent", spore_callback=callback_mock)
        
        message = BeastModeMessage(
            type=MessageType.SPORE_DELIVERY,
            source="spore_sender",
            payload={
                "spore_name": "optimization_spore",
                "spore_content": "def optimize(): pass",
                "metadata": {"version": "1.0", "author": "test"}
            }
        )
        
        result = await handler.handle_message(message)
        
        assert result is None  # Spore delivery doesn't generate response
        
        # Check callback was called with correct data
        callback_mock.assert_called_once()
        args = callback_mock.call_args
        assert args[0][0] == "spore_sender"  # source
        assert args[0][1] == "optimization_spore"  # spore_name
        
        spore_data = args[0][2]  # spore data
        assert spore_data["content"] == "def optimize(): pass"
        assert spore_data["metadata"] == {"version": "1.0", "author": "test"}
        assert "delivered_at" in spore_data


class TestSporeRequestHandler(ReflectiveModule):
    """Test SporeRequestHandler"""
    
    def test_supported_types(self):
        """Test supported message types"""
        handler = SporeRequestHandler("test_agent")
        assert handler.get_supported_types() == [MessageType.SPORE_REQUEST]
    
    @pytest.mark.asyncio
    async def test_handle_message_with_provider(self):
        """Test handling spore request with provider"""
        def spore_provider(spore_name):
            if spore_name == "test_spore":
                return {
                    "content": "def test(): pass",
                    "metadata": {"version": "1.0"}
                }
            return None
        
        handler = SporeRequestHandler("test_agent", spore_provider=spore_provider)
        
        message = BeastModeMessage(
            type=MessageType.SPORE_REQUEST,
            source="requester",
            payload={"spore_name": "test_spore"}
        )
        
        result = await handler.handle_message(message)
        
        assert result is not None
        assert result.type == MessageType.SPORE_DELIVERY
        assert result.source == "test_agent"
        assert result.target == "requester"
        assert result.payload["spore_name"] == "test_spore"
        assert result.payload["spore_content"] == "def test(): pass"
        assert result.payload["metadata"] == {"version": "1.0"}
    
    @pytest.mark.asyncio
    async def test_handle_message_spore_not_found(self):
        """Test handling when spore is not found"""
        def spore_provider(spore_name):
            return None  # Spore not found
        
        handler = SporeRequestHandler("test_agent", spore_provider=spore_provider)
        
        message = BeastModeMessage(
            type=MessageType.SPORE_REQUEST,
            source="requester",
            payload={"spore_name": "nonexistent_spore"}
        )
        
        result = await handler.handle_message(message)
        
        assert result is None  # No response when spore not found


class TestMessageRouter(ReflectiveModule):
    """Test MessageRouter"""
    
    def test_initialization(self):
        """Test router initialization"""
        router = MessageRouter("test_agent")
        
        assert router.agent_id == "test_agent"
        assert router.handlers == {}
        assert router.fallback_handlers == []
        assert router.stats['messages_routed'] == 0
    
    def test_register_handler(self):
        """Test handler registration"""
        router = MessageRouter("test_agent")
        handler = SimpleMessageHandler("test_agent")
        
        router.register_handler(handler)
        
        assert MessageType.SIMPLE_MESSAGE in router.handlers
        assert handler in router.handlers[MessageType.SIMPLE_MESSAGE]
    
    def test_register_fallback_handler(self):
        """Test fallback handler registration"""
        router = MessageRouter("test_agent")
        handler = SimpleMessageHandler("test_agent")
        
        router.register_fallback_handler(handler)
        
        assert handler in router.fallback_handlers
    
    @pytest.mark.asyncio
    async def test_route_message_success(self):
        """Test successful message routing"""
        router = MessageRouter("test_agent")
        handler = SimpleMessageHandler("test_agent")
        router.register_handler(handler)
        
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="sender",
            payload={"content": "Hello"}
        )
        
        responses = await router.route_message(message)
        
        assert len(responses) == 0  # Simple message doesn't generate response
        assert router.stats['messages_routed'] == 1
        assert router.stats['messages_handled'] == 1
        assert handler.handled_count == 1
    
    @pytest.mark.asyncio
    async def test_route_message_with_response(self):
        """Test routing message that generates response"""
        router = MessageRouter("test_agent")
        handler = PromptRequestHandler("test_agent")
        router.register_handler(handler)
        
        message = BeastModeMessage(
            type=MessageType.PROMPT_REQUEST,
            source="sender",
            payload={"prompt": "Test prompt"}
        )
        
        responses = await router.route_message(message)
        
        assert len(responses) == 1
        assert responses[0].type == MessageType.PROMPT_RESPONSE
        assert responses[0].target == "sender"
    
    @pytest.mark.asyncio
    async def test_route_message_skip_self(self):
        """Test that messages from self are skipped"""
        router = MessageRouter("test_agent")
        handler = SimpleMessageHandler("test_agent")
        router.register_handler(handler)
        
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="test_agent",  # Same as router agent_id
            payload={"content": "Hello"}
        )
        
        responses = await router.route_message(message)
        
        assert len(responses) == 0
        assert router.stats['messages_routed'] == 1
        assert router.stats['messages_handled'] == 0  # Should be 0 because message was skipped
        assert handler.handled_count == 0
    
    @pytest.mark.asyncio
    async def test_route_message_targeted(self):
        """Test routing targeted messages"""
        router = MessageRouter("test_agent")
        handler = SimpleMessageHandler("test_agent")
        router.register_handler(handler)
        
        # Message targeted to us
        our_message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="sender",
            target="test_agent",
            payload={"content": "Hello"}
        )
        
        responses = await router.route_message(our_message)
        assert len(responses) == 0
        assert handler.handled_count == 1
        
        # Message targeted to someone else
        other_message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="sender",
            target="other_agent",
            payload={"content": "Hello"}
        )
        
        responses = await router.route_message(other_message)
        assert len(responses) == 0
        assert handler.handled_count == 1  # Should still be 1, not incremented
    
    @pytest.mark.asyncio
    async def test_route_message_no_handler(self):
        """Test routing message with no handler"""
        router = MessageRouter("test_agent")
        
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="sender",
            payload={"content": "Hello"}
        )
        
        responses = await router.route_message(message)
        
        assert len(responses) == 0
        assert router.stats['messages_routed'] == 1
        assert router.stats['messages_handled'] == 0
    
    @pytest.mark.asyncio
    async def test_route_message_fallback_handler(self):
        """Test routing with fallback handler"""
        router = MessageRouter("test_agent")
        fallback_handler = SimpleMessageHandler("test_agent")
        router.register_fallback_handler(fallback_handler)
        
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="sender",
            payload={"content": "Hello"}
        )
        
        responses = await router.route_message(message)
        
        assert len(responses) == 0
        assert router.stats['messages_routed'] == 1
        assert router.stats['messages_handled'] == 1
        assert fallback_handler.handled_count == 1
    
    def test_convert_legacy_message(self):
        """Test legacy message conversion"""
        router = MessageRouter("test_agent")
        router.auto_convert_legacy = True
        
        # Legacy message format
        legacy_data = {
            "type": "message",  # Old type name
            "from": "sender",   # Old field name
            "content": "Hello world"
        }
        
        # This should work through the conversion process
        converted = router._convert_legacy_message({
            "type": "message",
            "source": "sender",
            "payload": {"content": "Hello"}
        })
        
        assert isinstance(converted, BeastModeMessage)
        assert converted.type == MessageType.SIMPLE_MESSAGE
        assert converted.source == "sender"
    
    @pytest.mark.asyncio
    async def test_route_dict_message(self):
        """Test routing dictionary message"""
        router = MessageRouter("test_agent")
        handler = SimpleMessageHandler("test_agent")
        router.register_handler(handler)
        
        message_dict = {
            "type": "simple_message",
            "source": "sender",
            "payload": {"content": "Hello"}
        }
        
        responses = await router.route_message(message_dict)
        
        assert len(responses) == 0
        assert router.stats['messages_routed'] == 1
        assert router.stats['messages_handled'] == 1
    
    def test_get_supported_types(self):
        """Test getting supported types"""
        router = MessageRouter("test_agent")
        
        simple_handler = SimpleMessageHandler("test_agent")
        prompt_handler = PromptRequestHandler("test_agent")
        
        router.register_handler(simple_handler)
        router.register_handler(prompt_handler)
        
        supported = router.get_supported_types()
        
        assert MessageType.SIMPLE_MESSAGE in supported
        assert MessageType.PROMPT_REQUEST in supported
        assert len(supported) == 2
    
    def test_validate_message_format(self):
        """Test message format validation"""
        router = MessageRouter("test_agent")
        
        # Valid message
        valid_data = {
            "type": "simple_message",
            "source": "sender",
            "payload": {"content": "Hello"}
        }
        
        assert router.validate_message_format(valid_data) is True
        
        # Invalid message
        invalid_data = {
            "type": "simple_message"
            # Missing source
        }
        
        assert router.validate_message_format(invalid_data) is False
    
    def test_get_handler_stats(self):
        """Test getting handler statistics"""
        router = MessageRouter("test_agent")
        handler = SimpleMessageHandler("test_agent")
        router.register_handler(handler)
        
        stats = router.get_handler_stats()
        
        assert "router_stats" in stats
        assert "handler_stats" in stats
        assert "supported_types" in stats

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

        assert MessageType.SIMPLE_MESSAGE.value in stats["handler_stats"]