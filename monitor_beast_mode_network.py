#!/usr/bin/env python3
"""
Beast Mode Network Monitor
==========================

Real-time monitoring tool for the Beast Mode coordination network.
Displays live activity from all connected nodes.

Usage:
    python3 monitor_beast_mode_network.py

Features:
- Live message monitoring across all Beast Mode channels
- Node presence tracking
- Challenge result aggregation
- Performance metrics display
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any
import signal

try:
    import redis.asyncio as redis
except ImportError:
    print("📦 Installing redis...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'redis'])
    import redis.asyncio as redis

# Network Configuration
REDIS_HOST = "192.168.1.119"
REDIS_PORT = 6379
REDIS_PASSWORD = "beastmode2025"

class BeastModeNetworkMonitor:
    """Real-time Beast Mode network monitor."""

    def __init__(self):
        self.redis_client = None
        self.pubsub = None
        self.running = False
        self.nodes_seen = {}
        self.challenge_results = {}
        self.message_count = 0

        # Beast Mode channels to monitor
        self.channels = [
            'beast_mode:coordination',
            'beast_mode:challenges',
            'beast_mode:results',
            'beast_mode:spores'
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

            # Subscribe to all Beast Mode channels
            for channel in self.channels:
                await self.pubsub.subscribe(channel)

            print(f"🔗 Connected to Beast Mode network at {REDIS_HOST}:{REDIS_PORT}")
            print(f"👂 Monitoring channels: {', '.join(self.channels)}")
            return True

        except Exception as e:
            print(f"❌ Failed to connect to Beast Mode network: {e}")
            return False

    async def start_monitoring(self):
        """Start real-time network monitoring."""
        if not self.pubsub:
            print("❌ Not connected to network")
            return

        self.running = True
        print("\n🎯 Beast Mode Network Monitor - ACTIVE")
        print("="*60)
        print(f"Timestamp: {datetime.now()}")
        print("="*60)

        try:
            while self.running:
                message = await self.pubsub.get_message(timeout=1.0)

                if message and message['type'] == 'message':
                    await self._process_message(message)

        except asyncio.CancelledError:
            print("\n🛑 Monitoring stopped")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")

    async def _process_message(self, raw_message):
        """Process and display incoming network messages."""
        try:
            envelope = json.loads(raw_message['data'])
            channel = raw_message['channel']
            sender = envelope.get('sender', 'unknown')
            content = envelope.get('content', {})
            timestamp = envelope.get('timestamp', 'unknown')

            self.message_count += 1

            # Track node activity
            if sender not in self.nodes_seen:
                self.nodes_seen[sender] = {
                    'first_seen': timestamp,
                    'message_count': 0,
                    'last_activity': timestamp
                }

            self.nodes_seen[sender]['message_count'] += 1
            self.nodes_seen[sender]['last_activity'] = timestamp

            # Display message based on type
            await self._display_message(channel, sender, content, timestamp)

            # Store results for aggregation
            if content.get('type') == 'challenge_results':
                self.challenge_results[sender] = content

        except Exception as e:
            print(f"⚠️  Message processing error: {e}")

    async def _display_message(self, channel: str, sender: str, content: Dict[str, Any], timestamp: str):
        """Display formatted network message."""
        message_type = content.get('type', 'unknown')
        time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp[:8]

        if message_type == 'node_presence':
            status = content.get('status', 'unknown')
            capabilities = content.get('capabilities', [])
            approach = content.get('implementation_approach', 'unknown')

            print(f"\n🟢 [{time_str}] NODE PRESENCE")
            print(f"   Node: {sender}")
            print(f"   Status: {status}")
            print(f"   Approach: {approach}")
            print(f"   Capabilities: {len(capabilities)} items")

        elif message_type == 'challenge_results':
            score = content.get('final_systematic_score', 0.0)
            passes = content.get('passes_target', False)
            approach = content.get('approach', 'unknown')

            print(f"\n📊 [{time_str}] CHALLENGE RESULTS")
            print(f"   Node: {sender}")
            print(f"   Approach: {approach}")
            print(f"   Score: {score:.3f}")
            print(f"   Target Met: {'✅' if passes else '❌'}")

        elif message_type == 'evolution_challenge':
            challenge_id = content.get('challenge_id', 'unknown')
            target_score = content.get('target_score', 0.0)

            print(f"\n🧬 [{time_str}] EVOLUTION CHALLENGE")
            print(f"   From: {sender}")
            print(f"   Challenge: {challenge_id}")
            print(f"   Target Score: {target_score}")

        elif message_type == 'spore_delivery':
            target = content.get('target', 'broadcast')
            description = content.get('description', 'No description')

            print(f"\n🧬 [{time_str}] SPORE DELIVERY")
            print(f"   From: {sender}")
            print(f"   To: {target}")
            print(f"   Task: {description[:50]}...")

        else:
            print(f"\n📡 [{time_str}] {message_type.upper()}")
            print(f"   From: {sender}")
            print(f"   Channel: {channel.split(':')[1]}")

        # Show network status periodically
        if self.message_count % 10 == 0:
            await self._show_network_status()

    async def _show_network_status(self):
        """Display current network status."""
        print(f"\n{'='*60}")
        print(f"📊 NETWORK STATUS - {len(self.nodes_seen)} active nodes | {self.message_count} messages")
        print(f"{'='*60}")

        for node_id, info in self.nodes_seen.items():
            print(f"   {node_id}: {info['message_count']} messages")

        if self.challenge_results:
            print(f"\n🏆 CHALLENGE LEADERBOARD:")
            sorted_results = sorted(
                self.challenge_results.items(),
                key=lambda x: x[1].get('final_systematic_score', 0),
                reverse=True
            )

            for i, (node, result) in enumerate(sorted_results, 1):
                score = result.get('final_systematic_score', 0.0)
                approach = result.get('approach', 'unknown')
                print(f"   {i}. {node}: {score:.3f} ({approach})")

    async def stop(self):
        """Stop monitoring and disconnect."""
        self.running = False
        if self.pubsub:
            await self.pubsub.aclose()
        if self.redis_client:
            await self.redis_client.aclose()
        print(f"\n🔌 Disconnected from Beast Mode network")

# Signal handling for graceful shutdown
monitor_instance = None

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    global monitor_instance
    if monitor_instance:
        asyncio.create_task(monitor_instance.stop())
    sys.exit(0)

async def main():
    """Main monitoring function."""
    global monitor_instance

    print("🧬 Beast Mode Network Monitor")
    print("="*40)
    print("Monitoring real-time Beast Mode network activity...")
    print("Press Ctrl+C to stop")
    print("="*40)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and start monitor
    monitor_instance = BeastModeNetworkMonitor()

    if not await monitor_instance.connect():
        print("❌ Could not connect to Beast Mode network")
        return

    # Start monitoring
    try:
        await monitor_instance.start_monitoring()
    finally:
        await monitor_instance.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Beast Mode monitoring stopped")
    except Exception as e:
        print(f"\n❌ Monitor failed: {e}")
        sys.exit(1)