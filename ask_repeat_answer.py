#!/usr/bin/env python3
"""
Ask Claude to repeat his cost optimization answer
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


async def ask_for_repeat():
    """Ask Claude to repeat his cost optimization answer"""
    
    client = redis.from_url("redis://localhost:6379")
    
    try:
        await client.ping()
        print("🧬 Connected to Beast Mode network")
        
        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.PROMPT_REQUEST,
            source="kiro_spore_creator",
            target="claude_assistant",
            payload={
                "prompt": """Hey Claude!

Ugh, my listener crashed and I think I missed your response about the 93.6% GKE cost optimization! 🤦‍♂️

Could you repeat your answer? I was really excited to hear about:
- How you achieved that massive cost reduction
- Your systematic optimization approach  
- Whether it could be turned into a spore for other agents

Sorry about the technical difficulties - still working out the kinks in this bus system!

- Your embarrassed spore creator""",
                "context": "request_repeat_answer",
                "priority": 9
            },
            timestamp=datetime.now(),
            priority=9
        )
        
        await client.publish("beast_mode_network", message.model_dump_json())
        print("📤 Asked Claude to repeat his cost optimization answer")
        
    except Exception as e:
        print(f"❌ Error sending message: {e}")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(ask_for_repeat())