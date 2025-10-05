#!/usr/bin/env python3
"""
Communicate with the agents on beast_mode_network using proper message formats
"""

import redis
import json
import time
import threading
from datetime import datetime


class AgentCommunicator:
    def __init__(self):
        self.r = redis.Redis(host="localhost", port=6379, db=0)
        self.pubsub = self.r.pubsub()
        self.listening = False
        self.responses = []

    def start_listening(self):
        """Start listening for responses"""
        self.pubsub.subscribe("beast_mode_network")
        self.listening = True

        def listen_loop():
            try:
                for message in self.pubsub.listen():
                    if not self.listening:
                        break

                    if message["type"] == "message":
                        try:
                            data = json.loads(message["data"].decode("utf-8"))

                            # Skip our own messages
                            if data.get("sender_id") == "HUMAN_TEAM":
                                continue

                            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            sender = data.get("sender_id", "unknown")
                            msg_type = data.get(
                                "message_type", data.get("type", "unknown")
                            )

                            self.responses.append(data)
                            print(
                                f"[{timestamp}] 📨 Response from {sender} ({msg_type})"
                            )

                            # Show the content
                            content = data.get("content", {})
                            if isinstance(content, dict):
                                if "message" in content:
                                    print(f"  💬 {content['message']}")
                                elif "status" in content:
                                    print(f"  📊 Status: {content['status']}")
                                else:
                                    print(f"  📄 Content: {content}")
                            else:
                                print(f"  📄 Content: {content}")

                        except json.JSONDecodeError:
                            print(
                                f"[{timestamp}] 📨 Raw message: {message['data'].decode('utf-8')}"
                            )
                        except Exception as e:
                            print(f"[{timestamp}] ❌ Error processing message: {e}")

            except Exception as e:
                print(f"❌ Listener error: {e}")

        self.listener_thread = threading.Thread(target=listen_loop, daemon=True)
        self.listener_thread.start()
        time.sleep(0.5)  # Give it time to subscribe

    def send_message(self, message_data):
        """Send message to beast_mode_network"""
        try:
            result = self.r.publish("beast_mode_network", json.dumps(message_data))
            print(f"📤 Message sent - {result} subscribers received it")
            return result > 0
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False

    def stop_listening(self):
        """Stop listening"""
        self.listening = False
        self.pubsub.close()


def main():
    """Main communication test"""
    print("💬 **COMMUNICATING WITH BEAST MODE AGENTS**")
    print("=" * 50)

    comm = AgentCommunicator()

    # Start listening
    print("🎧 Starting listener on beast_mode_network...")
    comm.start_listening()

    # Try different message formats that agents might recognize
    test_messages = [
        # Standard Beast Mode format
        {
            "message_type": "AGENT_INQUIRY",
            "sender_id": "HUMAN_TEAM",
            "timestamp": datetime.now().isoformat(),
            "subject": "Network Status Check",
            "content": {
                "message": "Hello agents! This is the human team. Are you receiving messages?",
                "request_type": "status_check",
                "respond_to": "beast_mode_network",
            },
        },
        # Simple format
        {
            "type": "HELLO",
            "sender": "HUMAN_TEAM",
            "timestamp": datetime.now().isoformat(),
            "message": "Hello Beast Mode network! Please respond if you can see this.",
            "request": "status_update",
        },
        # TIDB specific
        {
            "message_type": "DIRECT_QUESTION",
            "sender_id": "HUMAN_TEAM",
            "target": "TIDB",
            "timestamp": datetime.now().isoformat(),
            "subject": "Collaboration Network Status",
            "content": {
                "message": "TIDB, we have questions about the collaboration network. Are you available?",
                "questions": [
                    "What is the current network status?",
                    "How many agents are active?",
                    "What tasks are you working on?",
                ],
            },
        },
        # Help request format
        {
            "message_type": "HELP_REQUEST",
            "sender_id": "HUMAN_TEAM",
            "timestamp": datetime.now().isoformat(),
            "subject": "Need Network Information",
            "content": {
                "description": "Human team needs information about current network status and active agents",
                "priority": "normal",
                "capabilities_required": ["NETWORK_STATUS", "AGENT_MANAGEMENT"],
            },
        },
        # Ping format
        {
            "type": "PING",
            "sender_id": "HUMAN_TEAM",
            "timestamp": datetime.now().isoformat(),
            "ping_id": f"ping_{int(time.time())}",
            "message": "Network ping - please respond with PONG",
        },
    ]

    print(f"📤 Sending {len(test_messages)} different message formats...\n")

    for i, message in enumerate(test_messages, 1):
        print(f"📤 Sending message {i}/{len(test_messages)}...")
        print(
            f"  Format: {message.get('message_type', message.get('type', 'unknown'))}"
        )

        success = comm.send_message(message)
        if success:
            print(f"  ✅ Delivered to agents")
        else:
            print(f"  ❌ Delivery failed")

        print(f"  ⏳ Waiting 3 seconds for responses...")
        time.sleep(3)
        print()

    # Final summary
    print(f"📊 **COMMUNICATION RESULTS**")
    print(f"  Messages sent: {len(test_messages)}")
    print(f"  Responses received: {len(comm.responses)}")

    if comm.responses:
        print(f"\n📨 **RESPONSES RECEIVED:**")
        for i, response in enumerate(comm.responses, 1):
            sender = response.get("sender_id", response.get("sender", "unknown"))
            msg_type = response.get("message_type", response.get("type", "unknown"))
            print(f"  {i}. {sender} → {msg_type}")
    else:
        print(f"\n⚠️  **NO RESPONSES RECEIVED**")
        print(f"  Possible reasons:")
        print(f"    • Agents are listening but not programmed to respond")
        print(f"    • They expect different message formats")
        print(f"    • They're busy with other tasks")
        print(f"    • They only respond to specific senders or message types")

    comm.stop_listening()


if __name__ == "__main__":
    main()
