#!/usr/bin/env python3
"""
Ping the Beast Mode network via pub/sub channels
"""

import redis
import json
import time
from datetime import datetime


def ping_pubsub_network():
    """Send ping via pub/sub and listen for responses"""
    print("📡 **PINGING BEAST MODE NETWORK VIA PUB/SUB**")

    r = redis.Redis(host="localhost", port=6379, db=0)

    # Create pub/sub object for listening
    pubsub = r.pubsub()

    # Subscribe to response channel
    response_channel = "beast_mode_network_responses"
    pubsub.subscribe(response_channel)

    print(f"🎧 Subscribed to {response_channel} for responses")

    # Send ping message to main network channel
    ping_message = {
        "type": "NETWORK_PING",
        "sender": "NETWORK_DIAGNOSTICS",
        "timestamp": datetime.now().isoformat(),
        "message": "Network diagnostic ping via pub/sub - please respond",
        "respond_to": response_channel,
    }

    # Try multiple channels
    channels_to_ping = [
        "beast_mode_network",
        "beast_mode_messages",
        "agent_network",
        "collaboration_network",
    ]

    for channel in channels_to_ping:
        try:
            result = r.publish(channel, json.dumps(ping_message))
            print(f"📤 Sent ping to '{channel}' - {result} subscribers received it")
        except Exception as e:
            print(f"❌ Error sending to '{channel}': {e}")

    # Listen for responses
    print(f"⏳ Listening for responses for 5 seconds...")

    responses = []
    start_time = time.time()

    try:
        while time.time() - start_time < 5:
            message = pubsub.get_message(timeout=1)
            if message and message["type"] == "message":
                try:
                    data = json.loads(message["data"].decode("utf-8"))
                    if data.get("type") == "PONG":
                        responses.append(data)
                        sender = data.get("sender", "unknown")
                        print(f"🏓 PONG received from: {sender}")
                except Exception as e:
                    print(f"📨 Raw message received: {message['data']}")

    except KeyboardInterrupt:
        print("⏹️  Stopped listening")

    finally:
        pubsub.close()

    print(f"\n📊 **RESULTS**")
    print(f"  Responses received: {len(responses)}")

    if len(responses) == 0:
        print(f"  💡 Try checking what channels agents are actually listening to")

        # Check all active channels again
        channels = r.pubsub_channels()
        print(f"\n📻 **ACTIVE CHANNELS**")
        for channel in channels:
            num_subs = r.pubsub_numsub(channel)[0][1]
            print(f"  📡 {channel.decode('utf-8')}: {num_subs} subscribers")

    return len(responses) > 0


if __name__ == "__main__":
    ping_pubsub_network()
