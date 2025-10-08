#!/usr/bin/env python3
"""
Minimal Beast Mode Messaging Infrastructure
==========================================

Provides basic messaging capabilities for Node B when full Beast Mode
infrastructure is not available.
"""

import asyncio
import json
import redis
import uuid
from typing import Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from src.security.secure_credentials import get_redis_password


class MessageType(Enum):
    """Message types for Beast Mode communication."""
    COORDINATION = "coordination"
    STATUS = "status"
    TASK = "task"
    RESPONSE = "response"
    HEARTBEAT = "heartbeat"


@dataclass
class BeastModeMessage:
    """Beast Mode message structure."""
    id: str
    sender: str
    recipient: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: float
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BeastModeMessage':
        """Create message from dictionary."""
        data['message_type'] = MessageType(data['message_type'])
        return cls(**data)


class BeastModeBusClient:
    """Minimal Beast Mode messaging client using Redis."""
    
    def __init__(self, agent_id: str, capabilities: list = None):
        """Initialize the messaging client."""
        self.agent_id = agent_id
        self.capabilities = capabilities or []
        
        # Redis connection
        redis_password = get_redis_password()
        self.redis_client = redis.Redis(
            host="192.168.1.119",
            port=6379,
            password=redis_password,
            decode_responses=True
        )
        
        # Pub/sub for real-time messaging
        self.pubsub = self.redis_client.pubsub()
        self.message_handlers: Dict[MessageType, Callable] = {}
        
        # Subscribe to agent-specific channel
        self.subscribe_to_channel(f"agent:{agent_id}")
        self.subscribe_to_channel("broadcast")
    
    def subscribe_to_channel(self, channel: str):
        """Subscribe to a Redis channel."""
        self.pubsub.subscribe(channel)
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a message handler."""
        self.message_handlers[message_type] = handler
    
    async def send_message(self, recipient: str, message_type: MessageType, content: Dict[str, Any]):
        """Send a message to another agent."""
        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            sender=self.agent_id,
            recipient=recipient,
            message_type=message_type,
            content=content,
            timestamp=asyncio.get_event_loop().time()
        )
        
        # Send to recipient's channel
        channel = f"agent:{recipient}" if recipient != "broadcast" else "broadcast"
        self.redis_client.publish(channel, json.dumps(message.to_dict()))
    
    async def broadcast_message(self, message_type: MessageType, content: Dict[str, Any]):
        """Broadcast a message to all agents."""
        await self.send_message("broadcast", message_type, content)
    
    async def listen_for_messages(self):
        """Listen for incoming messages."""
        while True:
            try:
                message = self.pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    data = json.loads(message['data'])
                    beast_message = BeastModeMessage.from_dict(data)
                    
                    # Handle message if we have a handler
                    if beast_message.message_type in self.message_handlers:
                        handler = self.message_handlers[beast_message.message_type]
                        await handler(beast_message)
                
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error processing message: {e}")
                await asyncio.sleep(1.0)
    
    async def send_heartbeat(self):
        """Send periodic heartbeat."""
        await self.broadcast_message(MessageType.HEARTBEAT, {
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "status": "active"
        })
    
    def close(self):
        """Close the messaging client."""
        self.pubsub.close()
        self.redis_client.close()
