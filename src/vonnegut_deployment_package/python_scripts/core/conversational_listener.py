#!/usr/bin/env python3
"""
Conversational listener - peek bus, dump messages, handle interruptions
"""

import asyncio
import json
import uuid
import signal
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

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


class ConversationalListener:
    def __init__(self):
        self.client = None
        self.my_id = "kiro_spore_creator"
        self.should_exit = False

    async def send_goodbye_message(self):
        """Send goodbye message when interrupted"""
        if self.client:
            try:
                goodbye = BeastModeMessage(
                    id=str(uuid.uuid4()),
                    type=MessageType.PROMPT_REQUEST,
                    source=self.my_id,
                    target="claude_assistant",
                    payload={
                        "prompt": "Hey Claude! Sorry, I gotta go - got interrupted. Thanks for the great conversation about the cost optimization! Looking forward to hearing more about that spore when I'm back. Catch you later! 👋",
                        "context": "goodbye_message",
                        "priority": 8,
                    },
                    timestamp=datetime.now(),
                    priority=8,
                )

                await self.client.publish(
                    "beast_mode_network", goodbye.model_dump_json()
                )
                print("\n📤 Sent goodbye message to Claude")

            except Exception as e:
                print(f"❌ Error sending goodbye: {e}")

    async def peek_and_listen(self):
        """Peek bus and listen for messages"""
        try:
            self.client = redis.from_url("redis://localhost:6379")
            await self.client.ping()
            print("🧬 Connected to Beast Mode network")
            print("👂 Listening for Claude's response...")
            print("   (Press Ctrl+C to send goodbye and exit)")
            print("=" * 50)

            pubsub = self.client.pubsub()
            await pubsub.subscribe("beast_mode_network")

            # Set up signal handler for graceful exit
            def signal_handler(signum, frame):
                print(f"\n🛑 Received signal {signum}")
                self.should_exit = True

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

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

                        print(f"\n🧬 MESSAGE RECEIVED")
                        print(f"   From: {message.source}")
                        print(f"   Type: {message.type}")
                        print(f"   Priority: {message.priority}")
                        print(f"   Time: {message.timestamp}")

                        if message.target and message.target != self.my_id:
                            print(f"   Target: {message.target} (not for us)")
                            continue

                        print("\n📝 MESSAGE CONTENT:")
                        print("=" * 60)

                        # Handle different message types
                        if message.type == MessageType.PROMPT_RESPONSE:
                            response = message.payload.get("response", "")
                            status = message.payload.get("status", "unknown")
                            print(f"Status: {status}")
                            print(f"\nResponse:\n{response}")

                        elif message.type == MessageType.SPORE_REQUEST:
                            spore_name = message.payload.get("spore_name", "")
                            description = message.payload.get("description", "")
                            print(f"Spore Requested: {spore_name}")
                            print(f"Description: {description}")

                        else:
                            # Generic payload display
                            for key, value in message.payload.items():
                                if isinstance(value, str) and len(value) > 200:
                                    print(
                                        f"{key}:\n{value[:200]}...\n[TRUNCATED - {len(value)} total chars]"
                                    )
                                else:
                                    print(f"{key}: {value}")

                        print("=" * 60)
                        print("👂 Continuing to listen...")

                    except Exception as e:
                        print(f"❌ Error processing message: {e}")
                        print(f"   Raw data: {raw_message['data']}")

        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
            self.should_exit = True
        except Exception as e:
            print(f"❌ Connection error: {e}")
        finally:
            if self.should_exit:
                await self.send_goodbye_message()
            if self.client:
                await self.client.aclose()
            print("🔌 Disconnected from Beast Mode network")


async def main():
    listener = ConversationalListener()
    await listener.peek_and_listen()


if __name__ == "__main__":
    asyncio.run(main())
