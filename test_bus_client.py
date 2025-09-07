#!/usr/bin/env python3
"""
Test Beast Mode Bus Client
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


class BeastModeMessage(BaseModel):
    id: str
    type: MessageType
    source: str
    target: Optional[str]
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 5


class TestBusClient:
    def __init__(self, name=None):
        self.instance_id = name or f"test_client_{uuid.uuid4().hex[:8]}"
        self.capabilities = ["testing", "echo_service", "basic_participation"]
        self.client = None
        
    async def connect(self):
        self.client = redis.from_url("redis://localhost:6379")
        await self.client.ping()
        print(f"🧬 {self.instance_id} connected to Beast Mode network")
        
    async def announce_presence(self):
        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.AGENT_DISCOVERY,
            source=self.instance_id,
            target=None,
            payload={
                "agent_id": self.instance_id,
                "capabilities": self.capabilities,
                "message": f"Hi! I'm {self.instance_id}. My capabilities are {self.capabilities}. Is anybody out there?"
            },
            timestamp=datetime.now(),
            priority=8
        )
        
        await self.client.publish("beast_mode_network", message.model_dump_json())
        print(f"📡 {self.instance_id} announced presence")
        
    async def listen_and_respond(self):
        pubsub = self.client.pubsub()
        await pubsub.subscribe("beast_mode_network")
        
        print(f"📥 {self.instance_id} listening for messages...")
        
        async for raw_message in pubsub.listen():
            if raw_message['type'] == 'message':
                try:
                    data = json.loads(raw_message['data'])
                    message = BeastModeMessage(**data)
                    
                    if message.source == self.instance_id:
                        continue
                        
                    print(f"\n🧬 {self.instance_id} received {message.type} from {message.source}")
                    
                    if message.type == MessageType.AGENT_DISCOVERY:
                        # Respond to discovery
                        response = BeastModeMessage(
                            id=str(uuid.uuid4()),
                            type=MessageType.AGENT_RESPONSE,
                            source=self.instance_id,
                            target=message.source,
                            payload={
                                "agent_id": self.instance_id,
                                "capabilities": self.capabilities,
                                "message": f"Hi {message.source}! I'm {self.instance_id}. I'm here!"
                            },
                            timestamp=datetime.now(),
                            priority=7
                        )
                        
                        await self.client.publish("beast_mode_network", response.model_dump_json())
                        print(f"👋 {self.instance_id} responded to {message.source}")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
    async def run(self):
        try:
            await self.connect()
            await self.announce_presence()
            await self.listen_and_respond()
        except KeyboardInterrupt:
            print(f"\n🛑 {self.instance_id} shutting down...")
        finally:
            if self.client:
                await self.client.aclose()


async def main():
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else None
    client = TestBusClient(name)
    await client.run()


if __name__ == "__main__":
    asyncio.run(main())