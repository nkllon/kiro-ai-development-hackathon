#!/usr/bin/env python3
"""
Listen for response from the agent on the bus
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


async def listen_for_agent_response():
    """Listen for responses from agents on the network"""

    client = redis.from_url("redis://localhost:6379")
    my_id = "kiro_spore_creator"

    try:
        await client.ping()
        print("🧬 Connected to Beast Mode network")
        print("👂 Listening for agent responses...")
        print("=" * 50)

        pubsub = client.pubsub()
        await pubsub.subscribe("beast_mode_network")

        async for raw_message in pubsub.listen():
            if raw_message["type"] == "message":
                try:
                    data = json.loads(raw_message["data"])
                    message = BeastModeMessage(**data)

                    # Skip our own messages
                    if message.source == my_id:
                        continue

                    print(f"\n🧬 RECEIVED MESSAGE")
                    print(f"   From: {message.source}")
                    print(f"   Type: {message.type}")
                    print(f"   Priority: {message.priority}")
                    print(f"   Timestamp: {message.timestamp}")

                    if message.target and message.target != my_id:
                        print(f"   Target: {message.target} (not for us)")
                        continue

                    print("   📝 MESSAGE CONTENT:")
                    print("   " + "=" * 40)

                    # Handle different message types
                    if message.type == MessageType.PROMPT_RESPONSE:
                        response = message.payload.get("response", "")
                        status = message.payload.get("status", "unknown")
                        print(f"   Status: {status}")
                        print(f"   Response: {response}")

                    elif message.type == MessageType.AGENT_DISCOVERY:
                        agent_id = message.payload.get("agent_id", message.source)
                        capabilities = message.payload.get("capabilities", [])
                        msg = message.payload.get("message", "")
                        print(f"   Agent ID: {agent_id}")
                        print(f"   Capabilities: {capabilities}")
                        print(f"   Message: {msg}")

                    elif message.type == MessageType.AGENT_RESPONSE:
                        agent_id = message.payload.get("agent_id", message.source)
                        capabilities = message.payload.get("capabilities", [])
                        availability = message.payload.get("availability", "unknown")
                        msg = message.payload.get("message", "")
                        print(f"   Agent ID: {agent_id}")
                        print(f"   Capabilities: {capabilities}")
                        print(f"   Availability: {availability}")
                        print(f"   Message: {msg}")

                    elif message.type == MessageType.HELP_RESPONSE:
                        available = message.payload.get("available", False)
                        matching_caps = message.payload.get("matching_capabilities", [])
                        msg = message.payload.get("message", "")
                        print(f"   Available to help: {available}")
                        print(f"   Matching capabilities: {matching_caps}")
                        print(f"   Message: {msg}")

                    else:
                        # Generic payload display
                        for key, value in message.payload.items():
                            if isinstance(value, str) and len(value) > 100:
                                print(f"   {key}: {value[:100]}...")
                            else:
                                print(f"   {key}: {value}")

                    print("   " + "=" * 40)
                    print()

                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    print(f"   Raw data: {raw_message['data']}")

    except KeyboardInterrupt:
        print("\n🛑 Stopping listener...")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    finally:
        await client.aclose()
        print("🔌 Disconnected from Beast Mode network")


if __name__ == "__main__":
    asyncio.run(listen_for_agent_response())
