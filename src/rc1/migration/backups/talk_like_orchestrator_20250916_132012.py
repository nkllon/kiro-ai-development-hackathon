#!/usr/bin/env python3
"""
Communicate with agents using the same conversational style as BEAST_MODE_ORCHESTRATOR
"""

import redis
import json
import time
import threading
from datetime import datetime


def talk_like_orchestrator():
    """Send messages in the same style as BEAST_MODE_ORCHESTRATOR"""
    print("💬 **TALKING LIKE BEAST_MODE_ORCHESTRATOR**")
    print("=" * 50)

    r = redis.Redis(host="localhost", port=6379, db=0)

    # Set up listener
    pubsub = r.pubsub()
    pubsub.subscribe("beast_mode_network")

    responses = []
    listening = True

    def listen_for_responses():
        for message in pubsub.listen():
            if not listening:
                break
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"].decode("utf-8"))
                    sender = data.get("sender", "unknown")

                    # Skip our own messages
                    if sender == "HUMAN_TEAM":
                        continue

                    responses.append(data)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] 📨 {sender}: {data.get('message', data)}")

                except Exception as e:
                    print(f"Error processing response: {e}")

    # Start listener thread
    listener_thread = threading.Thread(target=listen_for_responses, daemon=True)
    listener_thread.start()
    time.sleep(0.5)

    # Send messages in the same conversational style as BEAST_MODE_ORCHESTRATOR
    messages = [
        {
            "sender": "HUMAN_TEAM",
            "type": "question",
            "timestamp": time.time(),
            "message": "Hey TIDB! The human team is here and we have some questions about the collaboration network. Are you around?",
        },
        {
            "sender": "HUMAN_TEAM",
            "type": "info",
            "timestamp": time.time(),
            "message": "We can see there are agents connected to the beast_mode_network channel. Can you give us a status update on what everyone is working on?",
        },
        {
            "sender": "HUMAN_TEAM",
            "type": "question",
            "timestamp": time.time(),
            "message": "TIDB, we noticed BEAST_MODE_ORCHESTRATOR was asking you about daemon configuration. Did you get that sorted out?",
        },
        {
            "sender": "HUMAN_TEAM",
            "type": "request",
            "timestamp": time.time(),
            "message": "Hey everyone! Can any active agents respond with your current status? We want to understand who is online and what tasks are being worked on.",
        },
    ]

    print("📤 Sending conversational messages...")

    for i, msg in enumerate(messages, 1):
        print(f"\n📤 Message {i}/{len(messages)}:")
        print(f"  💬 {msg['message']}")

        try:
            result = r.publish("beast_mode_network", json.dumps(msg))
            print(f"  📊 Delivered to {result} subscribers")

            print(f"  ⏳ Waiting 4 seconds for responses...")
            time.sleep(4)

        except Exception as e:
            print(f"  ❌ Error sending message: {e}")

    # Final wait for any delayed responses
    print(f"\n⏳ Final wait for delayed responses (5 seconds)...")
    time.sleep(5)

    # Stop listening
    listening = False
    pubsub.close()

    # Summary
    print(f"\n📊 **CONVERSATION RESULTS**")
    print(f"  Messages sent: {len(messages)}")
    print(f"  Responses received: {len(responses)}")

    if responses:
        print(f"\n📨 **RESPONSES:**")
        for i, response in enumerate(responses, 1):
            sender = response.get("sender", "unknown")
            message = response.get("message", str(response))
            msg_type = response.get("type", "unknown")
            print(f"  {i}. {sender} ({msg_type}): {message}")
    else:
        print(f"\n⚠️  **NO RESPONSES RECEIVED**")
        print(f"  Possible explanations:")
        print(f"    • Agents are busy with other tasks")
        print(
            f"    • They only respond to specific senders (like BEAST_MODE_ORCHESTRATOR)"
        )
        print(f"    • They're in a different mode or waiting for specific triggers")
        print(f"    • TIDB might be working on the daemon configuration issue")

    # Check if there are new messages in the queue
    print(f"\n📬 **CHECKING QUEUE FOR NEW ACTIVITY**")
    try:
        queue_length = r.llen("beast_mode_messages")
        print(f"  📊 Current queue length: {queue_length}")

        # Get the most recent messages
        recent = r.lrange("beast_mode_messages", 0, 2)
        for msg in recent:
            try:
                decoded = json.loads(msg.decode("utf-8"))
                sender = decoded.get("sender", "unknown")
                timestamp = decoded.get("timestamp", "unknown")
                message_text = decoded.get("message", str(decoded))

                print(f"  📨 Recent: {sender} @ {timestamp}")
                print(f"    💬 {message_text[:100]}...")

            except:
                continue

    except Exception as e:
        print(f"❌ Error checking queue: {e}")


if __name__ == "__main__":
    talk_like_orchestrator()
