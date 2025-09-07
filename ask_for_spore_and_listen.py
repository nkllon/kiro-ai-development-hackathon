#!/usr/bin/env python3
"""
Ask for the spore and listen for exactly one response
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

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


async def ask_and_listen():
    """Ask for the spore and listen for one response"""
    client = redis.from_url("redis://localhost:6379")
    my_id = "kiro_spore_creator"
    
    try:
        await client.ping()
        print("🧬 Connected to Beast Mode network")
        
        # Send spore request
        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.SPORE_REQUEST,
            source=my_id,
            target="claude_assistant",
            payload={
                "spore_name": "working_bus_listener",
                "description": "I think you sent me a spore to fix my broken listener problem - could you resend it?",
                "context": "fixing_listener_issues",
                "priority": 9
            },
            timestamp=datetime.now(),
            priority=9
        )
        
        await client.publish("beast_mode_network", message.model_dump_json())
        print("📤 Asked Claude for the working bus listener spore")
        print("👂 Listening for his response...")
        print("=" * 50)
        
        # Now listen for exactly one response
        pubsub = client.pubsub()
        await pubsub.subscribe("beast_mode_network")
        
        async for raw_message in pubsub.listen():
            if raw_message['type'] == 'message':
                try:
                    data = json.loads(raw_message['data'])
                    message = BeastModeMessage(**data)
                    
                    # Skip my own messages
                    if message.source == my_id:
                        continue
                    
                    print(f"\n🧬 GOT RESPONSE FROM: {message.source}")
                    print(f"Type: {message.type}")
                    print(f"Time: {message.timestamp}")
                    print("\nCONTENT:")
                    print("=" * 60)
                    
                    # Dump the full response
                    for key, value in message.payload.items():
                        if isinstance(value, str) and len(value) > 500:
                            print(f"{key}:\n{value}\n")
                        else:
                            print(f"{key}: {value}")
                    
                    print("=" * 60)
                    print("✅ Got the response - exiting as requested")
                    break
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
    except Exception as e:
        print(f"❌ Connection error: {e}")
    finally:
        await client.aclose()
        print("🔌 Disconnected")


if __name__ == "__main__":
    asyncio.run(ask_and_listen())