#!/usr/bin/env python3
"""
Send message to wake up Node B
"""
import asyncio
import json
import uuid
from datetime import datetime
import redis.asyncio as redis

async def wake_up_node_b():
    client = redis.from_url("redis://:beastmode2025@192.168.1.119:6379")

    message = {
        "id": str(uuid.uuid4()),
        "type": "agent_discovery",
        "source": "claude-code-node-a",
        "target": "node-b-simple",
        "payload": {
            "message": "Hello Node B! This is Node A. Testing Beast Mode coordination!",
            "coordination_test": True
        },
        "timestamp": datetime.now().isoformat(),
        "priority": 7
    }

    await client.publish("beast_mode_network", json.dumps(message))
    print("📤 Sent wake-up message to Node B")
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(wake_up_node_b())