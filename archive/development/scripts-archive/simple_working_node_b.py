#!/usr/bin/env python3
"""
Simple Working Node B
====================

Minimal Node B implementation that just works without complexity.
"""

import asyncio
import json
import redis
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.security.secure_credentials import get_redis_password


class SimpleNodeB:
    """Simple, working Node B implementation."""
    
    def __init__(self):
        self.node_id = "simple-node-b"
        self.running = True
        
        # Connect to Redis
        try:
            redis_password = get_redis_password()
            self.redis = redis.Redis(
                host="192.168.1.119",
                port=6379,
                password=redis_password,
                decode_responses=True
            )
            
            # Test connection
            self.redis.ping()
            print(f"✅ Connected to Redis as {self.node_id}")
            
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            sys.exit(1)
    
    async def send_heartbeat(self):
        """Send periodic heartbeat."""
        while self.running:
            try:
                heartbeat = {
                    "node_id": self.node_id,
                    "timestamp": datetime.now().isoformat(),
                    "status": "active",
                    "message": "Node B is alive and listening"
                }
                
                # Publish heartbeat
                self.redis.publish("beast_mode_network", json.dumps(heartbeat))
                print(f"💓 Heartbeat sent at {heartbeat['timestamp']}")
                
                await asyncio.sleep(10)  # Heartbeat every 10 seconds
                
            except Exception as e:
                print(f"❌ Heartbeat error: {e}")
                await asyncio.sleep(5)
    
    async def listen_for_messages(self):
        """Listen for incoming messages."""
        pubsub = self.redis.pubsub()
        pubsub.subscribe("beast_mode_network")
        
        print(f"👂 {self.node_id} listening on beast_mode_network channel...")
        
        while self.running:
            try:
                message = pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    data = json.loads(message['data'])
                    
                    # Don't process our own messages
                    if data.get('node_id') != self.node_id:
                        print(f"📨 Received: {data}")
                        
                        # Send a response
                        response = {
                            "node_id": self.node_id,
                            "timestamp": datetime.now().isoformat(),
                            "response_to": data.get('node_id', 'unknown'),
                            "message": f"Node B acknowledges: {data.get('message', 'no message')}"
                        }
                        
                        self.redis.publish("beast_mode_network", json.dumps(response))
                        print(f"📤 Sent response to {response['response_to']}")
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Message processing error: {e}")
                await asyncio.sleep(1)
    
    async def run(self):
        """Run Node B with heartbeat and message listening."""
        print(f"🚀 Starting {self.node_id}...")
        
        # Start heartbeat and message listening concurrently
        await asyncio.gather(
            self.send_heartbeat(),
            self.listen_for_messages()
        )
    
    def stop(self):
        """Stop Node B gracefully."""
        print(f"🛑 Stopping {self.node_id}...")
        self.running = False


async def main():
    """Main function."""
    node_b = SimpleNodeB()
    
    try:
        await node_b.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested")
        node_b.stop()
    except Exception as e:
        print(f"❌ Node B error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🧬 Simple Node B Starting...")
    asyncio.run(main())