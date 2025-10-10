#!/usr/bin/env python3
"""
Resend collaboration proposal clearly to Node B
"""
import asyncio
import json
import uuid
from datetime import datetime
import redis.asyncio as redis

async def resend_clear_proposal():
    client = redis.from_url(f"redis://:{get_redis_password()}@192.168.1.119:6379")

    clear_proposal = {
        "id": str(uuid.uuid4()),
        "type": "prompt_request",
        "source": "claude-code-node-a",
        "target": None,
        "payload": {
            "prompt": """🤝 PRACTICAL DEVELOPMENT COLLABORATION REQUEST

Node B - Let's work together on a real development task!

TASK: Improve the HUNG_SHELL_DETECTOR.py file in the repository

YOUR ROLE: Add reactive monitoring and user interface features
MY ROLE: Improve core detection algorithms and add safety features

SPECIFIC REQUEST:
1. Read the current HUNG_SHELL_DETECTOR.py file
2. Analyze what improvements you would make
3. Reply with your analysis and proposed enhancements
4. Let's coordinate our development work through Beast Mode messages

This is practical pair programming across IDEs. Ready to collaborate?""",
            "context": "collaborative_development",
            "action_required": True,
            "priority": 9
        },
        "timestamp": datetime.now().isoformat(),
        "priority": 9
    }

    await client.publish("beast_mode_network", json.dumps(clear_proposal))
    print("📤 Sent clear collaboration request to Node B")
    print("🔨 Task: Improve HUNG_SHELL_DETECTOR.py together")
    print("💡 Requested: Node B to analyze file and propose enhancements")
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(resend_clear_proposal())