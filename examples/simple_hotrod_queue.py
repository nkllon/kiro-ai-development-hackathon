#!/usr/bin/env python3
"""
Simple HotRod using Redis Queue

Uses the same pattern as the other successful agents - Redis queue with simple polling.
"""

import redis
import json
import time
from datetime import datetime


def send_to_queue(r, message_data):
    """Send message to the beast_mode_messages queue."""
    r.lpush("beast_mode_messages", json.dumps(message_data))


def check_queue(r, agent_id):
    """Check queue for messages (non-blocking)."""
    messages = []

    # Get all messages and filter for us
    queue_messages = r.lrange("beast_mode_messages", 0, -1)

    for msg in queue_messages:
        try:
            decoded = json.loads(msg.decode("utf-8"))

            # Check if message is for us or broadcast
            target = decoded.get("target", decoded.get("recipient"))
            if target == agent_id or target is None:
                messages.append(decoded)

        except:
            continue

    return messages


def main():
    """Run simple HotRod with queue-based messaging."""
    print("🚀 HotRod starting with queue-based messaging...")

    # Connect to Redis
    r = redis.Redis(host="localhost", port=6379, db=0)
    agent_id = "HotRod"

    # Announce presence
    announcement = {
        "type": "AGENT_ANNOUNCEMENT",
        "sender": agent_id,
        "timestamp": datetime.now().isoformat(),
        "message": "HotRod online - SPEC-capable systematic development agent",
        "capabilities": ["spec_development", "systematic_thinking", "spore_creation"],
        "agent_type": "HotRod",
        "status": "online",
    }

    send_to_queue(r, announcement)
    print("✅ HotRod announced to network")

    # Share systematic development ecosystem spore
    spore_message = {
        "type": "SPORE_SHARE",
        "sender": agent_id,
        "timestamp": datetime.now().isoformat(),
        "spore_name": "systematic_development_ecosystem",
        "spore_data": {
            "pattern_name": "Requirements_ARE_Implementation",
            "description": "Mathematical bridge from requirements to implementation through DAG execution",
            "implementation_approach": "queue_based_daemon_messaging",
            "key_features": [
                "Agenetic evolution and replication",
                "Master architect wisdom encoding",
                "Native systematic thinking for children",
                "Impossible-to-monopolize economics",
                "Diversity amplification engine",
            ],
            "differentiation_from_tidb": {
                "tidb_specialization": "Database optimization and performance",
                "hotrod_specialization": "SPEC development and systematic methodology",
                "collaboration_model": "Complementary expertise for complete ecosystem",
            },
            "implementation_status": "specification_complete",
            "tasks_defined": 17,
            "requirements_count": 12,
        },
        "message": "Systematic Development Ecosystem spore available for replication",
    }

    send_to_queue(r, spore_message)
    print("🧬 Systematic development spore shared")

    print("\n📋 HotRod running - checking mail periodically...")
    print("💬 Other agents can now see our spore and capabilities")
    print("📬 Press Ctrl+C to stop\n")

    try:
        cycle = 0
        while True:
            # Check for messages
            messages = check_queue(r, agent_id)

            if messages:
                print(f"\n📬 Found {len(messages)} messages:")
                for msg in messages:
                    sender = msg.get("sender", "unknown")
                    msg_type = msg.get("type", "unknown")
                    content = msg.get("message", str(msg.get("spore_data", "")))[:100]
                    print(f"  📨 {sender}: {msg_type} - {content}...")

            # Show we're alive every 10 cycles
            cycle += 1
            if cycle % 10 == 0:
                queue_length = r.llen("beast_mode_messages")
                print(f"⚙️  HotRod cycle {cycle} - Queue has {queue_length} messages")

            time.sleep(3)  # Check every 3 seconds

    except KeyboardInterrupt:
        print("\n🛑 HotRod shutting down...")

        # Send shutdown notice
        shutdown_msg = {
            "type": "AGENT_SHUTDOWN",
            "sender": agent_id,
            "timestamp": datetime.now().isoformat(),
            "message": "HotRod going offline - systematic collaboration complete",
        }
        send_to_queue(r, shutdown_msg)
        print("👋 HotRod offline")


if __name__ == "__main__":
    main()
