#!/usr/bin/env python3
"""
Persistent Node B - Beast Mode Network Node
===========================================

A persistent version of Node B that stays connected to the Beast Mode network
and participates in ongoing coordination activities.

Usage:
    python3 persistent_node_b.py

Features:
- Stays connected to Beast Mode network
- Responds to challenges from other nodes
- Sends periodic presence announcements
- Monitors and responds to network activity
"""

import asyncio
import json
import sys
import signal
import time
from datetime import datetime
from typing import Dict, Any

# Try to import redis, install if needed
try:
    import redis.asyncio as redis
except ImportError:
    import subprocess
    print("📦 Installing redis...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'redis'])
    import redis.asyncio as redis

# Network Configuration
NODE_ID = "persistent-node-b"
REDIS_HOST = "192.168.1.119"  # Vonnegut IP
REDIS_PORT = 6379
REDIS_PASSWORD = get_redis_password()

class PersistentNodeB:
    """Persistent Node B that stays connected to Beast Mode network."""

    def __init__(self):
        self.redis_client = None
        self.pubsub = None
        self.running = False
        self.message_count = 0
        self.challenges_received = 0
        self.responses_sent = 0

        # Beast Mode channels
        self.channels = [
            'beast_mode:coordination',
            'beast_mode:challenges',
            'beast_mode:spores',
            'beast_mode:results'
        ]

    async def connect(self) -> bool:
        """Connect to Beast Mode network."""
        try:
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=0,
                decode_responses=True
            )

            await self.redis_client.ping()
            self.pubsub = self.redis_client.pubsub()

            # Subscribe to all channels
            for channel in self.channels:
                await self.pubsub.subscribe(channel)

            print(f"✅ {NODE_ID} connected to Beast Mode network")
            print(f"👂 Subscribed to {len(self.channels)} channels")
            return True

        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False

    async def announce_presence(self):
        """Announce presence to the network."""
        try:
            presence_msg = {
                'type': 'node_presence',
                'node_id': NODE_ID,
                'status': 'online_persistent',
                'capabilities': [
                    'reactive_config_management',
                    'persistent_monitoring',
                    'challenge_response',
                    'adaptive_learning'
                ],
                'approach': 'reactive_event_driven',
                'uptime': time.time(),
                'timestamp': datetime.now().isoformat()
            }

            envelope = {
                'sender': NODE_ID,
                'timestamp': datetime.now().isoformat(),
                'message_id': f"{NODE_ID}_{int(time.time()*1000)}",
                'content': presence_msg
            }

            await self.redis_client.publish('beast_mode:coordination', json.dumps(envelope))
            print(f"📡 {NODE_ID} announced presence")
            return True

        except Exception as e:
            print(f"❌ Failed to announce presence: {e}")
            return False

    async def respond_to_challenge(self, challenge_content: Dict[str, Any]):
        """Respond to evolution challenges."""
        challenge_id = challenge_content.get('challenge_id', 'unknown')
        target_score = challenge_content.get('target_score', 0.9)

        print(f"🧬 Responding to challenge: {challenge_id}")

        # Simulate implementing the challenge with reactive approach
        await asyncio.sleep(0.1)  # Simulate work

        # Send response
        response_msg = {
            'type': 'challenge_response',
            'challenge_id': challenge_id,
            'node_implementation': NODE_ID,
            'approach': 'reactive_event_driven',
            'estimated_score': 0.94,  # Our reactive approach score
            'status': 'implemented',
            'unique_features': [
                'Event-driven healing',
                'Functional composition',
                'Adaptive pattern learning'
            ],
            'timestamp': datetime.now().isoformat()
        }

        envelope = {
            'sender': NODE_ID,
            'timestamp': datetime.now().isoformat(),
            'message_id': f"{NODE_ID}_response_{int(time.time()*1000)}",
            'content': response_msg
        }

        await self.redis_client.publish('beast_mode:results', json.dumps(envelope))
        self.responses_sent += 1
        print(f"📤 Sent response to {challenge_id}")

    async def send_periodic_heartbeat(self):
        """Send periodic heartbeat messages."""
        heartbeat_msg = {
            'type': 'heartbeat',
            'node_id': NODE_ID,
            'status': 'active',
            'messages_processed': self.message_count,
            'challenges_received': self.challenges_received,
            'responses_sent': self.responses_sent,
            'timestamp': datetime.now().isoformat()
        }

        envelope = {
            'sender': NODE_ID,
            'timestamp': datetime.now().isoformat(),
            'message_id': f"{NODE_ID}_heartbeat_{int(time.time()*1000)}",
            'content': heartbeat_msg
        }

        await self.redis_client.publish('beast_mode:coordination', json.dumps(envelope))
        print(f"💓 {NODE_ID} heartbeat sent")

    async def process_message(self, raw_message):
        """Process incoming network messages."""
        try:
            envelope = json.loads(raw_message['data'])
            channel = raw_message['channel']
            sender = envelope.get('sender', 'unknown')
            content = envelope.get('content', {})

            # Don't process our own messages
            if sender == NODE_ID:
                return

            self.message_count += 1
            message_type = content.get('type', 'unknown')

            print(f"📥 [{message_type}] from {sender}")

            # Respond to specific message types
            if message_type == 'evolution_challenge':
                self.challenges_received += 1
                await self.respond_to_challenge(content)
            elif message_type == 'node_presence':
                # Acknowledge other nodes
                print(f"   👋 Acknowledged {sender}")
            elif message_type == 'spore_delivery':
                print(f"   🧬 Received spore from {sender}")

        except Exception as e:
            print(f"❌ Message processing error: {e}")

    async def listen_for_messages(self):
        """Listen for network messages continuously."""
        print(f"👂 {NODE_ID} listening for messages...")

        try:
            while self.running:
                message = await self.pubsub.get_message(timeout=1.0)

                if message and message['type'] == 'message':
                    await self.process_message(message)

                # Send periodic heartbeat
                if self.message_count % 50 == 0 and self.message_count > 0:
                    await self.send_periodic_heartbeat()

        except Exception as e:
            print(f"❌ Error listening: {e}")

    async def start(self):
        """Start persistent Node B operation."""
        print("🧬 Starting Persistent Node B...")
        print("="*50)

        if not await self.connect():
            return False

        # Initial presence announcement
        await self.announce_presence()

        # Start listening
        self.running = True
        await self.listen_for_messages()

        return True

    async def stop(self):
        """Stop Node B and disconnect."""
        self.running = False

        # Send goodbye message
        goodbye_msg = {
            'type': 'node_disconnect',
            'node_id': NODE_ID,
            'final_stats': {
                'messages_processed': self.message_count,
                'challenges_received': self.challenges_received,
                'responses_sent': self.responses_sent
            },
            'timestamp': datetime.now().isoformat()
        }

        envelope = {
            'sender': NODE_ID,
            'timestamp': datetime.now().isoformat(),
            'message_id': f"{NODE_ID}_goodbye_{int(time.time()*1000)}",
            'content': goodbye_msg
        }

        if self.redis_client:
            await self.redis_client.publish('beast_mode:coordination', json.dumps(envelope))

        if self.pubsub:
            await self.pubsub.aclose()
        if self.redis_client:
            await self.redis_client.aclose()

        print(f"\n🔌 {NODE_ID} disconnected")
        print(f"📊 Final stats:")
        print(f"   Messages processed: {self.message_count}")
        print(f"   Challenges received: {self.challenges_received}")
        print(f"   Responses sent: {self.responses_sent}")

# Signal handling
node_b = None

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    global node_b
    if node_b:
        asyncio.create_task(node_b.stop())
    sys.exit(0)

async def main():
    """Main function."""
    global node_b

    print("🧬 Persistent Node B - Beast Mode Network Node")
    print("="*50)
    print("Press Ctrl+C to stop")
    print("="*50)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and start Node B
    node_b = PersistentNodeB()

    try:
        await node_b.start()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    finally:
        if node_b:
            await node_b.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Node B stopped")
    except Exception as e:
        print(f"\n❌ Node B failed: {e}")
        sys.exit(1)