#!/usr/bin/env python3
"""
Listen to the beast_mode_network channel to see what's happening
"""

import redis
import json
import time
from datetime import datetime


def listen_to_network():
    """Listen to beast_mode_network channel"""
    print("🎧 **LISTENING TO BEAST_MODE_NETWORK CHANNEL**")
    print("Press Ctrl+C to stop listening")
    print("=" * 50)

    r = redis.Redis(host="localhost", port=6379, db=0)
    pubsub = r.pubsub()

    # Subscribe to the main network channel
    pubsub.subscribe("beast_mode_network")

    message_count = 0

    try:
        for message in pubsub.listen():
            if message["type"] == "message":
                message_count += 1
                timestamp = datetime.now().strftime("%H:%M:%S")

                try:
                    # Try to parse as JSON
                    data = json.loads(message["data"].decode("utf-8"))
                    sender = data.get("sender", "unknown")
                    msg_type = data.get("type", "unknown")
                    content = data.get("message", str(data))

                    print(f"[{timestamp}] 📨 {sender} → {msg_type}")
                    print(f"  Content: {content}")

                    # If it's a response to our ping, note it
                    if "NETWORK_DIAGNOSTICS" in content:
                        print(f"  🎯 This is related to our diagnostic ping!")

                except json.JSONDecodeError:
                    # Raw message
                    raw_content = message["data"].decode("utf-8")
                    print(f"[{timestamp}] 📨 Raw message: {raw_content}")

                print()  # Empty line for readability

            elif message["type"] == "subscribe":
                print(f"✅ Subscribed to {message['channel'].decode('utf-8')}")
                print(f"🎧 Listening for messages... (message #{message_count})")
                print()

    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped listening after {message_count} messages")

    finally:
        pubsub.close()


if __name__ == "__main__":
    listen_to_network()
