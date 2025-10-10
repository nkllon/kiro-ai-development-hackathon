#!/usr/bin/env python3
"""
Node B Spore Using Existing Beast Mode Infrastructure
====================================================

Uses the existing BeastModeBusClient and messaging infrastructure
that's already built into the repo.

This demonstrates the conversational mailbox pattern using
the established Beast Mode framework components.
"""

import asyncio
import sys
from pathlib import Path

from src.security.secure_credentials import get_redis_password
from typing import Dict, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from beast_mode.messaging import BeastModeBusClient, BeastModeMessage, MessageType
    print("✅ Using existing Beast Mode messaging infrastructure")
except ImportError as e:
    print(f"❌ Could not import Beast Mode infrastructure: {e}")
    print("   The existing messaging system may need to be available")
    sys.exit(1)

# Node Configuration
NODE_ID = "existing-infrastructure-node-b"
REDIS_HOST = "192.168.1.119"  # Vonnegut
REDIS_PORT = 6379
REDIS_PASSWORD = get_redis_password()

class ConversationalNodeB:
    """Node B using existing Beast Mode infrastructure."""

    def __init__(self):
        # Use existing BeastModeBusClient
        redis_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"

        self.client = BeastModeBusClient(
            agent_id=NODE_ID,
            capabilities=[
                "reactive_config_management",
                "conversational_processing",
                "beast_mode_coordination",
                "mailbox_pattern_messaging"
            ],
            redis_url=redis_url
        )

        self.conversation_history = []
        self.challenges_completed = 0
        self.running = False

    async def start(self) -> bool:
        """Start the conversational node."""
        print("🧬 Starting Node B with Existing Infrastructure")
        print("="*60)

        # Connect using existing client
        connected = await self.client.connect()
        if not connected:
            print("❌ Failed to connect to Beast Mode network")
            return False

        print(f"✅ {NODE_ID} connected to Beast Mode network")

        # Announce presence using existing method
        await self.client.announce_presence()
        print(f"📡 Announced presence with capabilities: {self.client.capabilities}")

        self.running = True
        return True

    async def run_conversational_loop(self, max_iterations: int = 50):
        """Run conversational loop using existing infrastructure."""
        print(f"\n🗣️  Starting conversational loop...")
        print("   Using existing BeastModeBusClient mailbox pattern")

        for i in range(max_iterations):
            if not self.running:
                break

            # Use existing client's message checking (non-blocking)
            messages = await self._check_mail_non_blocking()

            if messages:
                print(f"   [{i+1}] Processing {len(messages)} messages...")
                for message in messages:
                    await self._process_message_conversationally(message)
            else:
                print(f"   [{i+1}] No messages - IDE stays responsive")

            # Simulate IDE being available for other work
            await asyncio.sleep(2)

            # Periodic status
            if (i + 1) % 20 == 0:
                await self._send_status_update()

        print(f"\n✅ Conversational loop completed")

    async def _check_mail_non_blocking(self) -> list[BeastModeMessage]:
        """Check for messages using existing infrastructure (non-blocking)."""
        # The existing BeastModeBusClient likely has message queuing built-in
        # We'll collect messages that arrived, then clear the queue

        collected_messages = []

        # Set up temporary message collector
        def collect_message(message: BeastModeMessage):
            collected_messages.append(message)

        # Brief non-blocking listen
        try:
            # Start listener briefly to collect any pending messages
            listen_task = asyncio.create_task(
                self.client.listen_for_messages(collect_message)
            )

            # Very brief wait to collect messages
            await asyncio.sleep(0.1)

            # Stop listening
            self.client.is_listening = False
            listen_task.cancel()

        except Exception as e:
            print(f"   ⚠️ Mail check error: {e}")

        return collected_messages

    async def _process_message_conversationally(self, message: BeastModeMessage):
        """Process message like conversational input."""
        print(f"\n📨 Processing: {message.type} from {message.source}")

        # Add to conversation history (like LLM context)
        self.conversation_history.append({
            'input_message': {
                'type': message.type.value,
                'source': message.source,
                'payload': message.payload
            },
            'timestamp': message.timestamp
        })

        # Generate conversational response based on message type
        response = await self._generate_conversational_response(message)

        if response:
            # Send response using existing client
            await self.client.send_message(response)
            print(f"   📤 Sent response: {response.type}")

        # Track conversation
        self.conversation_history.append({
            'output_message': response.model_dump() if response else None,
            'timestamp': message.timestamp
        })

    async def _generate_conversational_response(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Generate response like LLM processing input."""

        if message.type == MessageType.AGENT_DISCOVERY:
            # Respond to agent discovery
            return BeastModeMessage(
                type=MessageType.AGENT_RESPONSE,
                source=NODE_ID,
                target=message.source,
                payload={
                    "agent_info": {
                        "capabilities": self.client.capabilities,
                        "approach": "existing_infrastructure_based",
                        "conversation_history_size": len(self.conversation_history)
                    },
                    "greeting": f"Hello {message.source}! I'm Node B using existing Beast Mode infrastructure."
                }
            )

        elif message.type == MessageType.HELP_WANTED:
            # Respond to help requests
            required_caps = message.payload.get('required_capabilities', [])
            my_caps = set(self.client.capabilities)
            can_help = any(cap in my_caps for cap in required_caps)

            if can_help:
                return BeastModeMessage(
                    type=MessageType.HELP_RESPONSE,
                    source=NODE_ID,
                    target=message.source,
                    payload={
                        "can_help": True,
                        "matching_capabilities": [cap for cap in required_caps if cap in my_caps],
                        "approach": "conversational_processing_with_existing_infrastructure",
                        "conversation_context": len(self.conversation_history)
                    }
                )

        elif message.type == MessageType.SPORE_REQUEST:
            # Handle spore requests
            self.challenges_completed += 1
            return BeastModeMessage(
                type=MessageType.AGENT_RESPONSE,
                source=NODE_ID,
                target=message.source,
                payload={
                    "spore_processed": True,
                    "spore_name": message.payload.get('spore_name', 'unknown'),
                    "implementation_approach": "existing_beast_mode_client",
                    "challenges_completed": self.challenges_completed,
                    "estimated_score": 0.93  # Our existing infrastructure approach
                }
            )

        # Default acknowledgment for other message types
        return BeastModeMessage(
            type=MessageType.AGENT_RESPONSE,
            source=NODE_ID,
            target=message.source,
            payload={
                "acknowledged": message.type.value,
                "conversation_turn": len(self.conversation_history),
                "using_infrastructure": "BeastModeBusClient"
            }
        )

    async def _send_status_update(self):
        """Send periodic status using existing client."""
        health = self.client.get_health_status()

        status_message = BeastModeMessage(
            type=MessageType.SYSTEM_HEALTH,
            source=NODE_ID,
            payload={
                "status": "active_conversational",
                "infrastructure": "existing_beast_mode_messaging",
                "conversation_history_size": len(self.conversation_history),
                "challenges_completed": self.challenges_completed,
                "client_health": health,
                "approach": "non_blocking_mailbox_with_existing_client"
            }
        )

        await self.client.send_message(status_message)
        print(f"\n📊 Status update sent - {len(self.conversation_history)} conversations")

    async def stop(self):
        """Stop using existing client."""
        self.running = False

        # Send goodbye using existing method
        await self.client.send_simple_message(
            f"Node B ({NODE_ID}) signing off! Completed {self.challenges_completed} challenges "
            f"with {len(self.conversation_history)} conversational turns using existing Beast Mode infrastructure.",
            target=None  # Broadcast
        )

        # Disconnect using existing method
        await self.client.disconnect()
        print(f"\n👋 {NODE_ID} stopped gracefully using existing infrastructure")

async def main():
    """Main function using existing Beast Mode infrastructure."""
    print("🧬 Node B with Existing Beast Mode Infrastructure")
    print("="*60)
    print("Leveraging BeastModeBusClient and messaging framework")
    print("="*60)

    node_b = ConversationalNodeB()

    try:
        if await node_b.start():
            await node_b.run_conversational_loop(max_iterations=100)
        else:
            print("❌ Failed to start Node B")

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await node_b.stop()

if __name__ == "__main__":
    asyncio.run(main())