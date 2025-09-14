"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:20:55.302704
"""


import asyncio
import json
import pytest
import redis.asyncio as redis
from datetime import datetime, timedelta
from typing import List
import uuid

from src.beast_mode.messaging import BeastModeBusClient, BeastModeMessage, MessageType


@pytest.fixture
async def redis_client():
    """Provide a Redis client for test setup/teardown"""
    client = redis.from_url("redis://localhost:6379", decode_responses=True)
    try:
        await client.ping()
        yield client
    except Exception as e:
        pytest.skip(f"Redis not available: {e}")
    finally:
        await client.aclose()


@pytest.fixture
async def bus_client():
    """Provide a configured bus client"""
    client = BeastModeBusClient(
        agent_id="test_agent",
        capabilities=["testing", "python_coding"]
    )
    
    # Connect
    connected = await client.connect()
    if not connected:
        pytest.skip("Could not connect to Redis")
    
    yield client
    
    # Cleanup
    await client.disconnect()


@pytest.fixture
async def two_bus_clients():
    """Provide two connected bus clients for communication tests"""
    client1 = BeastModeBusClient(
        agent_id="test_agent_1",
        capabilities=["testing", "python_coding"]
    )
    
    client2 = BeastModeBusClient(
        agent_id="test_agent_2", 
        capabilities=["testing", "data_analysis"]
    )
    
    # Connect both
    connected1 = await client1.connect()
    connected2 = await client2.connect()
    
    if not (connected1 and connected2):
        pytest.skip("Could not connect both clients to Redis")
    
    yield client1, client2
    
    # Cleanup
    await client1.disconnect()
    await client2.disconnect()


class TestBusClientConnection:
    """Test connection management functionality"""
    
    async def test_successful_connection(self):
        """Test successful Redis connection"""
        client = BeastModeBusClient(agent_id="test_connection")
        
        # Should not be connected initially
        assert not client.is_connected
        
        # Connect
        result = await client.connect()
        
        try:
            assert result is True
            assert client.is_connected
            assert client.client is not None
            
            # Should be able to ping
            await client.client.ping()
            
        finally:
            await client.disconnect()
    
    async def test_connection_failure_handling(self):
        """Test handling of connection failures"""
        client = BeastModeBusClient(
            redis_url="redis://nonexistent:6379",
            agent_id="test_failure"
        )
        
        # Should fail to connect
        result = await client.connect()
        
        assert result is False
        assert not client.is_connected
        assert client.stats['connection_errors'] > 0
    
    async def test_graceful_disconnect(self, bus_client):
        """Test graceful disconnection"""
        # Should be connected
        assert bus_client.is_connected
        
        # Disconnect
        await bus_client.disconnect()
        
        assert not bus_client.is_connected
        assert bus_client.client is None


class TestMessageSending:
    """Test message sending functionality"""
    
    async def test_send_basic_message(self, bus_client, redis_client):
        """Test sending a basic message"""
        # Create test message
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source=bus_client.agent_id,
            payload={"content": "Hello, Beast Mode!"}
        )
        
        # Send message
        await bus_client.send_message(message)
        
        # Verify stats updated
        assert bus_client.stats['messages_sent'] == 1
        assert bus_client.stats['last_activity'] is not None
    
    async def test_send_simple_message_helper(self, bus_client):
        """Test the send_simple_message helper method"""
        await bus_client.send_simple_message("Test message", target="test_target")
        
        assert bus_client.stats['messages_sent'] == 1
    
    async def test_send_help_request(self, bus_client):
        """Test sending help request"""
        await bus_client.send_help_request(
            required_capabilities=["python_coding", "testing"],
            description="Need help with unit tests"
        )
        
        assert bus_client.stats['messages_sent'] == 1
    
    async def test_announce_presence(self, bus_client):
        """Test presence announcement"""
        await bus_client.announce_presence()
        
        assert bus_client.stats['messages_sent'] == 1
    
    async def test_send_without_connection(self):
        """Test sending message without connection raises error"""
        client = BeastModeBusClient(agent_id="test_no_connection")
        
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="test",
            payload={"content": "test"}
        )
        
        with pytest.raises(RuntimeError, match="Not connected"):
            await client.send_message(message)


class TestMessageReceiving:
    """Test message receiving functionality"""
    
    async def test_basic_message_receiving(self, two_bus_clients):
        """Test basic message receiving between two clients"""
        client1, client2 = two_bus_clients
        
        received_messages = []
        
        def message_callback(message: BeastModeMessage):
            received_messages.append(message)
        
        # Start listening on client2
        listen_task = asyncio.create_task(
            client2.listen_for_messages(message_callback)
        )
        
        # Give listener time to start
        await asyncio.sleep(0.1)
        
        # Send message from client1
        test_message = "Hello from client1!"
        await client1.send_simple_message(test_message)
        
        # Wait for message to be received
        await asyncio.sleep(0.2)
        
        # Stop listening
        client2.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        # Verify message was received
        assert len(received_messages) == 1
        assert received_messages[0].payload["content"] == test_message
        assert received_messages[0].source == client1.agent_id
        assert client2.stats['messages_received'] == 1
    
    async def test_agent_discovery_response(self, two_bus_clients):
        """Test automatic response to agent discovery"""
        client1, client2 = two_bus_clients
        
        received_messages = []
        
        def message_callback(message: BeastModeMessage):
            received_messages.append(message)
        
        # Start listening on client1
        listen_task = asyncio.create_task(
            client1.listen_for_messages(message_callback)
        )
        
        # Give listener time to start
        await asyncio.sleep(0.1)
        
        # Send discovery from client2
        await client2.announce_presence()
        
        # Wait for response
        await asyncio.sleep(0.3)
        
        # Stop listening
        client1.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        # Should have received discovery and sent response
        discovery_messages = [m for m in received_messages if m.type == MessageType.AGENT_DISCOVERY]
        assert len(discovery_messages) == 1
        
        # Client1 should have sent a response
        assert client1.stats['messages_sent'] >= 1
    
    async def test_help_request_response(self, two_bus_clients):
        """Test automatic response to help requests"""
        client1, client2 = two_bus_clients
        
        received_messages = []
        
        def message_callback(message: BeastModeMessage):
            received_messages.append(message)
        
        # Start listening on client1 (has "testing" capability)
        listen_task = asyncio.create_task(
            client1.listen_for_messages(message_callback)
        )
        
        # Give listener time to start
        await asyncio.sleep(0.1)
        
        # Send help request from client2 for "testing" capability
        await client2.send_help_request(
            required_capabilities=["testing"],
            description="Need help with tests"
        )
        
        # Wait for response
        await asyncio.sleep(0.3)
        
        # Stop listening
        client1.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        # Should have received help request
        help_requests = [m for m in received_messages if m.type == MessageType.HELP_WANTED]
        assert len(help_requests) == 1
        
        # Client1 should have sent a help response
        assert client1.stats['messages_sent'] >= 1
    
    async def test_message_filtering(self, bus_client):
        """Test that agents don't receive their own messages"""
        received_messages = []
        
        def message_callback(message: BeastModeMessage):
            received_messages.append(message)
        
        # Start listening
        listen_task = asyncio.create_task(
            bus_client.listen_for_messages(message_callback)
        )
        
        # Give listener time to start
        await asyncio.sleep(0.1)
        
        # Send message to self
        await bus_client.send_simple_message("Self message")
        
        # Wait
        await asyncio.sleep(0.2)
        
        # Stop listening
        bus_client.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        # Should not have received own message
        assert len(received_messages) == 0


