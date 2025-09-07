#!/usr/bin/env python3
"""
Fixed logger that logs ALL messages including my own (for queue verification)
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
        logging.FileHandler('beast_mode_mailbox.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    SPORE_REQUEST = "spore_request"
    PROMPT_RESPONSE = "prompt_response"
    PROMPT_REQUEST = "prompt_request"
    AGENT_DISCOVERY = "agent_discovery"
    AGENT_RESPONSE = "agent_response"


class BeastModeMessage(BaseModel):
    id: str
    type: MessageType
    source: str
    target: Optional[str]
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 5


async def mailbox_listener():
    """Mailbox that logs ALL messages (including my own for queue verification)"""
    client = redis.from_url("redis://localhost:6379")
    my_id = "kiro_spore_creator"
    
    try:
        await client.ping()
        logger.info("📬 Beast Mode Mailbox started")
        logger.info("👂 Listening for ALL messages (including my own for queue verification)")
        
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
                    
                    # Log ALL messages (including my own)
                    if message.source == my_id:
                        logger.info(f"📤 MY OWN MESSAGE (queue verification)")
                    else:
                        logger.info(f"📥 EXTERNAL MESSAGE")
                    
                    logger.info(f"   From: {message.source}")
                    logger.info(f"   Type: {message.type}")
                    logger.info(f"   Target: {message.target}")
                    logger.info(f"   Priority: {message.priority}")
                    
                    # Log payload content
                    for key, value in message.payload.items():
                        if isinstance(value, str) and len(value) > 200:
                            logger.info(f"   {key}: {value[:200]}... [TRUNCATED - {len(value)} chars total]")
                            # Save full content to file
                            filename = f"message_{message.source}_{datetime.now().strftime('%H%M%S')}.txt"
                            with open(filename, "w") as f:
                                f.write(f"From: {message.source}\n")
                                f.write(f"Type: {message.type}\n")
                                f.write(f"Target: {message.target}\n")
                                f.write(f"Time: {message.timestamp}\n")
                                f.write(f"\n{key}:\n{value}\n")
                            logger.info(f"💾 Full content saved to {filename}")
                        else:
                            logger.info(f"   {key}: {value}")
                    
                    logger.info("   " + "="*50)
                    
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    logger.error(f"Raw data: {raw_message['data']}")
                    
    except Exception as e:
        logger.error(f"❌ Connection error: {e}")
    finally:
        await client.aclose()
        logger.info("📬 Beast Mode Mailbox disconnected")


if __name__ == "__main__":
    logger.info("🚀 Starting Beast Mode Mailbox (logs ALL messages)")
    asyncio.run(mailbox_listener())