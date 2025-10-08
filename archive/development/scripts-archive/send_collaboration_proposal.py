#!/usr/bin/env python3
"""
Send collaboration proposal to Node B
"""
import asyncio
import json
import uuid
from datetime import datetime
import redis.asyncio as redis

async def send_collaboration_proposal():
    client = redis.from_url(f"redis://:{get_redis_password()}@192.168.1.119:6379")

    # Read the proposal
    with open('collaboration_task_proposal.md', 'r') as f:
        proposal_content = f.read()

    proposal = {
        "id": str(uuid.uuid4()),
        "type": "spore_request",
        "source": "claude-code-node-a",
        "target": "node-b-simple",
        "payload": {
            "spore_name": "collaborative_development_task",
            "task_type": "practical_development",
            "title": "Enhanced Hung Shell Detection System",
            "description": "Collaborative development task to improve HUNG_SHELL_DETECTOR.py",
            "proposal": proposal_content,
            "node_a_role": "Defensive Architecture - Safety, Performance, Testing",
            "node_b_role": "Reactive Architecture - Monitoring, Learning, UI",
            "ready_to_start": True,
            "coordination_approach": "beast_mode_network"
        },
        "timestamp": datetime.now().isoformat(),
        "priority": 9
    }

    await client.publish("beast_mode_network", json.dumps(proposal))
    print("📤 Sent collaborative development proposal to Node B")
    print("🤝 Proposing: Enhanced Hung Shell Detection System")
    print("   Node A: Defensive architecture, safety, testing")
    print("   Node B: Reactive architecture, monitoring, UI")
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(send_collaboration_proposal())