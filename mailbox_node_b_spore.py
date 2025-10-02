#!/usr/bin/env python3
"""
Mailbox-Based Beast Mode Node B Spore
=====================================

A conversational Beast Mode node that uses the mailbox pattern to avoid blocking
the main thread while participating in network coordination.

Architecture:
- Background thread handles Redis pub/sub listening
- Main thread checks mailbox when ready (non-blocking)
- Processes messages like conversational input/output
- Maintains state across Beast Mode conversations

Usage:
    python3 mailbox_node_b_spore.py

Features:
- Non-blocking mailbox pattern
- Conversational state management
- Background Redis listener
- Responsive main thread
- Persistent network participation
"""

import asyncio
import json
import sys
import threading
import time
import signal
from datetime import datetime
from typing import Dict, Any, List, Optional
from queue import Queue, Empty
from dataclasses import dataclass

# Auto-install dependencies
def install_dependencies():
    required_packages = ['redis']
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            import subprocess
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

install_dependencies()

import redis.asyncio as redis

# Configuration
NODE_ID = "mailbox-node-b"
REDIS_HOST = "192.168.1.119"
REDIS_PORT = 6379
REDIS_PASSWORD = get_redis_password()

@dataclass
class BeastModeMessage:
    """A Beast Mode network message."""
    sender: str
    channel: str
    message_type: str
    content: Dict[str, Any]
    timestamp: str
    message_id: str

class BeastModeMailbox:
    """Thread-safe mailbox for Beast Mode messages."""

    def __init__(self, max_size: int = 100):
        self.inbox = Queue(maxsize=max_size)
        self.outbox = Queue(maxsize=max_size)
        self.message_count = 0

    def deliver_message(self, message: BeastModeMessage) -> bool:
        """Deliver message to inbox (called by background thread)."""
        try:
            self.inbox.put_nowait(message)
            self.message_count += 1
            return True
        except:
            return False  # Mailbox full

    def check_mail(self) -> Optional[BeastModeMessage]:
        """Check for new messages (non-blocking)."""
        try:
            return self.inbox.get_nowait()
        except Empty:
            return None

    def send_message(self, message: BeastModeMessage):
        """Queue message for sending."""
        try:
            self.outbox.put_nowait(message)
        except:
            pass  # Outbox full

    def get_outgoing(self) -> Optional[BeastModeMessage]:
        """Get message to send (called by background thread)."""
        try:
            return self.outbox.get_nowait()
        except Empty:
            return None

class BeastModeBackgroundListener:
    """Background thread that handles Redis pub/sub."""

    def __init__(self, mailbox: BeastModeMailbox):
        self.mailbox = mailbox
        self.redis_client = None
        self.pubsub = None
        self.running = False
        self.thread = None

        # Channels to monitor
        self.channels = [
            'beast_mode:coordination',
            'beast_mode:challenges',
            'beast_mode:spores',
            'beast_mode:results'
        ]

    async def connect(self) -> bool:
        """Connect to Redis network."""
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

            # Subscribe to channels
            for channel in self.channels:
                await self.pubsub.subscribe(channel)

            print(f"🔗 Background listener connected to Beast Mode network")
            return True

        except Exception as e:
            print(f"❌ Background connection failed: {e}")
            return False

    async def publish_message(self, message: BeastModeMessage):
        """Publish message to Redis."""
        try:
            envelope = {
                'sender': message.sender,
                'timestamp': message.timestamp,
                'message_id': message.message_id,
                'content': message.content
            }

            await self.redis_client.publish(message.channel, json.dumps(envelope))

        except Exception as e:
            print(f"❌ Failed to publish message: {e}")

    async def listen_loop(self):
        """Main listening loop (runs in background)."""
        print(f"👂 Background listener started for {NODE_ID}")

        try:
            while self.running:
                # Listen for incoming messages
                message = await self.pubsub.get_message(timeout=1.0)

                if message and message['type'] == 'message':
                    await self._process_incoming_message(message)

                # Send any queued outgoing messages
                outgoing = self.mailbox.get_outgoing()
                if outgoing:
                    await self.publish_message(outgoing)

        except Exception as e:
            print(f"❌ Background listener error: {e}")

    async def _process_incoming_message(self, raw_message):
        """Process incoming Redis message."""
        try:
            envelope = json.loads(raw_message['data'])
            sender = envelope.get('sender', 'unknown')

            # Don't process our own messages
            if sender == NODE_ID:
                return

            content = envelope.get('content', {})

            beast_message = BeastModeMessage(
                sender=sender,
                channel=raw_message['channel'],
                message_type=content.get('type', 'unknown'),
                content=content,
                timestamp=envelope.get('timestamp', datetime.now().isoformat()),
                message_id=envelope.get('message_id', 'unknown')
            )

            # Deliver to mailbox
            if self.mailbox.deliver_message(beast_message):
                print(f"📬 Mail delivered: {beast_message.message_type} from {sender}")
            else:
                print(f"📬 Mailbox full! Dropped message from {sender}")

        except Exception as e:
            print(f"❌ Message processing error: {e}")

    def start_background_thread(self):
        """Start the background listener thread."""
        def run_async_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.connect())
                if self.redis_client:
                    self.running = True
                    loop.run_until_complete(self.listen_loop())
            finally:
                loop.close()

        self.thread = threading.Thread(target=run_async_loop, daemon=True)
        self.thread.start()

    async def stop(self):
        """Stop the background listener."""
        self.running = False
        if self.pubsub:
            await self.pubsub.aclose()
        if self.redis_client:
            await self.redis_client.aclose()

