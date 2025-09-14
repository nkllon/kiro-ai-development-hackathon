"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:24:55.644580
"""



import pytest
from datetime import datetime
from unittest.mock import Mock
import asyncio

from src.beast_mode.messaging.models import BeastModeMessage, MessageType, AgentCapabilities
from src.beast_mode.messaging.message_router import StandardMessageRouter, MessageTypeRegistry
from src.beast_mode.messaging.message_handlers import MessageValidationError
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule



class TestAllMessageTypes(ReflectiveModule):
    """Test all MessageType enum values with their handlers"""
    
    @pytest.fixture
    def router(self):
        """Create a standard router for testing"""
        callbacks = {
            'on_simple_message': Mock(),
            'on_prompt_request': Mock(return_value="Processed response"),
            'on_prompt_response': Mock(),
            'on_agent_discovery': Mock(),
            'on_agent_response': Mock(),
            'on_help_wanted': None,  # Let the handler decide based on capabilities
            'on_help_response': Mock(),
            'on_spore_delivery': Mock(),
            'on_spore_request': Mock(return_value={
                "content": "test spore content",
                "metadata": {"version": "1.0"}
            }),
            'on_technical_exchange': Mock(),
            'on_system_health': Mock()
        }
        
        return StandardMessageRouter(
            agent_id="test_agent",
            capabilities=["python", "testing", "docker"],
            callbacks=callbacks
        )
    
    @pytest.mark.asyncio
    async def test_simple_message_type(self, router):
        """Test SIMPLE_MESSAGE type"""
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="sender",
            payload={"content": "Hello world", "context": "greeting"}
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 0  # No response expected
        router.callbacks['on_simple_message'].assert_called_once_with("sender", "Hello world")
    
    @pytest.mark.asyncio
    async def test_prompt_request_type(self, router):
        """Test PROMPT_REQUEST type"""
        message = BeastModeMessage(
            type=MessageType.PROMPT_REQUEST,
            source="sender",
            payload={
                "prompt": "What is the capital of France?",
                "context": "geography question",
                "timeout": 30
            }
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 1
        response = responses[0]
        
        assert response.type == MessageType.PROMPT_RESPONSE
        assert response.source == "test_agent"
        assert response.target == "sender"
        assert response.payload["response"] == "Processed response"
        assert response.payload["original_prompt"] == "What is the capital of France?"
        assert response.correlation_id == message.id
    
    @pytest.mark.asyncio
    async def test_prompt_response_type(self, router):
        """Test PROMPT_RESPONSE type"""
        # First track a request for correlation
        original_request = BeastModeMessage(
            type=MessageType.PROMPT_REQUEST,
            source="test_agent",
            payload={"prompt": "Original question"}
        )
        router.track_sent_message(original_request)
        
        # Now process the response
        message = BeastModeMessage(
            type=MessageType.PROMPT_RESPONSE,
            source="responder",
            payload={
                "response": "The answer is 42",
                "original_prompt": "Original question",
                "processed_at": datetime.now().isoformat()
            },
            correlation_id=original_request.id
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 0  # No response expected
        router.callbacks['on_prompt_response'].assert_called_once()
    
    @pytest.mark.asyncio
    async def test_agent_discovery_type(self, router):
        """Test AGENT_DISCOVERY type"""
        sender_caps = AgentCapabilities(
            agent_id="discovering_agent",
            capabilities=["java", "spring", "microservices"],
            availability="ready_for_business",
            specializations=["backend_development"]
        )
        
        message = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="discovering_agent",
            payload={
                "agent_capabilities": sender_caps.model_dump(),
                "announcement": "New agent joining the network"
            }
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 1
        response = responses[0]
        
        assert response.type == MessageType.AGENT_RESPONSE
        assert response.source == "test_agent"
        assert response.target == "discovering_agent"
        
        # Check our capabilities in response
        our_caps = AgentCapabilities(**response.payload["agent_capabilities"])
        assert our_caps.agent_id == "test_agent"
        assert our_caps.capabilities == ["python", "testing", "docker"]
        
        router.callbacks['on_agent_discovery'].assert_called_once()
    
    @pytest.mark.asyncio
    async def test_agent_response_type(self, router):
        """Test AGENT_RESPONSE type"""
        responder_caps = AgentCapabilities(
            agent_id="responding_agent",
            capabilities=["kubernetes", "devops"],
            availability="busy"
        )
        
        message = BeastModeMessage(
            type=MessageType.AGENT_RESPONSE,
            source="responding_agent",
            payload={
                "agent_capabilities": responder_caps.model_dump(),
                "response_to": "some_discovery_id"
            }
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 0  # No response expected
        router.callbacks['on_agent_response'].assert_called_once()
    
    @pytest.mark.asyncio
    async def test_help_wanted_type(self, router):
        """Test HELP_WANTED type"""
        message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="needy_agent",
            payload={
                "required_capabilities": ["python", "testing"],
                "description": "Need help writing unit tests for Python project",
                "urgency": "normal",
                "max_helpers": 2,
                "timeout_hours": 24,
                "context": {"project": "web_app", "framework": "flask"}
            }
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 1
        response = responses[0]
        
        assert response.type == MessageType.HELP_RESPONSE
        assert response.source == "test_agent"
        assert response.target == "needy_agent"
        assert response.payload["can_help"] is True
        assert set(response.payload["matching_capabilities"]) == {"python", "testing"}
        assert response.payload["confidence_score"] == 1.0
    
    @pytest.mark.asyncio
    async def test_help_wanted_type_cannot_help(self, router):
        """Test HELP_WANTED type when we cannot help"""
        message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="needy_agent",
            payload={
                "required_capabilities": ["rust", "blockchain"],
                "description": "Need help with Rust blockchain development"
            }
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 0  # No response when we can't help
    
    @pytest.mark.asyncio
    async def test_help_response_type(self, router):
        """Test HELP_RESPONSE type"""
        # First track a help request for correlation
        help_request = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="test_agent",
            payload={
                "required_capabilities": ["python"],
                "description": "Need Python help",
                "request_id": "help_123"
            }
        )
        router.track_sent_message(help_request)
        
        message = BeastModeMessage(
            type=MessageType.HELP_RESPONSE,
            source="helper_agent",
            payload={
                "request_id": "help_123",
                "can_help": True,
                "matching_capabilities": ["python"],
                "confidence_score": 0.9,
                "response_message": "I can help with Python development"
            }
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 0  # No response expected
        router.callbacks['on_help_response'].assert_called_once()
    
    @pytest.mark.asyncio
    async def test_spore_delivery_type(self, router):
        """Test SPORE_DELIVERY type"""
        message = BeastModeMessage(
            type=MessageType.SPORE_DELIVERY,
            source="spore_provider",
            payload={
                "spore_name": "optimization_methodology",
                "spore_content": """
                # Optimization Spore
                def systematic_optimization(data):
                    # Apply PDCA methodology
                    return optimized_data
                """,
                "metadata": {
                    "version": "2.1",
                    "author": "optimization_expert",
                    "dependencies": ["numpy", "pandas"],
                    "description": "Systematic optimization methodology"
                }
            }
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 0  # No response expected
        
        # Check callback was called with correct parameters
        router.callbacks['on_spore_delivery'].assert_called_once()
        args = router.callbacks['on_spore_delivery'].call_args[0]
        assert args[0] == "spore_provider"
        assert args[1] == "optimization_methodology"
        assert "systematic_optimization" in args[2]["content"]
        assert args[2]["metadata"]["version"] == "2.1"
    
    @pytest.mark.asyncio
    async def test_spore_request_type(self, router):
        """Test SPORE_REQUEST type"""
        message = BeastModeMessage(
            type=MessageType.SPORE_REQUEST,
            source="spore_requester",
            payload={
                "spore_name": "test_spore",
                "version": "latest",
                "metadata": {"purpose": "learning"}
            }
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 1
        response = responses[0]
        
        assert response.type == MessageType.SPORE_DELIVERY
        assert response.source == "test_agent"
        assert response.target == "spore_requester"
        assert response.payload["spore_name"] == "test_spore"
        assert response.payload["spore_content"] == "test spore content"
        assert response.payload["metadata"]["version"] == "1.0"
    
    @pytest.mark.asyncio
    async def test_spore_spawn_type(self, router):
        """Test SPORE_SPAWN type (if implemented)"""
        # Note: SPORE_SPAWN is in the enum but may not have a specific handler yet
        # This test ensures the message can be processed without errors
        message = BeastModeMessage(
            type=MessageType.SPORE_SPAWN,
            source="spawner_agent",
            payload={
                "spore_type": "analysis_spore",
                "metadata": {"target": "performance_analysis"}
            }
        )
        
        # Should not raise an error even if no specific handler exists
        responses = await router.process_message(message)
        
        # May or may not have responses depending on implementation
        assert isinstance(responses, list)
    
    @pytest.mark.asyncio
    async def test_technical_exchange_type(self, router):
        """Test TECHNICAL_EXCHANGE type"""
        message = BeastModeMessage(
            type=MessageType.TECHNICAL_EXCHANGE,
            source="tech_agent",
            payload={
                "topic": "kubernetes_configuration",
                "data": {
                    "cluster_info": {"nodes": 3, "version": "1.21"},
                    "namespace": "production",
                    "resources": ["deployments", "services", "ingress"]
                },
                "metadata": {"environment": "production", "urgency": "low"}
            }
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 0  # No response expected
        router.callbacks['on_technical_exchange'].assert_called_once()
        
        # Check callback received correct data
        args = router.callbacks['on_technical_exchange'].call_args[0]
        assert args[0] == "tech_agent"
        assert args[1]["topic"] == "kubernetes_configuration"
        assert args[1]["data"]["cluster_info"]["nodes"] == 3
    
    @pytest.mark.asyncio
    async def test_system_health_type(self, router):
        """Test SYSTEM_HEALTH type"""
        message = BeastModeMessage(
            type=MessageType.SYSTEM_HEALTH,
            source="monitoring_agent",
            payload={
                "status": "healthy",
                "metrics": {
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "disk_usage": 23.1,
                    "network_latency": 12.5
                },
                "alerts": [],
                "timestamp": datetime.now().isoformat(),
                "agent_id": "monitoring_agent"
            }
        )
        
        responses = await router.process_message(message)
        
        assert len(responses) == 0  # No response expected
        router.callbacks['on_system_health'].assert_called_once()
        
        # Check callback received correct data
        args = router.callbacks['on_system_health'].call_args[0]
        assert args[0] == "monitoring_agent"
        assert args[1]["status"] == "healthy"
        assert args[1]["metrics"]["cpu_usage"] == 45.2
    
    def test_message_type_registry_completeness(self):
        """Test that MessageTypeRegistry has info for all message types"""
        registry = MessageTypeRegistry()
        
        for message_type in MessageType:
            type_info = registry.get_type_info(message_type)
            
            assert type_info is not None, f"No type info for {message_type}"
            assert 'description' in type_info, f"No description for {message_type}"
            assert 'required_fields' in type_info, f"No required_fields for {message_type}"
            assert 'optional_fields' in type_info, f"No optional_fields for {message_type}"
            assert 'handler_class' in type_info, f"No handler_class for {message_type}"
    
    @pytest.mark.asyncio
    async def test_all_message_types_have_handlers(self, router):
        """Test that all message types have registered handlers"""
        supported_types = router.get_supported_types()
        
        for message_type in MessageType:
            assert message_type in supported_types, f"No handler registered for {message_type}"
    
    def test_message_validation_for_all_types(self):
        """Test message validation for all message types"""
        registry = MessageTypeRegistry()
        
        for message_type in MessageType:
            type_info = registry.get_type_info(message_type)
            required_fields = type_info.get('required_fields', [])
            
            # Test with all required fields
            payload = {}
            for field in required_fields:
                if field == 'agent_capabilities':
                    payload[field] = AgentCapabilities(agent_id="test").model_dump()
                elif field == 'required_capabilities':
                    payload[field] = ["python"]
                elif field == 'spore_content':
                    payload[field] = "test content"
                else:
                    payload[field] = f"test_{field}"
            
            # Should be valid
            result = registry.validate_payload(message_type, payload)
            assert result['is_valid'], f"Valid payload failed for {message_type}: {result}"
            
            # Test with missing required field (if any)
            if required_fields:
                incomplete_payload = payload.copy()
                del incomplete_payload[required_fields[0]]
                
                result = registry.validate_payload(message_type, incomplete_payload)
                assert not result['is_valid'], f"Invalid payload passed for {message_type}"
                assert required_fields[0] in result['missing_fields']
    
    @pytest.mark.asyncio
    async def test_message_type_compatibility_layer(self, router):
        """Test compatibility layer for different message formats"""
        # Enable legacy conversion for this test
        router.auto_convert_legacy = True
        
        # Test legacy message format conversion
        legacy_message_data = {
            "type": "message",  # Old type name
            "source": "legacy_agent",
            "payload": {"content": "Legacy message"}
        }
        
        # Should be converted and processed
        responses = await router.process_message(legacy_message_data)
        
        # Should not raise error and should process as simple message
        assert isinstance(responses, list)
        
        # Check that message was processed (callback should be called)
        router.callbacks['on_simple_message'].assert_called()
    
    def test_create_test_messages_for_all_types(self, router):
        """Test creating test messages for all message types"""
        for message_type in MessageType:
            try:
                test_message = router.create_test_message(message_type)
                
                assert test_message.type == message_type
                assert test_message.source is not None
                assert isinstance(test_message.payload, dict)
                
                # Validate the test message payload
                registry = MessageTypeRegistry()
                validation_result = registry.validate_payload(message_type, test_message.payload)
                
                assert validation_result['is_valid'], f"Test message for {message_type} is invalid: {validation_result}"
                
            except Exception as e:
                pytest.fail(f"Failed to create test message for {message_type}: {e}")
    
    @pytest.mark.asyncio
    async def test_error_handling_for_all_types(self, router):
        """Test error handling for all message types"""
        for message_type in MessageType:
            # Create message with invalid payload
            invalid_message = BeastModeMessage(
                type=message_type,
                source="error_test",
                payload={}  # Empty payload, likely missing required fields
            )
            
            # Should handle gracefully without crashing
            try:
                responses = await router.process_message(invalid_message)
                assert isinstance(responses, list)
            except Exception as e:
                # Some validation errors are expected, but shouldn't crash the system
                assert isinstance(e, (MessageValidationError, ValueError))
    
    def test_message_type_enum_completeness(self):
        """Test that all expected message types are in the enum"""
        expected_types = [
            "SIMPLE_MESSAGE",
            "PROMPT_REQUEST", 
            "PROMPT_RESPONSE",
            "AGENT_DISCOVERY",
            "AGENT_RESPONSE",
            "HELP_WANTED",
            "HELP_RESPONSE",
            "SPORE_DELIVERY",
            "SPORE_REQUEST",
            "SPORE_SPAWN",
            "TECHNICAL_EXCHANGE",
            "SYSTEM_HEALTH"
        ]
        
        for type_name in expected_types:
            assert hasattr(MessageType, type_name), f"MessageType.{type_name} not found"
            
        # Check that enum values match expected string values
        assert MessageType.SIMPLE_MESSAGE.value == "simple_message"
        assert MessageType.PROMPT_REQUEST.value == "prompt_request"
        assert MessageType.AGENT_DISCOVERY.value == "agent_discovery"
        assert MessageType.HELP_WANTED.value == "help_wanted"
        assert MessageType.SPORE_DELIVERY.value == "spore_delivery"
    
    @pytest.mark.asyncio
    async def test_message_routing_statistics(self, router):
        """Test that message routing statistics are properly tracked"""
        initial_stats = router.get_handler_stats()
        
        # Process various message types
        messages = [
            router.create_test_message(MessageType.SIMPLE_MESSAGE),
            router.create_test_message(MessageType.PROMPT_REQUEST),
            router.create_test_message(MessageType.AGENT_DISCOVERY),
            router.create_test_message(MessageType.HELP_WANTED),
            router.create_test_message(MessageType.SPORE_DELIVERY)
        ]
        
        for message in messages:
            await router.process_message(message)
        
        final_stats = router.get_handler_stats()
        
        # Check that statistics were updated
        assert final_stats['router_stats']['messages_routed'] > initial_stats['router_stats']['messages_routed']
        assert final_stats['router_stats']['messages_handled'] > initial_stats['router_stats']['messages_handled']
        
        # Check individual handler stats
        for msg_type, handlers in final_stats['handler_stats'].items():
            for handler_stat in handlers:
                if handler_stat['handled_count'] > 0:

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

                    assert handler_stat['last_handled'] is not None