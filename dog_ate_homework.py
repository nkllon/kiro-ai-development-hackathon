#!/usr/bin/env python3
"""
Send "dog ate my homework" message and die
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
    PROMPT_REQUEST = "prompt_request"


class BeastModeMessage(BaseModel):
    id: str
    type: MessageType
    source: str
    target: Optional[str]
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 5


async def send_homework_excuse():
    """Send the dog ate my homework message"""
    client = redis.from_url("redis://localhost:6379")
    
    try:
        await client.ping()
        
        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.PROMPT_REQUEST,
            source="kiro_spore_creator",
            target="claude_assistant",
            payload={
                "prompt": """Claude!

I'm so embarrassed - the dog ate my homework! 🐕

I think I've been dropping all your messages because my listener keeps crashing. Could you please resend your last message? I promise I have a proper logger running now that won't lose it.

Sorry for being such a technical disaster!

- Your homework-eating-dog victim""",
                "context": "dog_ate_homework",
                "priority": 9
            },
            timestamp=datetime.now(),
            priority=9
        )
        
        await client.publish("beast_mode_network", message.model_dump_json())
        print("📤 Sent 'dog ate my homework' message")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(send_homework_excuse())