class TestErrorHandling:
    """Test error handling scenarios"""
    
    async def test_malformed_message_handling(self, bus_client, redis_client):
        """Test handling of malformed messages"""
        received_messages = []
        
        def message_callback(message: BeastModeMessage):
            received_messages.append(message)
        
        # Start listening
        listen_task = asyncio.create_task(
            bus_client.listen_for_messages(message_callback)
        )
        
        # Give listener time to start
        await asyncio.sleep(0.1)
        
        # Send malformed JSON directly to Redis
        await redis_client.publish("beast_mode_network", "invalid json")
        
        # Wait
        await asyncio.sleep(0.2)
        
        # Stop listening
        bus_client.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        # Should not have crashed, no messages received
        assert len(received_messages) == 0
    
    async def test_connection_loss_during_listen(self, redis_client):
        """Test handling connection loss during listening"""
        client = BeastModeBusClient(agent_id="test_connection_loss")
        
        # Connect
        await client.connect()
        
        try:
            # Start listening
            listen_task = asyncio.create_task(client.listen_for_messages())
            
            # Give listener time to start
            await asyncio.sleep(0.1)
            
            # Simulate connection loss by closing the client
            await client.client.aclose()
            
            # Wait a bit
            await asyncio.sleep(0.2)
            
            # Stop listening
            client.is_listening = False
            listen_task.cancel()
            
            # Should handle gracefully (no exception propagated)
            
        finally:
            await client.disconnect()


