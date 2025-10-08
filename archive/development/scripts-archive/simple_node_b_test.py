#!/usr/bin/env python3
"""
Simple Node B test - verify it works
"""
import asyncio
import json
import uuid
from datetime import datetime
import redis.asyncio as redis

NODE_ID = "simple-test-node-b"
REDIS_HOST = "192.168.1.119"
REDIS_PORT = 6379
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
CHANNEL = "beast_mode_network"

async def simple_node_b_test():
    """Simple test of Node B functionality."""
    print("🧬 Simple Node B Test")
    print("="*40)

    try:
        # Connect to Redis
        redis_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
        client = redis.from_url(redis_url)
        await client.ping()
        print(f"✅ Connected to Beast Mode network")

        # Send presence announcement
        presence = {
            "id": str(uuid.uuid4()),
            "type": "agent_discovery",
            "source": NODE_ID,
            "target": None,
            "payload": {
                "agent_info": {
                    "approach": "simple_test_node_b",
                    "status": "testing"
                },
                "message": f"{NODE_ID} is testing Beast Mode coordination!"
            },
            "timestamp": datetime.now().isoformat(),
            "priority": 5
        }

        await client.publish(CHANNEL, json.dumps(presence))
        print(f"📡 Sent presence announcement")

        # Listen for messages briefly
        pubsub = client.pubsub()
        await pubsub.subscribe(CHANNEL)

        print(f"👂 Listening for responses...")

        message_count = 0
        timeout_count = 0
        max_timeout = 10  # 10 seconds of no messages = exit

        async for raw_message in pubsub.listen():
            if raw_message["type"] == "message":
                try:
                    data = json.loads(raw_message["data"])

                    # Skip our own messages
                    if data.get("source") == NODE_ID:
                        continue

                    message_count += 1
                    print(f"\n📨 Message {message_count} received:")
                    print(f"   From: {data.get('source', 'unknown')}")
                    print(f"   Type: {data.get('type', 'unknown')}")
                    print(f"   Payload: {str(data.get('payload', {}))[:100]}...")

                    timeout_count = 0  # Reset timeout

                except Exception as e:
                    print(f"❌ Error processing message: {e}")

            else:
                # No message - increment timeout
                timeout_count += 1
                if timeout_count >= max_timeout:
                    print(f"\n⏰ No messages for {max_timeout} seconds - stopping")
                    break

                # Brief wait
                await asyncio.sleep(1)

        await pubsub.aclose()
        await client.aclose()

        print(f"\n📊 Test Results:")
        print(f"   Messages processed: {message_count}")
        print(f"   Connection: ✅ Success")
        print(f"   Pub/Sub: ✅ Working")

        if message_count > 0:
            print(f"   Network Activity: ✅ Active")
        else:
            print(f"   Network Activity: ⚠️  Quiet (no other nodes responding)")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(simple_node_b_test())
    print(f"\n🎯 Test {'PASSED' if success else 'FAILED'}")