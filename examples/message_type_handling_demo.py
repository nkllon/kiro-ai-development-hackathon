#!/usr/bin/env python3
"""
Beast Mode Message Type Handling Demo

Demonstrates the standardized message type handling system with all MessageType enum values.
Shows routing, validation, compatibility layers, and error handling.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from src.beast_mode.messaging.models import BeastModeMessage, MessageType, AgentCapabilities
from src.beast_mode.messaging.message_router import StandardMessageRouter, MessageTypeRegistry
from src.beast_mode.messaging.bus_client import BeastModeBusClient


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MessageTypeDemo:
    """Demonstrates all message type handling capabilities"""
    
    def __init__(self):
        self.agent_id = "demo_agent"
        self.capabilities = ["python", "testing", "demo", "message_handling"]
        
        # Create message router with callbacks
        self.router = StandardMessageRouter(
            agent_id=self.agent_id,
            capabilities=self.capabilities,
            callbacks=self._create_callbacks()
        )
        
        # Message type registry for validation
        self.registry = MessageTypeRegistry()
        
        # Statistics
        self.processed_messages = []
        self.generated_responses = []
    
    def _create_callbacks(self) -> Dict[str, Any]:
        """Create callback functions for all message types"""
        return {
            'on_simple_message': self._handle_simple_message,
            'on_prompt_request': self._handle_prompt_request,
            'on_prompt_response': self._handle_prompt_response,
            'on_agent_discovery': self._handle_agent_discovery,
            'on_agent_response': self._handle_agent_response,
            'on_help_wanted': self._handle_help_wanted,
            'on_help_response': self._handle_help_response,
            'on_spore_delivery': self._handle_spore_delivery,
            'on_spore_request': self._handle_spore_request,
            'on_technical_exchange': self._handle_technical_exchange,
            'on_system_health': self._handle_system_health
        }
    
    # Callback implementations
    
    def _handle_simple_message(self, source: str, content: str) -> None:
        """Handle simple message"""
        logger.info(f"📝 Simple message from {source}: {content}")
    
    def _handle_prompt_request(self, prompt: str) -> str:
        """Handle prompt request"""
        logger.info(f"🤔 Processing prompt: {prompt}")
        return f"Demo response to: {prompt}"
    
    def _handle_prompt_response(self, source: str, response: str, original_prompt: str) -> None:
        """Handle prompt response"""
        logger.info(f"💡 Received response from {source}: {response}")
    
    def _handle_agent_discovery(self, source: str, capabilities: AgentCapabilities) -> None:
        """Handle agent discovery"""
        logger.info(f"🔍 Discovered agent {source} with capabilities: {capabilities.capabilities}")
    
    def _handle_agent_response(self, source: str, capabilities: AgentCapabilities) -> None:
        """Handle agent response"""
        logger.info(f"👋 Agent {source} responded with capabilities: {capabilities.capabilities}")
    
    def _handle_help_wanted(self, source: str, required_capabilities: list, description: str) -> bool:
        """Handle help wanted request"""
        logger.info(f"🆘 Help request from {source}: {description}")
        logger.info(f"   Required capabilities: {required_capabilities}")
        
        # Check if we can help
        can_help = any(cap in self.capabilities for cap in required_capabilities)
        logger.info(f"   Can help: {can_help}")
        return can_help
    
    def _handle_help_response(self, source: str, response_data: Dict[str, Any]) -> None:
        """Handle help response"""
        can_help = response_data.get('can_help', False)
        confidence = response_data.get('confidence_score', 0.0)
        logger.info(f"🤝 Help response from {source}: can_help={can_help}, confidence={confidence:.2f}")
    
    def _handle_spore_delivery(self, source: str, spore_name: str, spore_data: Dict[str, Any]) -> None:
        """Handle spore delivery"""
        logger.info(f"🧬 Received spore '{spore_name}' from {source}")
        logger.info(f"   Content length: {len(spore_data.get('content', ''))}")
        logger.info(f"   Metadata: {spore_data.get('metadata', {})}")
    
    def _handle_spore_request(self, spore_name: str) -> Dict[str, Any]:
        """Handle spore request"""
        logger.info(f"📦 Spore request for: {spore_name}")
        
        # Demo spore repository
        spores = {
            "demo_spore": {
                "content": "def demo_function(): return 'Hello from spore!'",
                "metadata": {"version": "1.0", "author": "demo_agent"}
            },
            "optimization_spore": {
                "content": "def optimize(data): return sorted(data)",
                "metadata": {"version": "2.1", "author": "optimization_expert"}
            }
        }
        
        return spores.get(spore_name)
    
    def _handle_technical_exchange(self, source: str, data: Dict[str, Any]) -> None:
        """Handle technical exchange"""
        topic = data.get('topic', 'unknown')
        logger.info(f"🔧 Technical exchange from {source} on topic: {topic}")
    
    def _handle_system_health(self, source: str, data: Dict[str, Any]) -> None:
        """Handle system health"""
        status = data.get('status', 'unknown')
        logger.info(f"💚 Health update from {source}: {status}")
    
    async def demonstrate_all_message_types(self):
        """Demonstrate handling of all message types"""
        logger.info("🚀 Starting message type handling demonstration")
        logger.info("=" * 60)
        
        # Test each message type
        await self._demo_simple_message()
        await self._demo_prompt_request_response()
        await self._demo_agent_discovery()
        await self._demo_help_system()
        await self._demo_spore_system()
        await self._demo_technical_exchange()
        await self._demo_system_health()
        
        # Demonstrate validation and compatibility
        await self._demo_validation_and_compatibility()
        
        # Show statistics
        self._show_statistics()
        
        logger.info("=" * 60)
        logger.info("✅ Message type handling demonstration complete")
    
    async def _demo_simple_message(self):
        """Demo simple message handling"""
        logger.info("\n📝 SIMPLE MESSAGE DEMO")
        logger.info("-" * 30)
        
        message = self.router.create_test_message(
            MessageType.SIMPLE_MESSAGE,
            content="Hello from the message type demo!",
            context="demonstration"
        )
        
        responses = await self.router.process_message(message)
        self.processed_messages.append(message)
        self.generated_responses.extend(responses)
    
    async def _demo_prompt_request_response(self):
        """Demo prompt request/response handling"""
        logger.info("\n🤔 PROMPT REQUEST/RESPONSE DEMO")
        logger.info("-" * 35)
        
        # Create and process prompt request
        request = self.router.create_test_message(
            MessageType.PROMPT_REQUEST,
            prompt="What is the best way to handle message routing?",
            context="architecture_question"
        )
        
        responses = await self.router.process_message(request)
        self.processed_messages.append(request)
        self.generated_responses.extend(responses)
        
        # Process the response
        if responses:
            response = responses[0]
            logger.info(f"Generated response: {response.payload.get('response', 'No response')}")
            
            # Simulate receiving the response
            await self.router.process_message(response)
    
    async def _demo_agent_discovery(self):
        """Demo agent discovery handling"""
        logger.info("\n🔍 AGENT DISCOVERY DEMO")
        logger.info("-" * 25)
        
        # Create discovery message from another agent
        other_agent_caps = AgentCapabilities(
            agent_id="other_demo_agent",
            capabilities=["java", "spring", "microservices"],
            availability="ready_for_business"
        )
        
        discovery = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="other_demo_agent",
            payload={
                "agent_capabilities": other_agent_caps.model_dump(),
                "announcement": "New agent joining the network"
            }
        )
        
        responses = await self.router.process_message(discovery)
        self.processed_messages.append(discovery)
        self.generated_responses.extend(responses)
        
        # Process our response
        if responses:
            our_response = responses[0]
            logger.info(f"Our capabilities: {our_response.payload['agent_capabilities']['capabilities']}")
    
    async def _demo_help_system(self):
        """Demo help system handling"""
        logger.info("\n🆘 HELP SYSTEM DEMO")
        logger.info("-" * 20)
        
        # Create help request
        help_request = self.router.create_test_message(
            MessageType.HELP_WANTED,
            required_capabilities=["python", "testing"],
            description="Need help writing comprehensive unit tests"
        )
        
        responses = await self.router.process_message(help_request)
        self.processed_messages.append(help_request)
        self.generated_responses.extend(responses)
        
        # Create help request we can't fulfill
        impossible_request = self.router.create_test_message(
            MessageType.HELP_WANTED,
            required_capabilities=["rust", "blockchain"],
            description="Need help with Rust blockchain development"
        )
        
        responses2 = await self.router.process_message(impossible_request)
        self.processed_messages.append(impossible_request)
        logger.info(f"Responses to impossible request: {len(responses2)} (should be 0)")
    
    async def _demo_spore_system(self):
        """Demo spore system handling"""
        logger.info("\n🧬 SPORE SYSTEM DEMO")
        logger.info("-" * 20)
        
        # Request a spore
        spore_request = self.router.create_test_message(
            MessageType.SPORE_REQUEST,
            spore_name="demo_spore"
        )
        
        responses = await self.router.process_message(spore_request)
        self.processed_messages.append(spore_request)
        self.generated_responses.extend(responses)
        
        # Deliver a spore
        spore_delivery = self.router.create_test_message(
            MessageType.SPORE_DELIVERY,
            spore_name="optimization_methodology",
            spore_content="def systematic_optimize(data): return optimized_data"
        )
        
        await self.router.process_message(spore_delivery)
        self.processed_messages.append(spore_delivery)
    
    async def _demo_technical_exchange(self):
        """Demo technical exchange handling"""
        logger.info("\n🔧 TECHNICAL EXCHANGE DEMO")
        logger.info("-" * 28)
        
        tech_message = self.router.create_test_message(
            MessageType.TECHNICAL_EXCHANGE,
            payload={
                "topic": "kubernetes_deployment",
                "data": {
                    "cluster_version": "1.21",
                    "namespace": "production",
                    "replicas": 3
                }
            }
        )
        
        await self.router.process_message(tech_message)
        self.processed_messages.append(tech_message)
    
    async def _demo_system_health(self):
        """Demo system health handling"""
        logger.info("\n💚 SYSTEM HEALTH DEMO")
        logger.info("-" * 22)
        
        health_message = self.router.create_test_message(
            MessageType.SYSTEM_HEALTH,
            payload={
                "status": "healthy",
                "metrics": {
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "message_throughput": 150
                }
            }
        )
        
        await self.router.process_message(health_message)
        self.processed_messages.append(health_message)
    
    async def _demo_validation_and_compatibility(self):
        """Demo message validation and compatibility features"""
        logger.info("\n✅ VALIDATION & COMPATIBILITY DEMO")
        logger.info("-" * 35)
        
        # Test valid message
        valid_data = {
            "type": "simple_message",
            "source": "test_agent",
            "payload": {"content": "Valid message"}
        }
        
        validation_result = self.router.validate_message_compatibility(valid_data)
        logger.info(f"Valid message validation: {validation_result['is_valid']}")
        
        # Test invalid message
        invalid_data = {
            "type": "prompt_request",
            "source": "test_agent"
            # Missing required 'prompt' field
        }
        
        validation_result = self.router.validate_message_compatibility(invalid_data)
        logger.info(f"Invalid message validation: {validation_result['is_valid']}")
        logger.info(f"Validation errors: {validation_result['errors']}")
        
        # Test legacy message format
        legacy_data = {
            "type": "message",  # Old type name
            "source": "legacy_agent",
            "payload": {"content": "Legacy format message"}
        }
        
        validation_result = self.router.validate_message_compatibility(legacy_data)
        logger.info(f"Legacy message validation: {validation_result['is_valid']}")
        logger.info(f"Is legacy format: {validation_result['is_legacy']}")
        
        # Test payload validation for all types
        logger.info("\nPayload validation for all message types:")
        for msg_type in MessageType:
            type_info = self.registry.get_type_info(msg_type)
            logger.info(f"  {msg_type.value}: {len(type_info.get('required_fields', []))} required fields")
    
    def _show_statistics(self):
        """Show processing statistics"""
        logger.info("\n📊 PROCESSING STATISTICS")
        logger.info("-" * 25)
        
        logger.info(f"Messages processed: {len(self.processed_messages)}")
        logger.info(f"Responses generated: {len(self.generated_responses)}")
        
        # Message type breakdown
        type_counts = {}
        for msg in self.processed_messages:
            msg_type = msg.type.value
            type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
        
        logger.info("\nMessage type breakdown:")
        for msg_type, count in type_counts.items():
            logger.info(f"  {msg_type}: {count}")
        
        # Router statistics
        router_stats = self.router.get_handler_stats()
        logger.info(f"\nRouter statistics:")
        logger.info(f"  Messages routed: {router_stats['router_stats']['messages_routed']}")
        logger.info(f"  Messages handled: {router_stats['router_stats']['messages_handled']}")
        logger.info(f"  Validation errors: {router_stats['router_stats']['validation_errors']}")
        logger.info(f"  Handler errors: {router_stats['router_stats']['handler_errors']}")
        
        # Handler info
        handler_info = self.router.get_handler_info()
        logger.info(f"  Total handlers: {handler_info['total_handlers']}")
        logger.info(f"  Supported types: {len(handler_info['handlers_by_type'])}")


async def demonstrate_bus_client_integration():
    """Demonstrate integration with BeastModeBusClient"""
    logger.info("\n🚌 BUS CLIENT INTEGRATION DEMO")
    logger.info("-" * 32)
    
    # Create bus client (will use mock Redis for demo)
    client = BeastModeBusClient(
        redis_url="redis://localhost:6379",
        agent_id="bus_demo_agent",
        capabilities=["python", "redis", "messaging"]
    )
    
    # Set up message callbacks
    client.set_message_callback('on_simple_message', 
        lambda source, content: logger.info(f"Bus client received: {content} from {source}"))
    
    # Create test messages
    test_messages = [
        client.create_test_message(MessageType.SIMPLE_MESSAGE, content="Hello from bus client"),
        client.create_test_message(MessageType.PROMPT_REQUEST, prompt="Test prompt"),
        client.create_test_message(MessageType.AGENT_DISCOVERY)
    ]
    
    # Validate messages
    for i, msg in enumerate(test_messages):
        validation = client.validate_message_format(msg.model_dump())
        logger.info(f"Test message {i+1} validation: {validation['is_valid']}")
    
    # Show router info
    router_info = client.get_message_router_info()
    if "error" not in router_info:
        logger.info(f"Bus client router has {router_info['total_handlers']} handlers")
    else:
        logger.info("Bus client router not initialized (Redis not available)")


async def main():
    """Main demonstration function"""
    logger.info("🎯 Beast Mode Message Type Handling System Demo")
    logger.info("=" * 60)
    
    # Create and run the demo
    demo = MessageTypeDemo()
    await demo.demonstrate_all_message_types()
    
    # Demonstrate bus client integration
    await demonstrate_bus_client_integration()
    
    logger.info("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())