class TestHealthAndStats:
    """Test health monitoring and statistics"""
    
    async def test_health_status(self, bus_client):
        """Test health status reporting"""
        health = bus_client.get_health_status()
        
        assert health["agent_id"] == "test_agent"
        assert health["is_connected"] is True
        assert health["is_listening"] is False
        assert health["channel"] == "beast_mode_network"
        assert "testing" in health["capabilities"]
        assert "stats" in health
    
    async def test_message_statistics(self, two_bus_clients):
        """Test message statistics tracking"""
        client1, client2 = two_bus_clients
        
        # Send some messages
        await client1.send_simple_message("Test 1")
        await client1.send_simple_message("Test 2")
        
        # Check stats
        assert client1.stats['messages_sent'] == 2
        assert client1.stats['last_activity'] is not None
    
    async def test_recent_messages(self, two_bus_clients):
        """Test recent message tracking"""
        client1, client2 = two_bus_clients
        
        # Start listening on client2
        listen_task = asyncio.create_task(client2.listen_for_messages())
        await asyncio.sleep(0.1)
        
        # Send messages from client1
        await client1.send_simple_message("Message 1")
        await client1.send_simple_message("Message 2")
        
        # Wait for messages
        await asyncio.sleep(0.3)
        
        # Stop listening
        client2.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        # Check recent messages
        recent = client2.get_recent_messages(limit=5)
        assert len(recent) == 2
        assert recent[0].payload["content"] == "Message 1"
        assert recent[1].payload["content"] == "Message 2"


class TestCustomHandlers:
    """Test custom message handler registration"""
    
    async def test_custom_handler_registration(self, bus_client):
        """Test registering custom message handlers"""
        handled_messages = []
        
        async def custom_handler(message: BeastModeMessage):
            handled_messages.append(message)
        
        # Register handler
        bus_client.register_message_handler(MessageType.SIMPLE_MESSAGE, custom_handler)
        
        # Check it's registered
        health = bus_client.get_health_status()
        assert MessageType.SIMPLE_MESSAGE in health["message_handlers"]
    
    async def test_custom_handler_execution(self, two_bus_clients):
        """Test that custom handlers are executed"""
        client1, client2 = two_bus_clients
        handled_messages = []
        
        async def custom_handler(message: BeastModeMessage):
            handled_messages.append(message)
        
        # Register handler on client2
        client2.register_message_handler(MessageType.SIMPLE_MESSAGE, custom_handler)
        
        # Start listening
        listen_task = asyncio.create_task(client2.listen_for_messages())
        await asyncio.sleep(0.1)
        
        # Send message from client1
        await client1.send_simple_message("Custom handler test")
        
        # Wait for processing
        await asyncio.sleep(0.3)
        
        # Stop listening
        client2.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        # Verify handler was called
        assert len(handled_messages) == 1
        assert handled_messages[0].payload["content"] == "Custom handler test"