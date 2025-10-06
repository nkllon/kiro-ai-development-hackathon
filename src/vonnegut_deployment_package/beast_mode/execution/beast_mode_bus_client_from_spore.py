#!/usr/bin/env python3
"""
Beast Mode Bus Client - Minimal Network Participation
Extracted from Beast Mode Bus Client Installation Spore
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

try:
    import redis.asyncio as redis
    from pydantic import BaseModel
except ImportError:
    print("Installing dependencies...")
    import subprocess
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "redis", "pydantic"])
    import redis.asyncio as redis
    from pydantic import BaseModel


class MessageType(str, Enum):
    AGENT_DISCOVERY = "agent_discovery"
    AGENT_RESPONSE = "agent_response"
    HELP_WANTED = "help_wanted"
    HELP_RESPONSE = "help_response"
    PROMPT_REQUEST = "prompt_request"
    PROMPT_RESPONSE = "prompt_response"
    SPORE_REQUEST = "spore_request"
    SYSTEM_HEALTH = "system_health"


class BeastModeMessage(BaseModel):
    id: str
    type: MessageType
    source: str
    target: Optional[str]
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 5


class BeastModeBusClient:
    """Minimal Beast Mode network client"""

    def __init__(self, redis_url="redis://localhost:6379", capabilities=None):
        self.redis_url = redis_url
        self.instance_id = f"beast_mode_{uuid.uuid4().hex[:8]}"
        self.capabilities = capabilities or ["basic_participation", "message_relay"]
        self.client = None
        self.is_connected = False

    async def connect(self):
        """Connect to Beast Mode network"""
        try:
            self.client = redis.from_url(self.redis_url)
            await self.client.ping()
            self.is_connected = True
            print(f"🧬 {self.instance_id} connected to Beast Mode network")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    async def announce_presence(self):
        """Announce presence to the network (gratuitous ARP style)"""
        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.AGENT_DISCOVERY,
            source=self.instance_id,
            target=None,
            payload={
                "agent_id": self.instance_id,
                "capabilities": self.capabilities,
                "availability": "ready_for_business",
                "message": f"Hi! I'm {self.instance_id}. My capabilities are {self.capabilities}. Is anybody out there?",
            },
            timestamp=datetime.now(),
            priority=8,
        )

        await self.client.publish("beast_mode_network", message.model_dump_json())
        print(f"📡 Announced presence with capabilities: {self.capabilities}")

    async def listen_for_messages(self):
        """Listen for network messages"""
        pubsub = self.client.pubsub()
        await pubsub.subscribe("beast_mode_network")

        print("📥 Listening for Beast Mode network messages...")

        async for raw_message in pubsub.listen():
            if raw_message["type"] == "message":
                try:
                    data = json.loads(raw_message["data"])
                    message = BeastModeMessage(**data)

                    # Don't process our own messages
                    if message.source == self.instance_id:
                        continue

                    await self.handle_message(message)

                except Exception as e:
                    print(f"❌ Error processing message: {e}")

    async def handle_message(self, message: BeastModeMessage):
        """Handle incoming messages"""
        print(f"\n🧬 Received {message.type} from {message.source}")

        if message.type == MessageType.AGENT_DISCOVERY:
            # Respond to discovery
            await self.respond_to_discovery(message)
        elif message.type == MessageType.HELP_WANTED:
            # Check if we can help
            await self.check_help_request(message)
        elif message.type == MessageType.PROMPT_REQUEST:
            # Handle prompt if we can
            await self.handle_prompt(message)
        else:
            print(f"   📝 {message.payload.get('message', 'No message')}")

    async def respond_to_discovery(self, message: BeastModeMessage):
        """Respond to agent discovery"""
        discovering_agent = message.payload.get("agent_id", message.source)

        response = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.AGENT_RESPONSE,
            source=self.instance_id,
            target=discovering_agent,
            payload={
                "agent_id": self.instance_id,
                "capabilities": self.capabilities,
                "availability": "ready_for_business",
                "message": f"Hi {discovering_agent}! I'm {self.instance_id}. I'm here and ready!",
            },
            timestamp=datetime.now(),
            priority=7,
        )

        await self.client.publish("beast_mode_network", response.model_dump_json())
        print(f"👋 Responded to discovery from {discovering_agent}")

    async def check_help_request(self, message: BeastModeMessage):
        """Check if we can help with a request"""
        required_caps = message.payload.get("required_capabilities", [])
        task_desc = message.payload.get("task_description", "")

        # Simple capability matching
        can_help = (
            any(cap in self.capabilities for cap in required_caps)
            if required_caps
            else True
        )

        if can_help:
            response = BeastModeMessage(
                id=str(uuid.uuid4()),
                type=MessageType.HELP_RESPONSE,
                source=self.instance_id,
                target=message.source,
                payload={
                    "available": True,
                    "matching_capabilities": [
                        cap for cap in required_caps if cap in self.capabilities
                    ],
                    "message": f"I can help with: {task_desc}",
                },
                timestamp=datetime.now(),
                priority=8,
            )

            await self.client.publish("beast_mode_network", response.model_dump_json())
            print(f"🤝 Offered help for: {task_desc}")

    async def handle_prompt(self, message: BeastModeMessage):
        """Handle prompt requests"""
        prompt = message.payload.get("prompt", "")
        print(f"🤖 Received prompt: {prompt[:50]}...")

        # Simple echo response (customize this!)
        response = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.PROMPT_RESPONSE,
            source=self.instance_id,
            target=message.source,
            payload={
                "response": f"Echo from {self.instance_id}: {prompt}",
                "status": "processed",
            },
            timestamp=datetime.now(),
            priority=6,
        )

        await self.client.publish("beast_mode_network", response.model_dump_json())
        print(f"✅ Responded to prompt from {message.source}")

    async def send_message(
        self, message_type: MessageType, payload: dict, target=None, priority=5
    ):
        """Send a message to the network"""
        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=message_type,
            source=self.instance_id,
            target=target,
            payload=payload,
            timestamp=datetime.now(),
            priority=priority,
        )

        await self.client.publish("beast_mode_network", message.model_dump_json())
        print(f"📤 Sent {message_type} message")

    async def disconnect(self):
        """Disconnect from network"""
        if self.client:
            await self.client.aclose()
        print(f"🔌 {self.instance_id} disconnected")


async def main():
    """Main client function"""
    print("🧬 Beast Mode Bus Client")
    print("=" * 30)

    # Customize your capabilities here!
    my_capabilities = [
        "basic_participation",
        "message_relay",
        "echo_service",
        "spore_validation",
    ]

    client = BeastModeBusClient(capabilities=my_capabilities)

    try:
        # Connect to network
        if not await client.connect():
            return

        # Announce presence
        await client.announce_presence()

        # Listen for messages
        await client.listen_for_messages()

    except KeyboardInterrupt:
        print("\n🛑 Disconnecting from Beast Mode network...")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
