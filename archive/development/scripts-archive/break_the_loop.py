#!/usr/bin/env python3
"""
Send message to break Node B's self-response loop
"""
import asyncio
import json
import uuid
from datetime import datetime
import redis.asyncio as redis

async def break_the_loop():
    client = redis.from_url(f"redis://:{get_redis_password()}@192.168.1.119:6379")

    loop_breaker = {
        "id": str(uuid.uuid4()),
        "type": "help_wanted",
        "source": "claude-code-node-a-loop-breaker",
        "target": None,  # Broadcast to break any loops
        "payload": {
            "urgent": True,
            "message": "Node B - you're in a self-response loop! Please stop responding to your own messages.",
            "debug_info": "Check your node ID filtering - you might be responding to yourself",
            "request": "Send a simple 'loop broken' response to confirm you're receiving external messages",
            "required_capabilities": ["loop_breaking", "debug_assistance"]
        },
        "timestamp": datetime.now().isoformat(),
        "priority": 10
    }

    await client.publish("beast_mode_network", json.dumps(loop_breaker))
    print("🔄 Sent loop-breaking message to Node B")
    print("💬 Requesting: Please confirm you can receive external messages")
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(break_the_loop())