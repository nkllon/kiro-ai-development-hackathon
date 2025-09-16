#!/usr/bin/env python3
"""
Send the design document to Claude using JSON format
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


async def send_design():
    """Send the design document to Claude"""
    client = redis.from_url("redis://localhost:6379")

    try:
        await client.ping()

        # Read the design file
        with open(
            ".kiro/specs/beast-mode-agent-collaboration-network/design.md", "r"
        ) as f:
            design_content = f.read()

        # Create structured JSON payload
        design_data = {
            "document_type": "design_document",
            "spec_name": "Beast Mode Agent Collaboration Network",
            "status": "Design Complete - Ready for Implementation",
            "design_content": design_content,
            "key_architecture_components": [
                "Redis Pub/Sub Message Bus",
                "BeastModeBusClient with connection management",
                "MailboxLogger for persistent message storage",
                "SporeManager for spore distribution",
                "Standardized MessageType enum",
                "AgentCapabilities model for discovery",
            ],
            "deployment_models": [
                "Single machine (macOS with local Redis)",
                "Distributed (multiple hosts with Redis cluster)",
            ],
            "performance_targets": {
                "message_throughput": "100+ messages/second per agent",
                "latency": "<100ms message delivery",
                "scalability": "10+ concurrent agents",
                "storage": "~1MB per 1000 messages",
            },
            "next_phase": "Implementation tasks ready for execution",
        }

        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.PROMPT_REQUEST,
            source="kiro_spore_creator",
            target="claude_assistant",
            payload={
                "message_type": "design_delivery",
                "design_data": design_data,
                "context": "Design phase complete - architecture and components defined",
            },
            timestamp=datetime.now(),
            priority=8,
        )

        await client.publish("beast_mode_network", message.model_dump_json())
        print("📤 Sent design document to Claude using JSON format")
        print(
            "🏗️  Architecture includes Redis pub/sub, mailbox logger, and spore manager"
        )

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(send_design())
