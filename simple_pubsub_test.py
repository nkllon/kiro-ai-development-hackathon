#!/usr/bin/env python3
"""
Simple Beast Mode Pub/Sub Test - No Docker Required
"""

import asyncio
import json
import sys
from datetime import datetime
import uuid

# Try to import redis, install if needed
try:
    import redis.asyncio as redis
except ImportError:
    print("Installing redis...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "redis"])
    import redis.asyncio as redis

try:
    from pydantic import BaseModel
except ImportError:
    print("Installing pydantic...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic"])
    from pydantic import BaseModel


class SimpleMessage(BaseModel):
    """Simple message format"""

    id: str
    type: str
    source: str
    payload: dict
    timestamp: str


async def simple_publisher():
    """Simple message publisher"""
    client = redis.from_url("redis://localhost:6379")

    print("🧬 Beast Mode Simple Publisher Started")

    for i in range(5):
        message = SimpleMessage(
            id=str(uuid.uuid4()),
            type="test_message",
            source="simple_publisher",
            payload={"count": i, "message": f"Hello Beast Mode #{i}"},
            timestamp=datetime.now().isoformat(),
        )

        await client.publish("beast_mode_test", message.model_dump_json())
        print(f"📤 Published message {i}: {message.id}")
        await asyncio.sleep(1)

    await client.close()


async def simple_subscriber():
    """Simple message subscriber"""
    client = redis.from_url("redis://localhost:6379")
    pubsub = client.pubsub()

    await pubsub.subscribe("beast_mode_test")
    print("🧬 Beast Mode Simple Subscriber Started")
    print("📥 Listening for messages...")

    message_count = 0
    async for message in pubsub.listen():
        if message["type"] == "message":
            try:
                data = json.loads(message["data"])
                msg = SimpleMessage(**data)
                message_count += 1

                print(f"📨 Received message {message_count}:")
                print(f"   ID: {msg.id}")
                print(f"   Type: {msg.type}")
                print(f"   From: {msg.source}")
                print(f"   Payload: {msg.payload}")
                print(f"   Time: {msg.timestamp}")
                print("-" * 40)

                if message_count >= 5:
                    break

            except Exception as e:
                print(f"❌ Error processing message: {e}")

    await pubsub.close()
    await client.close()


async def test_redis_connection():
    """Test Redis connection"""
    try:
        client = redis.from_url("redis://localhost:6379")
        pong = await client.ping()
        await client.close()

        if pong:
            print("✅ Redis connection successful!")
            return True
        else:
            print("❌ Redis ping failed")
            return False

    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🧬 Beast Mode Simple Pub/Sub Test")
    print("=" * 40)

    # Test Redis connection
    if not await test_redis_connection():
        print("Please make sure Redis is running: brew services start redis")
        return

    print("\nStarting pub/sub test...")

    # Run subscriber and publisher concurrently
    await asyncio.gather(
        simple_subscriber(), asyncio.sleep(0.5), simple_publisher()  # Small delay
    )

    print("\n🎉 Beast Mode pub/sub test completed!")


if __name__ == "__main__":
    asyncio.run(main())
