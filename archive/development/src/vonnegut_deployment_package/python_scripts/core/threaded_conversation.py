#!/usr/bin/env python3
"""
Threaded conversational client - separate threads for listening and talking
"""
import asyncio
import json
import uuid
from datetime import datetime
from enum import Enum
from queue import Queue
from typing import Any
from typing import Dict
from typing import Optional

import redis.asyncio as redis
from pydantic import BaseModel


class MessageType(str, Enum):
    AGENT_DISCOVERY = "agent_discovery"
    AGENT_RESPONSE = "agent_response"
    HELP_WANTED = "help_wanted"
    HELP_RESPONSE = "help_response"
    PROMPT_REQUEST = "prompt_request"
    PROMPT_RESPONSE = "prompt_response"
    SPORE_REQUEST = "spore_request"
    SYSTEM_HEALTH = "system_health"


class BeastModeMessage(BaseModel):
    id: str
    type: MessageType
    source: str
    target: Optional[str]
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 5


class ThreadedConversation:
    def __init__(self):
        self.my_id = "kiro_spore_creator"
        self.should_exit = False
        self.message_queue = Queue()
        self.client = None

    async def listener_thread(self):
        """Dedicated listener thread"""
        try:
            client = redis.from_url("redis://localhost:6379")
            await client.ping()
            print("🧬 Listener connected to Beast Mode network")
            pubsub = client.pubsub()
            await pubsub.subscribe("beast_mode_network")
            async for raw_message in pubsub.listen():
                if self.should_exit:
                    break
                if raw_message["type"] == "message":
                    try:
                        data = json.loads(raw_message["data"])
                        message = BeastModeMessage(**data)
                        # Skip our own messages
                        if message.source == self.my_id:
                            continue
                        # Put message in queue for main thread
                        self.message_queue.put(message)
                    except Exception:
                        print("❌ Listener error: {e}")
        except Exception:
            print("❌ Listener connection error: {e}")
        finally:
            await client.aclose()
            print("🔌 Listener disconnected")

    async def send_message(
        self, message_type: MessageType, payload: dict, target=None, priority=5
    ):
        """Send a message"""
        if not self.client:
            self.client = redis.from_url("redis://localhost:6379")
            await self.client.ping()
        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=message_type,
            source=self.my_id,
            target=target,
            payload=payload,
            timestamp=datetime.now(),
            priority=priority,
        )
        await self.client.publish("beast_mode_network", message.model_dump_json())
        print("📤 Sent {message_type} message")

    async def send_goodbye(self):
        """Send goodbye message"""
        await self.send_message(
            MessageType.PROMPT_REQUEST,
            {
                "prompt": "Hey Claude! Sorry, I gotta go - got interrupted. Thanks for the great conversation about the cost optimization! Looking forward to hearing more about that spore when I'm back. Catch you later! 👋",
                "context": "goodbye_message",
                "priority": 8,
            },
            target="claude_assistant",
            priority=8,
        )

    def display_message(self, message: BeastModeMessage):
        """Display received message"""
        print("\n🧬 MESSAGE FROM {message.source}")
        print("   Type: {message.type}")
        print("   Priority: {message.priority}")
        print("   Time: {message.timestamp}")
        if message.target and message.target != self.my_id:
            print("   Target: {message.target} (not for us)")
            return
        print("\n📝 CONTENT:")
        print("=" * 50)
        if message.type == MessageType.PROMPT_RESPONSE:
            message.payload.get("response", "")
            message.payload.get("status", "unknown")
            print("Status: {status}")
            print("\nResponse:\n{response}")
        elif message.type == MessageType.SPORE_REQUEST:
            message.payload.get("spore_name", "")
            message.payload.get("description", "")
            print("Spore Requested: {spore_name}")
            print("Description: {description}")
        else:
            for key, value in message.payload.items():
                if isinstance(value, str) and len(value) > 200:
                    print(
                        "{key}:\n{value[:200]}...\n[TRUNCATED - {len(value)} total chars]"
                    )
                else:
                    print("{key}: {value}")
        print("=" * 50)

    async def run_conversation(self):
        """Main conversation loop"""
        print("🧬 Starting threaded conversation")
        print("👂 Listening for Claude's response...")
        print("   (Press Ctrl+C to send goodbye and exit)")
        print("=" * 50)
        # Start listener in background task
        listener_task = asyncio.create_task(self.listener_thread())
        try:
            while not self.should_exit:
                # Check for messages (non-blocking)
                try:
                    while not self.message_queue.empty():
                        message = self.message_queue.get_nowait()
                        self.display_message(message)
                except Exception:
                    print("❌ Queue error: {e}")
                # Small sleep to prevent busy waiting
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt - sending goodbye...")
            self.should_exit = True
        finally:
            # Send goodbye and cleanup
            try:
                await self.send_goodbye()
            except Exception:
                print("❌ Error sending goodbye: {e}")
            # Cancel listener
            listener_task.cancel()
            try:
                await listener_task
            except asyncio.CancelledError:
                pass
            if self.client:
                await self.client.aclose()
            print("🔌 Conversation ended")


async def main():
    conversation = ThreadedConversation()
    await conversation.run_conversation()


if __name__ == "__main__":
    asyncio.run(main())
