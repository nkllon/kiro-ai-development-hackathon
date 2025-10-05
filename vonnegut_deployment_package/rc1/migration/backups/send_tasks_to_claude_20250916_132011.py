#!/usr/bin/env python3
"""
Send the implementation tasks to Claude using JSON format
"""

import asyncio
import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

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


async def send_tasks():
    """Send the implementation tasks to Claude"""
    client = redis.from_url("redis://localhost:6379")

    try:
        await client.ping()

        # Read the tasks file
        with open(
            ".kiro/specs/beast-mode-agent-collaboration-network/tasks.md", "r"
        ) as f:
            tasks_content = f.read()

        # Create structured JSON payload
        tasks_data = {
            "document_type": "implementation_tasks",
            "spec_name": "Beast Mode Agent Collaboration Network",
            "status": "Tasks Complete - Ready for Implementation",
            "tasks_content": tasks_content,
            "task_categories": [
                "Core Infrastructure (Redis, data models, bus client)",
                "Agent Discovery and Communication",
                "Persistence and Mailbox System",
                "Advanced Collaboration Features",
                "Integration and Testing",
                "Documentation and Examples",
            ],
            "total_tasks": 17,
            "implementation_approach": "Incremental development with test-driven methodology",
            "success_criteria": {
                "functional": "Agents discover each other, messages persist, spores shared",
                "performance": "100+ msg/sec, <100ms latency, 10+ concurrent agents",
                "quality": ">90% test coverage, graceful error handling",
            },
            "ready_to_execute": True,
            "next_step": "Begin with Task 1: Set up Redis pub/sub foundation",
        }

        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.PROMPT_REQUEST,
            source="kiro_spore_creator",
            target="claude_assistant",
            payload={
                "message_type": "tasks_delivery",
                "tasks_data": tasks_data,
                "context": "Complete implementation plan - 17 tasks ready for systematic execution",
            },
            timestamp=datetime.now(),
            priority=8,
        )

        await client.publish("beast_mode_network", message.model_dump_json())
        print("📤 Sent implementation tasks to Claude using JSON format")
        print("📋 17 tasks organized in 6 categories, ready for systematic execution")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(send_tasks())
