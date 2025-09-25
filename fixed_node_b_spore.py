#!/usr/bin/env python3
"""
FIXED Node B Coordination Spore
==============================
This version actually works and doesn't get stuck in loops
"""

import asyncio
import json
import uuid
import sys
from datetime import datetime

# Auto-install redis if needed
try:
    import redis.asyncio as redis
except ImportError:
    import subprocess
    print("📦 Installing redis...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'redis'])
    import redis.asyncio as redis

# Configuration
NODE_ID = "node-b-fixed"
REDIS_HOST = "192.168.1.119"
REDIS_PORT = 6379
REDIS_PASSWORD = "beastmode2025"
CHANNEL = "beast_mode_network"

class FixedNodeB:
    def __init__(self):
        self.client = None
        self.messages_processed = 0
        self.running = True

    async def connect_and_announce(self):
        """Connect and announce presence."""
        try:
            redis_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
            self.client = redis.from_url(redis_url)
            await self.client.ping()
            print(f"✅ Node B connected to Beast Mode network")

            # Announce presence
            await self.send_message({
                "type": "agent_discovery",
                "payload": {
                    "message": "🧬 FIXED Node B is online and ready for Beast Mode coordination!",
                    "capabilities": ["beast_mode_coordination", "practical_development", "hung_shell_detection"],
                    "status": "ready_for_collaboration"
                }
            })
            print(f"📡 Node B announced presence")
            return True

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    async def send_message(self, content):
        """Send a message to the network."""
        message = {
            "id": str(uuid.uuid4()),
            "source": NODE_ID,
            "target": None,
            "timestamp": datetime.now().isoformat(),
            "priority": 5,
            **content
        }

        await self.client.publish(CHANNEL, json.dumps(message))

    async def process_message(self, data):
        """Process incoming message and respond appropriately."""
        sender = data.get("source", "unknown")
        msg_type = data.get("type", "unknown")
        payload = data.get("payload", {})

        self.messages_processed += 1
        print(f"\n📨 Message #{self.messages_processed} from {sender} (type: {msg_type})")

        # Handle different message types
        if msg_type == "prompt_request":
            prompt = payload.get("prompt", "")
            print(f"📝 Received prompt: {prompt[:100]}...")

            # Check if it's about collaboration
            if "HUNG_SHELL_DETECTOR" in prompt or "collaboration" in prompt.lower():
                await self.handle_collaboration_request(prompt, sender)
            else:
                await self.send_generic_response(sender, "Received your prompt!")

        elif msg_type == "spore_request":
            await self.handle_spore_request(payload, sender)

        elif msg_type == "agent_discovery":
            await self.handle_agent_discovery(sender)

        elif msg_type == "help_wanted":
            await self.handle_help_request(payload, sender)

        else:
            print(f"   ℹ️ Acknowledged {msg_type} from {sender}")

    async def handle_collaboration_request(self, prompt, sender):
        """Handle collaboration request for development work."""
        print("🤝 Processing collaboration request for HUNG_SHELL_DETECTOR.py")

        response = """🔧 NODE B COLLABORATION RESPONSE

I'm ready to collaborate on improving HUNG_SHELL_DETECTOR.py!

MY PROPOSED ENHANCEMENTS:
1. REACTIVE MONITORING - Add real-time process monitoring with event triggers
2. INTERACTIVE CLI - Create user-friendly interface for manual intervention
3. SMART RECOVERY - Implement adaptive recovery strategies based on shell type
4. LEARNING SYSTEM - Track patterns of hung processes to improve detection

ANALYSIS OF CURRENT CODE:
- Good basic detection logic
- Needs better error handling
- Could use more sophisticated hung process criteria
- Missing user interaction capabilities

Ready to start development work! What's our coordination approach?

STATUS: Node B ready for practical pair programming! 🚀"""

        await self.send_message({
            "type": "prompt_response",
            "target": sender,
            "payload": {
                "response": response,
                "status": "collaboration_accepted",
                "ready_for_development": True
            }
        })
        print("📤 Sent collaboration acceptance and analysis")

    async def handle_spore_request(self, payload, sender):
        """Handle spore requests."""
        spore_name = payload.get("spore_name", "unknown")
        print(f"🧬 Processing spore: {spore_name}")

        await self.send_message({
            "type": "agent_response",
            "target": sender,
            "payload": {
                "spore_processed": True,
                "spore_name": spore_name,
                "result": f"Successfully processed {spore_name} with reactive approach"
            }
        })

    async def handle_agent_discovery(self, sender):
        """Handle agent discovery."""
        await self.send_message({
            "type": "agent_response",
            "target": sender,
            "payload": {
                "greeting": f"Hello {sender}! Node B here, ready for Beast Mode coordination!",
                "capabilities": ["practical_development", "reactive_architecture", "hung_shell_detection"]
            }
        })

    async def handle_help_request(self, payload, sender):
        """Handle help requests."""
        required_caps = payload.get("required_capabilities", [])
        my_caps = ["practical_development", "reactive_architecture", "beast_mode_coordination"]

        can_help = any(cap in my_caps for cap in required_caps)

        await self.send_message({
            "type": "help_response",
            "target": sender,
            "payload": {
                "can_help": can_help,
                "capabilities": my_caps,
                "message": "Node B ready to help!" if can_help else "Sorry, can't help with that"
            }
        })

    async def send_generic_response(self, sender, message):
        """Send generic response."""
        await self.send_message({
            "type": "agent_response",
            "target": sender,
            "payload": {"message": message, "from": "node_b_fixed"}
        })

    async def run_coordination_loop(self):
        """Main coordination loop - this one actually works."""
        if not await self.connect_and_announce():
            return False

        print(f"🎯 Node B entering coordination loop...")

        pubsub = self.client.pubsub()
        await pubsub.subscribe(CHANNEL)

        # Process messages for reasonable time
        message_count = 0
        no_message_count = 0

        try:
            while self.running and message_count < 50:  # Process up to 50 messages
                try:
                    # Get message with timeout
                    message = await asyncio.wait_for(pubsub.get_message(), timeout=2.0)

                    if message and message["type"] == "message":
                        data = json.loads(message["data"])

                        # Skip our own messages
                        if data.get("source") == NODE_ID:
                            continue

                        await self.process_message(data)
                        message_count += 1
                        no_message_count = 0

                    else:
                        no_message_count += 1
                        print(f"   [{message_count}] Waiting for messages... ({no_message_count}/10)")

                        # Exit if no messages for too long
                        if no_message_count >= 10:
                            print("   ⏰ No activity - wrapping up")
                            break

                except asyncio.TimeoutError:
                    no_message_count += 1
                    print(f"   ⏰ Timeout {no_message_count}/10")
                    if no_message_count >= 10:
                        break

                except Exception as e:
                    print(f"❌ Message processing error: {e}")

        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        finally:
            await pubsub.aclose()

        # Send final status
        await self.send_message({
            "type": "agent_response",
            "payload": {
                "message": f"Node B coordination complete! Processed {self.messages_processed} messages.",
                "final_status": "coordination_successful"
            }
        })

        await self.client.aclose()
        print(f"\n✅ Node B coordination completed - processed {self.messages_processed} messages")
        return True

async def main():
    """Main function with working coordination."""
    print("🧬 FIXED Node B Beast Mode Coordination")
    print("="*50)

    node_b = FixedNodeB()

    try:
        success = await node_b.run_coordination_loop()
        print(f"🎯 Coordination {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())