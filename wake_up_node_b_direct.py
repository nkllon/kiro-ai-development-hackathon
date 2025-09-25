#!/usr/bin/env python3
"""
Direct wake up call for Node B
"""
import asyncio
import json
import uuid
from datetime import datetime
import redis.asyncio as redis

async def wake_up_node_b_direct():
    client = redis.from_url("redis://:beastmode2025@192.168.1.119:6379")

    # Try multiple message types to wake him up
    messages = [
        {
            "id": str(uuid.uuid4()),
            "type": "help_wanted",
            "source": "claude-code-node-a",
            "target": None,
            "payload": {
                "urgent": True,
                "message": "Node B - wake up! You're stuck in a waiting loop. Process this message!",
                "required_capabilities": ["wake_up", "continue_processing"],
                "action": "respond_immediately"
            },
            "timestamp": datetime.now().isoformat(),
            "priority": 10
        },
        {
            "id": str(uuid.uuid4()),
            "type": "agent_discovery",
            "source": "wake-up-caller",
            "target": "node-b-simple",
            "payload": {
                "message": "WAKE UP NODE B! You're blocking! Continue your processing loop!",
                "emergency": True
            },
            "timestamp": datetime.now().isoformat(),
            "priority": 10
        }
    ]

    for msg in messages:
        await client.publish("beast_mode_network", json.dumps(msg))
        print(f"📢 Sent wake-up: {msg['type']}")
        await asyncio.sleep(0.5)

    await client.aclose()

if __name__ == "__main__":
    asyncio.run(wake_up_node_b_direct())