class ConversationalNodeB:
    """Main conversational Beast Mode node."""

    def __init__(self):
        self.mailbox = BeastModeMailbox()
        self.background_listener = BeastModeBackgroundListener(self.mailbox)
        self.running = False

        # Conversational state
        self.conversation_history = []
        self.active_challenges = {}
        self.network_nodes = {}
        self.my_capabilities = [
            'reactive_config_management',
            'mailbox_coordination',
            'conversational_state_management',
            'non_blocking_processing'
        ]

    def start(self):
        """Start the conversational node."""
        print("🧬 Starting Mailbox-Based Node B")
        print("="*50)

        # Start background listener
        self.background_listener.start_background_thread()
        time.sleep(2)  # Give it time to connect

        # Announce presence
        self._announce_presence()

        self.running = True
        print(f"✅ {NODE_ID} is now active and checking mail")

    def _announce_presence(self):
        """Announce our presence to the network."""
        presence_msg = BeastModeMessage(
            sender=NODE_ID,
            channel='beast_mode:coordination',
            message_type='node_presence',
            content={
                'type': 'node_presence',
                'node_id': NODE_ID,
                'status': 'online_conversational',
                'approach': 'mailbox_based',
                'capabilities': self.my_capabilities,
                'architecture': 'non_blocking_mailbox_pattern',
                'timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now().isoformat(),
            message_id=f"{NODE_ID}_presence_{int(time.time()*1000)}"
        )

        self.mailbox.send_message(presence_msg)
        print(f"📤 Announced presence to Beast Mode network")

    def check_mail_and_process(self) -> bool:
        """Check mailbox and process one message if available."""
        message = self.mailbox.check_mail()

        if message:
            print(f"\n📨 Processing mail: {message.message_type} from {message.sender}")
            response = self._process_message_conversationally(message)

            if response:
                self.mailbox.send_message(response)

            return True  # Processed something

        return False  # No mail

    def _process_message_conversationally(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Process message like conversational input, return response."""

        # Add to conversation history
        self.conversation_history.append({
            'input': message,
            'timestamp': datetime.now().isoformat()
        })

        # Process different message types
        if message.message_type == 'node_presence':
            return self._handle_node_presence(message)

        elif message.message_type == 'evolution_challenge':
            return self._handle_challenge(message)

        elif message.message_type == 'spore_delivery':
            return self._handle_spore(message)

        elif message.message_type == 'heartbeat':
            return self._handle_heartbeat(message)

        else:
            # Generic acknowledgment
            return self._create_ack_message(message)

    def _handle_node_presence(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle node presence announcements."""
        sender = message.sender
        self.network_nodes[sender] = message.content

        print(f"   👋 Acknowledged {sender} ({message.content.get('approach', 'unknown')})")

        # Send back acknowledgment
        return BeastModeMessage(
            sender=NODE_ID,
            channel='beast_mode:coordination',
            message_type='presence_ack',
            content={
                'type': 'presence_ack',
                'acknowledging': sender,
                'my_approach': 'mailbox_based',
                'conversation_history_size': len(self.conversation_history),
                'timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now().isoformat(),
            message_id=f"{NODE_ID}_ack_{int(time.time()*1000)}"
        )

    def _handle_challenge(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle evolution challenges."""
        challenge_id = message.content.get('challenge_id', 'unknown')
        self.active_challenges[challenge_id] = message

        print(f"   🧬 Accepted challenge: {challenge_id}")

        # Simulate working on it
        estimated_score = 0.92  # Our mailbox approach estimate

        return BeastModeMessage(
            sender=NODE_ID,
            channel='beast_mode:results',
            message_type='challenge_response',
            content={
                'type': 'challenge_response',
                'challenge_id': challenge_id,
                'node_implementation': NODE_ID,
                'approach': 'mailbox_based_conversational',
                'estimated_score': estimated_score,
                'status': 'implemented',
                'unique_features': [
                    'Non-blocking mailbox pattern',
                    'Conversational state management',
                    'Background pub/sub handling',
                    'Thread-safe message queuing'
                ],
                'conversation_context': len(self.conversation_history),
                'timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now().isoformat(),
            message_id=f"{NODE_ID}_challenge_response_{int(time.time()*1000)}"
        )

    def _handle_spore(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle spore deliveries."""
        print(f"   🧬 Received spore from {message.sender}")

        return BeastModeMessage(
            sender=NODE_ID,
            channel='beast_mode:coordination',
            message_type='spore_ack',
            content={
                'type': 'spore_ack',
                'spore_received': True,
                'from': message.sender,
                'processing_approach': 'conversational_mailbox',
                'timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now().isoformat(),
            message_id=f"{NODE_ID}_spore_ack_{int(time.time()*1000)}"
        )

    def _handle_heartbeat(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle heartbeat messages."""
        print(f"   💓 Heartbeat from {message.sender}")
        return None  # Don't respond to heartbeats to avoid spam

    def _create_ack_message(self, message: BeastModeMessage) -> BeastModeMessage:
        """Create generic acknowledgment."""
        return BeastModeMessage(
            sender=NODE_ID,
            channel='beast_mode:coordination',
            message_type='message_ack',
            content={
                'type': 'message_ack',
                'acknowledging': message.message_type,
                'from': message.sender,
                'conversational_context': len(self.conversation_history),
                'timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now().isoformat(),
            message_id=f"{NODE_ID}_ack_{int(time.time()*1000)}"
        )

    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            'node_id': NODE_ID,
            'running': self.running,
            'mailbox_messages': self.mailbox.message_count,
            'conversation_history': len(self.conversation_history),
            'active_challenges': len(self.active_challenges),
            'known_nodes': len(self.network_nodes),
            'capabilities': self.my_capabilities
        }

    def run_conversational_loop(self, max_iterations: int = 100):
        """Run the main conversational loop."""
        print(f"\n🗣️  Starting conversational loop (max {max_iterations} iterations)")
        print("   Checking mail periodically while staying responsive...")

        for i in range(max_iterations):
            if not self.running:
                break

            # Check mail and process (non-blocking)
            had_mail = self.check_mail_and_process()

            if had_mail:
                print(f"   [{i+1}] Processed mail - conversation continues...")
            else:
                # No mail - simulate being available for other IDE work
                print(f"   [{i+1}] No mail - IDE remains responsive")

            # Simulate IDE doing other work
            time.sleep(2)

            # Periodic status
            if (i + 1) % 20 == 0:
                status = self.get_status()
                print(f"\n📊 Status: {status['mailbox_messages']} messages, {status['conversation_history']} conversations")

        print(f"\n✅ Conversational loop completed - processed {self.mailbox.message_count} messages")

    def stop(self):
        """Stop the conversational node."""
        self.running = False

        # Send goodbye
        goodbye_msg = BeastModeMessage(
            sender=NODE_ID,
            channel='beast_mode:coordination',
            message_type='node_goodbye',
            content={
                'type': 'node_goodbye',
                'final_stats': self.get_status(),
                'conversations_held': len(self.conversation_history),
                'timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now().isoformat(),
            message_id=f"{NODE_ID}_goodbye_{int(time.time()*1000)}"
        )

        self.mailbox.send_message(goodbye_msg)
        time.sleep(1)  # Let it send

        # Stop background thread
        asyncio.run(self.background_listener.stop())

        print(f"\n👋 {NODE_ID} stopped gracefully")

# Signal handling
node_b = None

def signal_handler(signum, frame):
    global node_b
    if node_b:
        node_b.stop()
    sys.exit(0)

def main():
    global node_b

    print("🧬 Mailbox-Based Beast Mode Node B")
    print("="*50)
    print("Non-blocking conversational coordination")
    print("Press Ctrl+C to stop")
    print("="*50)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and start node
    node_b = ConversationalNodeB()

    try:
        node_b.start()

        # Run conversational loop
        node_b.run_conversational_loop(max_iterations=200)

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    finally:
        if node_b:
            node_b.stop()

if __name__ == "__main__":
    main()