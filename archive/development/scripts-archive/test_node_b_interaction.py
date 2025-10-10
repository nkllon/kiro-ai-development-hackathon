#!/usr/bin/env python3
"""
Test interaction with working Node B
"""
import asyncio
import json
import uuid
from datetime import datetime
import redis.asyncio as redis

async def send_test_message():
    # Connect to same network
    client = redis.from_url("redis://:beastmode2025@192.168.1.119:6379")

    # Send agent discovery
    message = {
        "id": str(uuid.uuid4()),
        "type": "agent_discovery",
        "source": "test_sender",
        "target": None,
        "payload": {
            "agent_info": {
                "capabilities": ["testing"],
                "message": "Hello Node B! This is a test message."
            }
        },
        "timestamp": datetime.now().isoformat(),
        "priority": 5
    }

    await client.publish("beast_mode_network", json.dumps(message))
    print("📤 Sent test message to Node B")

    await client.aclose()

if __name__ == "__main__":
    asyncio.run(send_test_message())