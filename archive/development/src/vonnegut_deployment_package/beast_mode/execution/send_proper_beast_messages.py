#!/usr/bin/env python3
"""
Send messages to the proper Beast Mode channels that agents are listening to
"""

import redis
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, Any


def send_to_proper_channels():
    """Send messages to the channels Beast Mode agents actually monitor"""
    print("📡 **SENDING TO PROPER BEAST MODE CHANNELS**")
    print("=" * 50)

    r = redis.Redis(host="localhost", port=6379, db=0)

    # Test messages for different channels
    test_messages = [
        {
            "channel": "beast_mode_general",
            "message": {
                "message_type": "GENERAL_INQUIRY",
                "sender_id": "human_team",
                "timestamp": datetime.now().isoformat(),
                "subject": "Network Status Check",
                "content": {
                    "message": "Hello Beast Mode agents! This is the human team checking network status.",
                    "request": "Please respond if you can see this message",
                },
            },
        },
        {
            "channel": "help_requests",
            "message": {
                "message_type": "HELP_REQUEST",
                "sender_id": "human_team",
                "timestamp": datetime.now().isoformat(),
                "subject": "General Network Help",
                "content": {
                    "description": "We need help understanding the current network status and agent availability",
                    "priority": "normal",
                    "capabilities_required": [],
                },
            },
        },
        {
            "channel": "beast_mode_heartbeats",
            "message": {
                "message_type": "HEARTBEAT_REQUEST",
                "sender_id": "human_team",
                "timestamp": datetime.now().isoformat(),
                "subject": "Requesting Agent Heartbeats",
                "content": {
                    "message": "Human team requesting status updates from all active agents",
                    "request_type": "status_check",
                },
            },
        },
    ]

    # Send messages to each channel
    for test in test_messages:
        channel = test["channel"]
        message = test["message"]

        try:
            result = r.publish(channel, json.dumps(message))
            print(f"📤 Sent to '{channel}' - {result} subscribers received it")

            if result > 0:
                print(f"  ✅ Message delivered to {result} agent(s)")
                print(f"  📝 Message type: {message['message_type']}")
            else:
                print(f"  ⚠️  No subscribers on this channel")

        except Exception as e:
            print(f"  ❌ Error sending to '{channel}': {e}")

        print()  # Empty line for readability
        time.sleep(1)  # Brief pause between messages

    # Also try direct messages to known agent IDs
    known_agent_ids = [
        "cost_optimizer_001",
        "deployment_specialist_001",
        "code_mentor_001",
        "tidb_agent",
        "beast_mode_orchestrator",
    ]

    print("📬 **TRYING DIRECT MESSAGES TO KNOWN AGENTS**")

    for agent_id in known_agent_ids:
        direct_channel = f"direct_{agent_id}"
        direct_message = {
            "message_type": "DIRECT_INQUIRY",
            "sender_id": "human_team",
            "timestamp": datetime.now().isoformat(),
            "subject": f"Direct message to {agent_id}",
            "content": {
                "message": f"Hello {agent_id}! Are you active and receiving messages?",
                "request": "Please respond with your current status",
            },
        }

        try:
            result = r.publish(direct_channel, json.dumps(direct_message))
            if result > 0:
                print(f"  📤 {agent_id}: {result} subscriber(s)")
            else:
                print(f"  ⚪ {agent_id}: no subscribers")

        except Exception as e:
            print(f"  ❌ {agent_id}: error - {e}")

    print(f"\n💡 **RECOMMENDATIONS**")
    print(f"  • If agents are running, they should respond to help_requests")
    print(f"  • Check if agents are using different Redis databases")
    print(f"  • Verify agent processes are actually running")
    print(f"  • Look for agent logs to see if they're receiving messages")


if __name__ == "__main__":
    send_to_proper_channels()
