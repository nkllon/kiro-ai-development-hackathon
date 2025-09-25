#!/usr/bin/env python3
"""
Check what message Node B sent
"""
import asyncio
import json
import redis.asyncio as redis

async def check_recent_messages():
    client = redis.from_url("redis://:beastmode2025@192.168.1.119:6379")

    print("👂 Monitoring Beast Mode network for Node B's message...")

    pubsub = client.pubsub()
    await pubsub.subscribe("beast_mode_network")

    # Listen briefly to catch any recent messages
    timeout_count = 0

    try:
        async for raw_message in pubsub.listen():
            if raw_message["type"] == "message":
                try:
                    data = json.loads(raw_message["data"])
                    sender = data.get("source", "unknown")

                    # Look for messages from Node B
                    if "node-b" in sender.lower() or sender == "node-b-simple":
                        print(f"\n📨 MESSAGE FROM NODE B ({sender}):")
                        print(f"   Type: {data.get('type', 'unknown')}")
                        print(f"   Target: {data.get('target', 'broadcast')}")

                        payload = data.get('payload', {})
                        if 'message' in payload:
                            print(f"   Message: {payload['message']}")
                        elif 'response' in payload:
                            print(f"   Response: {payload['response'][:200]}...")
                        else:
                            print(f"   Payload: {str(payload)[:150]}...")

                        # Found Node B's message, we can exit
                        break

                except Exception as e:
                    print(f"❌ Error processing message: {e}")

            # Timeout after a few seconds of no activity
            timeout_count += 1
            if timeout_count > 5:
                print("⏰ No recent messages from Node B detected")
                break

    except Exception as e:
        print(f"❌ Error monitoring: {e}")
    finally:
        await pubsub.aclose()
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(check_recent_messages())