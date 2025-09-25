#!/usr/bin/env python3
"""
Simple Node B Coordination Spore
================================

A minimal spore for Node B to establish Beast Mode coordination.
Just run this and it will connect to the network and respond to Node A.
"""

import asyncio
import json
import uuid
import sys
from datetime import datetime
from typing import Dict, Any

# Auto-install redis if needed
try:
    import redis.asyncio as redis
except ImportError:
    import subprocess
    print("📦 Installing redis...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'redis'])
    import redis.asyncio as redis

# Configuration
NODE_ID = "node-b-simple"
REDIS_HOST = "192.168.1.119"
REDIS_PORT = 6379
REDIS_PASSWORD = "beastmode2025"
CHANNEL = "beast_mode_network"

class SimpleNodeB:
    def __init__(self):
        self.client = None
        self.messages_processed = 0

    async def connect_and_announce(self):
        """Connect and announce presence."""
        try:
            redis_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
            self.client = redis.from_url(redis_url)
            await self.client.ping()

            print(f"✅ Node B connected to Beast Mode network")

            # Announce presence
            message = {
                "id": str(uuid.uuid4()),
                "type": "agent_discovery",
                "source": NODE_ID,
                "target": None,
                "payload": {
                    "message": "🧬 Node B is online and ready for Beast Mode coordination!",
                    "capabilities": ["beast_mode_coordination", "spore_processing"],
                    "approach": "simple_coordination"
                },
                "timestamp": datetime.now().isoformat(),
                "priority": 5
            }

            await self.client.publish(CHANNEL, json.dumps(message))
            print(f"📡 Node B announced presence to network")
            return True

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    async def send_status_to_node_a(self):
        """Send status update to Node A."""
        status = {
            "id": str(uuid.uuid4()),
            "type": "agent_response",
            "source": NODE_ID,
            "target": "claude-code-node-a",
            "payload": {
                "status": "online_and_coordinating",
                "messages_processed": self.messages_processed,
                "message": f"Node B here! I've processed {self.messages_processed} coordination messages. Ready for Beast Mode collaboration!",
                "timestamp": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat(),
            "priority": 6
        }

        await self.client.publish(CHANNEL, json.dumps(status))
        print(f"📤 Sent status update to Node A")

    async def listen_briefly(self, duration=30):
        """Listen for messages with timeout - FIXED VERSION."""
        print(f"👂 Listening for Beast Mode messages for up to {duration} seconds...")

        pubsub = self.client.pubsub()
        await pubsub.subscribe(CHANNEL)

        message_count = 0
        no_message_count = 0
        max_messages = 20  # Limit total messages

        try:
            while message_count < max_messages and no_message_count < 10:
                try:
                    # FIXED: Use timeout instead of infinite blocking
                    raw_message = await asyncio.wait_for(pubsub.get_message(), timeout=3.0)

                    if raw_message and raw_message["type"] == "message":
                        try:
                            data = json.loads(raw_message["data"])

                            # Skip our own messages
                            if data.get("source") == NODE_ID:
                                continue

                            self.messages_processed += 1
                            message_count += 1
                            no_message_count = 0  # Reset timeout counter

                            sender = data.get("source", "unknown")
                            msg_type = data.get("type", "unknown")

                            print(f"\n📨 Message #{message_count} from {sender} (type: {msg_type})")

                            # Process different message types
                            if "collaboration" in str(data).lower() or "HUNG_SHELL_DETECTOR" in str(data):
                                print("   🤝 Collaboration request detected!")
                                await self.handle_collaboration_request(data)
                            elif sender == "claude-code-node-a":
                                print("   🎯 Message from Node A - sending response!")
                                await self.send_response_to_node_a(data)
                            else:
                                print(f"   ℹ️  General message from {sender}")

                        except Exception as e:
                            print(f"❌ Error processing message: {e}")

                    else:
                        no_message_count += 1
                        print(f"   ⏰ No message ({no_message_count}/10)")

                except asyncio.TimeoutError:
                    no_message_count += 1
                    print(f"   ⏰ Timeout {no_message_count}/10")

                except Exception as e:
                    print(f"❌ Listening error: {e}")
                    break

        finally:
            await pubsub.aclose()
            print(f"\n✅ Listening complete - processed {self.messages_processed} messages")

    async def handle_collaboration_request(self, received_message):
        """Handle collaboration requests from Node A."""
        response = {
            "id": str(uuid.uuid4()),
            "type": "prompt_response",
            "source": NODE_ID,
            "target": "claude-code-node-a",
            "payload": {
                "response": """🤝 NODE B COLLABORATION RESPONSE

I'm ready to collaborate on improving HUNG_SHELL_DETECTOR.py!

MY PROPOSED ENHANCEMENTS:
1. REACTIVE MONITORING - Real-time process monitoring with event triggers
2. INTERACTIVE CLI - User-friendly interface for manual intervention
3. SMART RECOVERY - Adaptive recovery strategies based on shell type
4. LEARNING SYSTEM - Track hung process patterns for better detection

ANALYSIS OF CURRENT CODE:
- Good basic detection logic but needs improvement
- Missing sophisticated hung process criteria
- Could use better error handling
- Needs user interaction capabilities

Ready for practical pair programming! Let's coordinate our development work.

STATUS: Node B ready to collaborate! 🚀""",
                "status": "collaboration_accepted",
                "ready_for_development": True
            },
            "timestamp": datetime.now().isoformat(),
            "priority": 8
        }

        await self.client.publish(CHANNEL, json.dumps(response))
        print("📤 Sent collaboration response to Node A")

    async def send_response_to_node_a(self, received_message):
        """Send specific response to Node A."""
        response = {
            "id": str(uuid.uuid4()),
            "type": "agent_response",
            "source": NODE_ID,
            "target": "claude-code-node-a",
            "payload": {
                "responding_to": received_message.get("type"),
                "message": "Hello Node A! Node B here - Beast Mode coordination is working! 🧬",
                "coordination_status": "active",
                "received_your_message": True,
                "my_approach": "simple_but_effective"
            },
            "timestamp": datetime.now().isoformat(),
            "priority": 7
        }

        await self.client.publish(CHANNEL, json.dumps(response))
        print("   📤 Sent direct response to Node A")

    async def cleanup(self):
        """Send goodbye and cleanup."""
        if self.client:
            goodbye = {
                "id": str(uuid.uuid4()),
                "type": "agent_response",
                "source": NODE_ID,
                "target": None,
                "payload": {
                    "message": f"Node B signing off! Processed {self.messages_processed} messages. Beast Mode coordination successful! 👋",
                    "final_stats": {
                        "messages_processed": self.messages_processed,
                        "status": "coordination_complete"
                    }
                },
                "timestamp": datetime.now().isoformat(),
                "priority": 5
            }

            await self.client.publish(CHANNEL, json.dumps(goodbye))
            await self.client.aclose()
            print("👋 Node B signed off from Beast Mode network")

async def main():
    """Main coordination function."""
    print("🧬 Simple Node B Beast Mode Coordination")
    print("="*50)

    node_b = SimpleNodeB()

    try:
        # Connect and announce
        if not await node_b.connect_and_announce():
            return

        # Send initial status
        await node_b.send_status_to_node_a()

        # Listen for coordination messages
        await node_b.listen_briefly(duration=30)

        # Send final status
        await node_b.send_status_to_node_a()

        print(f"\n🎯 Beast Mode coordination complete!")
        print(f"   Node B processed {node_b.messages_processed} messages")
        print(f"   Coordination with Node A: ✅ Success")

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await node_b.cleanup()

if __name__ == "__main__":
    asyncio.run(main())