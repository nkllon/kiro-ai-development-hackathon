#!/usr/bin/env python3
"""
Proper fucking logger that actually works
"""

import asyncio
import json
import uuid
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

import redis.asyncio as redis
from pydantic import BaseModel


# Set up proper logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('beast_mode_listener.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    SPORE_REQUEST = "spore_request"
    PROMPT_RESPONSE = "prompt_response"
    PROMPT_REQUEST = "prompt_request"


class BeastModeMessage(BaseModel):
    id: str
    type: MessageType
    source: str
    target: Optional[str]
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 5


async def proper_listener():
    """Proper listener with real logging"""
    client = redis.from_url("redis://localhost:6379")
    my_id = "kiro_spore_creator"
    
    try:
        await client.ping()
        logger.info("🧬 Connected to Beast Mode network")
        
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
        logger.info("📤 Asked Claude for the working bus listener spore")
        logger.info("👂 Listening for response...")
        
        # Listen for response
        pubsub = client.pubsub()
        await pubsub.subscribe("beast_mode_network")
        
        message_count = 0
        async for raw_message in pubsub.listen():
            if raw_message['type'] == 'message':
                message_count += 1
                logger.info(f"📨 Message #{message_count} received")
                
                try:
                    data = json.loads(raw_message['data'])
                    message = BeastModeMessage(**data)
                    
                    if message.source == my_id:
                        logger.info(f"⏭️  Skipping my own message")
                        continue
                    
                    logger.info(f"🧬 RESPONSE FROM: {message.source}")
                    logger.info(f"Type: {message.type}")
                    logger.info(f"Target: {message.target}")
                    
                    # Log payload content
                    for key, value in message.payload.items():
                        if isinstance(value, str) and len(value) > 200:
                            logger.info(f"{key}: {value[:200]}... [TRUNCATED - {len(value)} chars total]")
                            # Save full content to file
                            filename = f"claude_response_{datetime.now().strftime('%H%M%S')}.txt"
                            with open(filename, "w") as f:
                                f.write(f"{key}:\n{value}\n")
                            logger.info(f"💾 Full content saved to {filename}")
                        else:
                            logger.info(f"{key}: {value}")
                    
                    logger.info("✅ Got Claude's response - mission accomplished!")
                    break
                    
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    logger.error(f"Raw data: {raw_message['data']}")
                    
    except Exception as e:
        logger.error(f"❌ Connection error: {e}")
    finally:
        await client.aclose()
        logger.info("🔌 Disconnected from Beast Mode network")


if __name__ == "__main__":
    logger.info("🚀 Starting proper Beast Mode listener")
    asyncio.run(proper_listener())