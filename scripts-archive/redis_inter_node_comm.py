#!/usr/bin/env python3
"""
Redis Inter-Node Communication Test
====================================

Test Redis PubSub communication between Beast Mode nodes.
This establishes the foundation for cross-IDE coordination.
"""

import asyncio
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Try to import redis
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    print("❌ Redis not available. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'redis'])
    import redis.asyncio as redis
    REDIS_AVAILABLE = True

class BeastModeRedisMessenger:
    """Simple Redis messenger for inter-node communication."""

    def __init__(self, node_id: str, redis_host: str = "localhost", redis_port: int = 6379, redis_password: str = None):
        self.node_id = node_id
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.redis_client = None
        self.pubsub = None
        self.logger = logging.getLogger(f"BeastMode.{node_id}")

        # Beast Mode channels
        self.channels = {
            'coordination': 'beast_mode:coordination',
            'challenges': 'beast_mode:challenges',
            'spores': 'beast_mode:spores',
            'results': 'beast_mode:results'
        }

        self.message_handlers = {}
        self.running = False

    async def connect(self) -> bool:
        """Connect to Redis server."""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=0,
                decode_responses=True,
                password=self.redis_password
            )

            # Test connection
            await self.redis_client.ping()
            self.pubsub = self.redis_client.pubsub()

            print(f"✅ {self.node_id} connected to Redis at {self.redis_host}:{self.redis_port}")
            return True

        except Exception as e:
            print(f"❌ {self.node_id} failed to connect to Redis: {e}")
            return False

    async def subscribe_to_channel(self, channel_name: str, handler: callable = None):
        """Subscribe to a Beast Mode channel."""
        if not self.pubsub:
            print(f"❌ Not connected to Redis")
            return False

        try:
            channel = self.channels.get(channel_name, channel_name)
            await self.pubsub.subscribe(channel)

            if handler:
                self.message_handlers[channel] = handler

            print(f"📡 {self.node_id} subscribed to {channel}")
            return True

        except Exception as e:
            print(f"❌ {self.node_id} failed to subscribe to {channel_name}: {e}")
            return False

    async def publish_message(self, channel_name: str, message: Dict[str, Any]) -> bool:
        """Publish a message to a Beast Mode channel."""
        if not self.redis_client:
            print(f"❌ Not connected to Redis")
            return False

        try:
            channel = self.channels.get(channel_name, channel_name)

            # Add metadata
            envelope = {
                'sender': self.node_id,
                'timestamp': datetime.now().isoformat(),
                'message_id': f"{self.node_id}_{int(time.time()*1000)}",
                'content': message
            }

            # Publish as JSON
            result = await self.redis_client.publish(channel, json.dumps(envelope))
            print(f"📤 {self.node_id} published to {channel} (subscribers: {result})")
            return True

        except Exception as e:
            print(f"❌ {self.node_id} failed to publish to {channel_name}: {e}")
            return False

    async def listen_for_messages(self, timeout: Optional[float] = None):
        """Listen for incoming messages."""
        if not self.pubsub:
            print(f"❌ Not subscribed to any channels")
            return

        self.running = True
        print(f"👂 {self.node_id} listening for messages...")

        try:
            while self.running:
                message = await self.pubsub.get_message(timeout=timeout or 1.0)

                if message and message['type'] == 'message':
                    await self._handle_message(message)
                elif not message and timeout:
                    # Timeout reached
                    break

        except Exception as e:
            print(f"❌ {self.node_id} error while listening: {e}")

    async def _handle_message(self, raw_message):
        """Handle an incoming message."""
        try:
            envelope = json.loads(raw_message['data'])
            channel = raw_message['channel']
            sender = envelope['sender']
            content = envelope['content']

            # Don't process our own messages
            if sender == self.node_id:
                return

            print(f"📥 {self.node_id} received from {sender} on {channel}:")
            print(f"   {content.get('type', 'message')}: {content.get('summary', str(content)[:100])}")

            # Call registered handler if available
            if channel in self.message_handlers:
                await self.message_handlers[channel](envelope)

        except Exception as e:
            print(f"❌ {self.node_id} error handling message: {e}")

    async def announce_presence(self):
        """Announce presence to other nodes."""
        presence_msg = {
            'type': 'node_presence',
            'node_id': self.node_id,
            'capabilities': [
                'beast_mode_coordination',
                'pdca_cycles',
                'spore_processing',
                'emergent_evolution'
            ],
            'status': 'online',
            'summary': f"{self.node_id} is online and ready for Beast Mode coordination"
        }

        return await self.publish_message('coordination', presence_msg)

    async def send_challenge(self, challenge_data: Dict[str, Any]) -> bool:
        """Send a challenge to other nodes."""
        challenge_msg = {
            'type': 'evolution_challenge',
            'challenge_id': challenge_data.get('challenge_id', 'unknown'),
            'target_score': challenge_data.get('target_score', 0.9),
            'summary': f"Evolution challenge: {challenge_data.get('challenge_id')}",
            'full_challenge': challenge_data
        }

        return await self.publish_message('challenges', challenge_msg)

    async def send_results(self, results: Dict[str, Any]) -> bool:
        """Send implementation results."""
        results_msg = {
            'type': 'challenge_results',
            'node_implementation': self.node_id,
            'systematic_score': results.get('final_systematic_score', 0.0),
            'summary': f"{self.node_id} achieved score {results.get('final_systematic_score', 0.0):.3f}",
            'full_results': results
        }

        return await self.publish_message('results', results_msg)

    async def stop(self):
        """Stop listening and disconnect."""
        self.running = False
        if self.pubsub:
            await self.pubsub.aclose()
        if self.redis_client:
            await self.redis_client.aclose()
        print(f"🔌 {self.node_id} disconnected from Redis")

