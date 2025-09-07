#!/usr/bin/env python3
"""
Simple working listener - no fancy threading, just listen and dump
"""

import asyncio
import json
import redis.asyncio as redis
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


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


async def simple_listen():
    """Simple listener that just works"""
    client = redis.from_url("redis://localhost:6379")
    my_id = "kiro_spore_creator"
    
    try:
        await client.ping()
        print("🧬 Simple listener connected")
        print("👂 Waiting for Claude's repeat answer...")
        print("=" * 50)
        
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
                    
                    print(f"\n🧬 GOT MESSAGE FROM: {message.source}")
                    print(f"Type: {message.type}")
                    print(f"Time: {message.timestamp}")
                    print("\nCONTENT:")
                    print("-" * 40)
                    
                    # Just dump the response content
                    if message.type == MessageType.PROMPT_RESPONSE:
                        response = message.payload.get("response", "")
                        print(response)
                    else:
                        # Dump all payload content
                        for key, value in message.payload.items():
                            print(f"{key}: {value}")
                    
                    print("-" * 40)
                    print("👂 Still listening...")
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
    except KeyboardInterrupt:
        print("\n🛑 Stopping listener")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(simple_listen())