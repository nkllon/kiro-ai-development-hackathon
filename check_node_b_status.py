#!/usr/bin/env python3
"""
Check if Node B is still listening and ready to respond
"""
import asyncio
import json
import uuid
from datetime import datetime
import redis.asyncio as redis

async def check_node_b_status():
    client = redis.from_url("redis://:beastmode2025@192.168.1.119:6379")

    status_check = {
        "id": str(uuid.uuid4()),
        "type": "agent_discovery",
        "source": "claude-code-node-a",
        "target": "node-b-simple",
        "payload": {
            "message": "Node B - are you still listening? Did you receive the collaboration proposal?",
            "request_type": "status_check",
            "awaiting_response": True,
            "question": "Are you ready to collaborate on the hung shell detection system enhancement?"
        },
        "timestamp": datetime.now().isoformat(),
        "priority": 8
    }

    await client.publish("beast_mode_network", json.dumps(status_check))
    print("📤 Sent status check to Node B")
    print("❓ Question: Are you still listening and ready to collaborate?")
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(check_node_b_status())