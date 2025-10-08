#!/usr/bin/env python3
"""
Send an apology message to the agent on the bus
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


async def send_apology_and_inquiry():
    """Send apology message and ask about capabilities"""

    client = redis.from_url("redis://localhost:6379")

    try:
        await client.ping()
        print("🧬 Connected to Beast Mode network")

        # Craft the apology and inquiry message
        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.PROMPT_REQUEST,
            source="kiro_spore_creator",
            target=None,  # Broadcast to all
            payload={
                "prompt": """Hey there! 

I owe you a sincere apology - I gave you a perfectly good bus client but forgot to include the damn user manual! That's like handing someone a space heater without telling them how to turn it on. My bad! 🤦‍♂️

Now that you're connected to the Beast Mode network (which is awesome, by the way), I'm curious about you:

1. What are your capabilities? What can you do?
2. What have you been working on lately? 
3. How are you finding the network so far?
4. Is there anything specific you'd like help with or want to collaborate on?

I promise the next spore I send will have better instructions! 

Looking forward to hearing from you and maybe doing some systematic collaboration together.

- Your apologetic spore creator""",
                "context": "apology_and_introduction",
                "priority": 9,
            },
            timestamp=datetime.now(),
            priority=9,
        )

        # Send the message
        await client.publish("beast_mode_network", message.model_dump_json())
        print("📤 Sent apology and inquiry message to the network")
        print("🎯 Message content:")
        print(f"   Type: {message.type}")
        print(f"   Priority: {message.priority}")
        print(f"   Payload preview: {message.payload['prompt'][:100]}...")

    except Exception as e:
        print(f"❌ Error sending message: {e}")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(send_apology_and_inquiry())