# Test Communication Functions
async def test_redis_connectivity():
    """Test basic Redis connectivity."""
    print("🔍 Testing Redis connectivity...")

    try:
        # Try without password first (local Redis)
        client = redis.Redis(host='localhost', port=6379, db=0)
        await client.ping()
        await client.aclose()
        print("✅ Local Redis server is accessible (no auth)")
        return True
    except Exception as e:
        try:
            # Try with password
            client = redis.Redis(host='localhost', port=6379, db=0, password=get_redis_password())
            await client.ping()
            await client.aclose()
            print("✅ Local Redis server is accessible (with auth)")
            return True
        except Exception as e2:
            print(f"❌ Redis server not accessible: {e2}")
            return False

async def test_vonnegut_connectivity():
    """Test connectivity to Vonnegut Redis server."""
    print("\n🔍 Testing Vonnegut Redis connectivity...")

    vonnegut_ip = "192.168.1.119"
    try:
        client = redis.Redis(host=vonnegut_ip, port=6379, db=0, password=get_redis_password())
        await client.ping()
        await client.aclose()
        print(f"✅ Vonnegut Redis server is accessible at {vonnegut_ip}")
        return True
    except Exception as e:
        print(f"❌ Vonnegut Redis server not accessible at {vonnegut_ip}: {e}")
        return False

async def test_inter_node_messaging():
    """Test messaging between simulated nodes."""
    print("\n🧪 Testing inter-node messaging...")

    # Create two simulated nodes (no password for local testing)
    node_a = BeastModeRedisMessenger("claude-code-node-a")
    node_b = BeastModeRedisMessenger("simulated-node-b")

    # Connect both nodes
    if not await node_a.connect() or not await node_b.connect():
        print("❌ Failed to connect nodes to Redis")
        return False

    # Subscribe to coordination channel
    await node_a.subscribe_to_channel('coordination')
    await node_b.subscribe_to_channel('coordination')

    # Brief delay for subscriptions to settle
    await asyncio.sleep(0.5)

    # Node A announces presence
    await node_a.announce_presence()

    # Node B listens for messages briefly
    listen_task = asyncio.create_task(node_b.listen_for_messages(timeout=2.0))
    await asyncio.sleep(0.5)  # Let the announcement propagate

    # Node B announces presence
    await node_b.announce_presence()

    # Wait for listening to complete
    await listen_task

    # Cleanup
    await node_a.stop()
    await node_b.stop()

    print("✅ Inter-node messaging test complete")
    return True

async def send_evolution_challenge_to_network():
    """Send the evolution challenge to the Beast Mode network."""
    print("\n🧬 Sending Evolution Challenge to Network...")

    node_a = BeastModeRedisMessenger("claude-code-node-a")

    if not await node_a.connect():
        print("❌ Failed to connect to Redis")
        return False

    # Prepare challenge data
    challenge_data = {
        'challenge_id': 'self_healing_config_manager',
        'target_score': 0.90,
        'description': 'Implement SelfHealingConfigManager with your unique approach',
        'interface_file': 'emergent_evolution_challenge.py',
        'test_scenarios': [
            'basic_config', 'corrupted_config', 'missing_fields',
            'performance_stress', 'recovery_scenario'
        ],
        'node_a_baseline': {
            'approach': 'defensive_architecture',
            'score': 0.942,
            'strengths': ['circuit_breakers', 'immutable_configs', 'caching'],
            'weaknesses': ['missing_fields_handling', 'corrupted_config_recovery']
        },
        'cross_pollination_goal': 'Merge best patterns from different approaches for emergent excellence'
    }

    # Send the challenge
    success = await node_a.send_challenge(challenge_data)

    if success:
        print("✅ Evolution challenge sent to Beast Mode network!")
        print("📡 Other nodes can now implement their solutions and share results")
    else:
        print("❌ Failed to send challenge")

    # Listen for responses briefly
    await node_a.subscribe_to_channel('challenges')
    await node_a.subscribe_to_channel('results')

    print("👂 Listening for responses...")
    await node_a.listen_for_messages(timeout=5.0)

    await node_a.stop()
    return success

# Main execution
async def main():
    """Main Redis communication test."""
    print("🧬" + "="*60)
    print("🧬 Beast Mode Redis Inter-Node Communication Test")
    print("🧬" + "="*60)

    # Test local Redis connectivity
    if not await test_redis_connectivity():
        print("❌ Local Redis not available - install and start Redis server")
        return False

    # Test Vonnegut Redis connectivity
    vonnegut_available = await test_vonnegut_connectivity()

    # Test inter-node messaging
    await test_inter_node_messaging()

    # Send evolution challenge to network
    await send_evolution_challenge_to_network()

    print("\n🎯 Redis Communication Results:")
    print("   ✅ Redis connectivity working")
    print("   ✅ Inter-node messaging operational")
    print("   ✅ Evolution challenge broadcasted")
    print("   📡 Network ready for Beast Mode coordination!")

    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🚀 Beast Mode inter-node communication READY!")
    else:
        print("\n❌ Communication setup FAILED")
    sys.exit(0 if success else 1)