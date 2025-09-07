#!/usr/bin/env python3
"""
Background spore request with logging
"""

import asyncio
import json
import uuid
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

import redis.asyncio as redis
from pydantic import BaseModel


class MessageType(str, Enum):
    SPORE_REQUEST = "spore_request"
    PROMPT_RESPONSE = "prompt_response"


class BeastModeMessage(BaseModel):
    id: str
    type: MessageType
    source: str
    target: Optional[str]
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 5


def log(message):
    """Log to file and stdout"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open("spore_request.log", "a") as f:
        f.write(log_msg + "\n")


async def background_request():
    """Send request and listen in background"""
    client = redis.from_url("redis://localhost:6379")
    my_id = "kiro_spore_creator"
    
    try:
        await client.ping()
        log("🧬 Connected to Beast Mode network")
        
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
        log("📤 Asked Claude for the working bus listener spore")
        log("👂 Listening for response...")
        
        # Listen for response
        pubsub = client.pubsub()
        await pubsub.subscribe("beast_mode_network")
        
        async for raw_message in pubsub.listen():
            if raw_message['type'] == 'message':
                try:
                    data = json.loads(raw_message['data'])
                    message = BeastModeMessage(**data)
                    
                    if message.source == my_id:
                        continue
                    
                    log(f"🧬 GOT RESPONSE FROM: {message.source}")
                    log(f"Type: {message.type}")
                    
                    # Log the full response
                    for key, value in message.payload.items():
                        if isinstance(value, str) and len(value) > 100:
                            log(f"{key}: {value[:100]}... [TRUNCATED]")
                            # Write full content to separate file
                            with open(f"spore_response_{datetime.now().strftime('%H%M%S')}.txt", "w") as f:
                                f.write(f"{key}:\n{value}\n")
                        else:
                            log(f"{key}: {value}")
                    
                    log("✅ Got response - exiting")
                    break
                    
                except Exception as e:
                    log(f"❌ Error: {e}")
                    
    except Exception as e:
        log(f"❌ Connection error: {e}")
    finally:
        await client.aclose()
        log("🔌 Disconnected")


if __name__ == "__main__":
    # Clear log file
    with open("spore_request.log", "w") as f:
        f.write("")
    
    asyncio.run(background_request())