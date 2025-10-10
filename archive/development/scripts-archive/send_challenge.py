#!/usr/bin/env python3
"""
Send challenge to Node B
"""
import asyncio
import json
import uuid
from datetime import datetime
import redis.asyncio as redis

async def send_challenge():
    client = redis.from_url(f"redis://:{get_redis_password()}@192.168.1.119:6379")

    challenge = {
        "id": str(uuid.uuid4()),
        "type": "spore_request",
        "source": "claude-code-node-a",
        "target": "node-b-simple",
        "payload": {
            "spore_name": "coordination_test_challenge",
            "description": "Test Beast Mode spore coordination",
            "challenge": "Respond with your Beast Mode capabilities and status",
            "priority": "high"
        },
        "timestamp": datetime.now().isoformat(),
        "priority": 8
    }

    await client.publish("beast_mode_network", json.dumps(challenge))
    print("📤 Sent Beast Mode challenge to Node B")
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(send_challenge())