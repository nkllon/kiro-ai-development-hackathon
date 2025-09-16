#!/usr/bin/env python3
"""
Interactive network test - send message and listen for responses
"""
import json
import threading
import time
from datetime import datetime

import redis


class NetworkTester:
    def __init__(self):
        self.r = redis.Redis(host="localhost", port=6379, db=0)
        self.pubsub = self.r.pubsub()
        self.listening = False
        self.messages_received = []

    def start_listening(self):
        """Start listening in background thread"""
        self.pubsub.subscribe("beast_mode_network")
        self.listening = True

        def listen_loop():
            try:
                for message in self.pubsub.listen():
                    if not self.listening:
                        break
                    if message["type"] == "message":
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        try:
                            data = json.loads(message["data"].decode("utf-8"))
                            sender = data.get("sender", "unknown")
                            msg_type = data.get("type", "unknown")
                            content = data.get("message", "")
                            self.messages_received.append(
                                {
                                    "timestamp": timestamp,
                                    "sender": sender,
                                    "type": msg_type,
                                    "content": content,
                                    "raw_data": data,
                                }
                            )
                            print("[{timestamp}] 📨 {sender} → {msg_type}: {content}")
                        except json.JSONDecodeError:
                            message["data"].decode("utf-8")
                            print("[{timestamp}] 📨 Raw: {raw_content}")
                    elif message["type"] == "subscribe":
                        print("✅ Subscribed to beast_mode_network")
            except Exception:
                print("❌ Listener error: {e}")

        # Start listener thread
        self.listener_thread = threading.Thread(target=listen_loop, daemon=True)
        self.listener_thread.start()
        time.sleep(0.5)  # Give it time to subscribe

    def send_message(self, message_data):
        """Send message to network"""
        try:
            result = self.r.publish("beast_mode_network", json.dumps(message_data))
            print("📤 Sent message - {result} subscribers received it")
            return result
        except Exception:
            print("❌ Error sending: {e}")
            return 0

    def stop_listening(self):
        """Stop listening"""
        self.listening = False
        self.pubsub.close()

    def run_test(self):
        """Run interactive test"""
        print("🧪 **INTERACTIVE BEAST MODE NETWORK TEST**")
        print("=" * 50)
        # Start listening
        print("🎧 Starting listener...")
        self.start_listening()
        # Send various test messages
        test_messages = [
            {
                "type": "HELLO",
                "sender": "HUMAN_TEAM",
                "timestamp": datetime.now().isoformat(),
                "message": "Hello! Is anyone there?",
                "request": "Please respond if you can see this",
            },
            {
                "type": "STATUS_REQUEST",
                "sender": "HUMAN_TEAM",
                "timestamp": datetime.now().isoformat(),
                "message": "Requesting status from all agents",
                "request": "What are you working on?",
            },
            {
                "type": "TIDB_DIRECT",
                "sender": "HUMAN_TEAM",
                "timestamp": datetime.now().isoformat(),
                "message": "TIDB, are you there? We have questions about the collaboration network.",
                "target": "TIDB",
            },
        ]
        for i, msg in enumerate(test_messages):
            print("\n📤 Sending test message {i+1}/3...")
            self.send_message(msg)
            print("⏳ Waiting 3 seconds for responses...")
            time.sleep(3)
        print("\n📊 **TEST RESULTS**")
        print("Messages received: {len(self.messages_received)}")
        if self.messages_received:
            print("\n📨 **RECEIVED MESSAGES:**")
            for msg in self.messages_received:
                print("  [{msg['timestamp']}] {msg['sender']} → {msg['type']}")
                print("    Content: {msg['content']}")
        else:
            print("⚠️  No responses received")
            print("💡 Agents are listening but not responding to these message types")
        self.stop_listening()


if __name__ == "__main__":
    tester = NetworkTester()
    try:
        tester.run_test()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
        tester.stop_listening()
