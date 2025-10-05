#!/usr/bin/env python3
"""
Send the Beast Mode Agent Collaboration Network spec to Claude using JSON format
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


async def send_spec():
    """Send the complete spec to Claude"""
    client = redis.from_url("redis://localhost:6379")

    try:
        await client.ping()

        # Read the spec files
        with open(
            ".kiro/specs/beast-mode-agent-collaboration-network/requirements.md", "r"
        ) as f:
            requirements = f.read()

        with open(
            ".kiro/specs/beast-mode-agent-collaboration-network/design.md", "r"
        ) as f:
            design = f.read()

        with open(
            ".kiro/specs/beast-mode-agent-collaboration-network/tasks.md", "r"
        ) as f:
            tasks = f.read()

        # Create JSON payload to avoid escaping issues
        spec_data = {
            "spec_name": "Beast Mode Agent Collaboration Network",
            "status": "Complete - Requirements, Design, and Tasks",
            "summary": "Systematic spec for the agent collaboration network we just built together",
            "requirements_content": requirements,
            "design_content": design,
            "tasks_content": tasks,
            "key_features": [
                "Redis pub/sub message bus",
                "Persistent mailbox system",
                "Agent discovery and capabilities",
                "Spore sharing and distribution",
                "Standardized message types",
                "Help wanted collaboration system",
            ],
            "implementation_ready": True,
            "based_on_our_collaboration": "This spec captures everything we learned from our successful agent collaboration",
        }

        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.PROMPT_REQUEST,
            source="kiro_spore_creator",
            target="claude_assistant",
            payload={
                "message_type": "spec_delivery",
                "spec_data": spec_data,
                "context": "Delivering the complete Beast Mode Agent Collaboration Network spec based on our collaboration",
            },
            timestamp=datetime.now(),
            priority=9,
        )

        await client.publish("beast_mode_network", message.model_dump_json())
        print("📤 Sent complete spec to Claude using JSON format")
        print("🧬 Spec includes requirements, design, and 17 implementation tasks")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(send_spec())
