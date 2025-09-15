#!/usr/bin/env python3
"""
Beast Mode Spore Receiver
Receives and consumes spores from the Beast Mode network
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import redis.asyncio as redis
    from pydantic import BaseModel
except ImportError:
    print("Installing dependencies...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "redis", "pydantic"])
    import redis.asyncio as redis
    from pydantic import BaseModel

from typing import Dict, Any, Optional
from enum import Enum


class MessageType(str, Enum):
    SPORE_BROADCAST = "spore_broadcast"
    SPORE_REQUEST = "spore_request"
    SPORE_RESPONSE = "spore_response"
    SPORE_CATALOG = "spore_catalog"


class BeastModeMessage(BaseModel):
    id: str
    type: MessageType
    source: str
    target: Optional[str]
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 5


class SporeReceiver:
    """Receive and consume Beast Mode spores from the network"""

    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis_url = redis_url
        self.client = None
        self.instance_id = f"spore_receiver_{uuid.uuid4().hex[:8]}"
        self.received_spores = {}
        self.available_catalog = {}

    async def connect(self):
        """Connect to Redis"""
        self.client = redis.from_url(self.redis_url)
        await self.client.ping()
        print(f"🧬 {self.instance_id} connected to Beast Mode network")

    async def listen_for_spores(self):
        """Listen for spore broadcasts and catalogs"""
        pubsub = self.client.pubsub()
        await pubsub.subscribe("beast_mode_network")

        print("📥 Listening for Beast Mode spores...")
        print("   Waiting for spore catalogs and broadcasts...")

        async for raw_message in pubsub.listen():
            if raw_message["type"] == "message":
                try:
                    data = json.loads(raw_message["data"])
                    message = BeastModeMessage(**data)

                    # Don't process our own messages
                    if message.source == self.instance_id:
                        continue

                    if message.type == MessageType.SPORE_CATALOG:
                        await self.handle_spore_catalog(message)
                    elif message.type == MessageType.SPORE_BROADCAST:
                        await self.handle_spore_broadcast(message)
                    elif message.type == MessageType.SPORE_RESPONSE:
                        await self.handle_spore_response(message)

                except Exception as e:
                    print(f"❌ Error processing message: {e}")

    async def handle_spore_catalog(self, message: BeastModeMessage):
        """Handle spore catalog broadcasts"""
        catalog = message.payload.get("catalog", {})
        distributor_id = message.payload.get("distributor_id", message.source)
        total_spores = message.payload.get("total_spores", 0)

        print(f"\n📋 Spore catalog from {distributor_id}")
        print(f"   Total spores available: {total_spores}")

        self.available_catalog.update(catalog)

        print("   Available spores:")
        for spore_name, info in catalog.items():
            size_kb = info["size"] / 1024
            print(f"     📦 {spore_name}: {size_kb:.1f}KB - {info['description']}")

    async def handle_spore_broadcast(self, message: BeastModeMessage):
        """Handle spore broadcasts"""
        spore_name = message.payload.get("spore_name", "unknown")
        spore_content = message.payload.get("spore_content", "")
        spore_size = message.payload.get("spore_size", 0)
        description = message.payload.get("description", "")

        print(f"\n🧬 Received spore broadcast: {spore_name}")
        print(f"   Size: {spore_size:,} bytes ({spore_size/1024:.1f}KB)")
        print(f"   Description: {description}")

        # Store the spore
        self.received_spores[spore_name] = {
            "content": spore_content,
            "size": spore_size,
            "description": description,
            "received_at": datetime.now().isoformat(),
            "source": message.source,
        }

        print(f"✅ Spore {spore_name} stored successfully")

    async def handle_spore_response(self, message: BeastModeMessage):
        """Handle direct spore responses"""
        if message.target != self.instance_id:
            return  # Not for us

        spore_name = message.payload.get("spore_name", "unknown")
        spore_content = message.payload.get("spore_content", "")
        spore_size = message.payload.get("spore_size", 0)

        print(f"\n📨 Received requested spore: {spore_name}")
        print(f"   Size: {spore_size:,} bytes ({spore_size/1024:.1f}KB)")

        # Store the spore
        self.received_spores[spore_name] = {
            "content": spore_content,
            "size": spore_size,
            "received_at": datetime.now().isoformat(),
            "source": message.source,
        }

        print(f"✅ Requested spore {spore_name} received and stored")

    async def request_spore(self, spore_name: str):
        """Request a specific spore from the network"""
        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.SPORE_REQUEST,
            source=self.instance_id,
            target=None,  # Broadcast request
            payload={
                "spore_name": spore_name,
                "requester_id": self.instance_id,
                "message": f"🧬 Requesting spore: {spore_name}",
            },
            timestamp=datetime.now(),
            priority=7,
        )

        await self.client.publish("beast_mode_network", message.model_dump_json())
        print(f"📤 Requested spore: {spore_name}")

    def save_spore(self, spore_name: str, output_dir: str = "received_spores"):
        """Save a received spore to disk"""
        if spore_name not in self.received_spores:
            print(f"❌ Spore {spore_name} not found in received spores")
            return False

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        spore_info = self.received_spores[spore_name]
        file_path = output_path / f"{spore_name}.md"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(spore_info["content"])

        print(f"💾 Saved spore {spore_name} to {file_path}")
        return True

    def list_received_spores(self):
        """List all received spores"""
        if not self.received_spores:
            print("📭 No spores received yet")
            return

        print(f"\n📦 Received Spores ({len(self.received_spores)}):")
        for spore_name, info in self.received_spores.items():
            size_kb = info["size"] / 1024
            print(f"   🧬 {spore_name}: {size_kb:.1f}KB (from {info['source']})")

    def list_available_spores(self):
        """List spores available in the network catalog"""
        if not self.available_catalog:
            print("📭 No spore catalog received yet")
            return

        print(f"\n📋 Available Spores ({len(self.available_catalog)}):")
        for spore_name, info in self.available_catalog.items():
            size_kb = info["size"] / 1024
            status = (
                "✅ Received" if spore_name in self.received_spores else "📥 Available"
            )
            print(f"   {status} {spore_name}: {size_kb:.1f}KB - {info['description']}")

    async def disconnect(self):
        """Disconnect from network"""
        if self.client:
            await self.client.aclose()
        print(f"🔌 {self.instance_id} disconnected")


async def main():
    """Main spore receiver function"""
    print("🧬 Beast Mode Spore Receiver")
    print("=" * 40)

    receiver = SporeReceiver()

    try:
        await receiver.connect()

        print("\n🎯 Receiver Options:")
        print("1. Listen for all spore broadcasts")
        print("2. Request specific spore")
        print("3. Interactive mode")

        choice = input("Select option (1-3): ").strip()

        if choice == "1":
            await receiver.listen_for_spores()

        elif choice == "2":
            spore_name = input("Enter spore name to request: ").strip()
            await receiver.request_spore(spore_name)

            # Listen for response
            print("📥 Waiting for spore response...")
            listener_task = asyncio.create_task(receiver.listen_for_spores())
            await asyncio.sleep(10)  # Wait 10 seconds for response
            listener_task.cancel()

        elif choice == "3":
            # Interactive mode
            listener_task = asyncio.create_task(receiver.listen_for_spores())

            print("\n🎮 Interactive Mode Commands:")
            print("  list - List received spores")
            print("  catalog - List available spores")
            print("  request <spore_name> - Request specific spore")
            print("  save <spore_name> - Save spore to disk")
            print("  save_all - Save all received spores")
            print("  quit - Exit")

            while True:
                try:
                    command = input("\n🧬 > ").strip().lower()

                    if command == "quit":
                        break
                    elif command == "list":
                        receiver.list_received_spores()
                    elif command == "catalog":
                        receiver.list_available_spores()
                    elif command.startswith("request "):
                        spore_name = command.replace("request ", "").strip()
                        await receiver.request_spore(spore_name)
                    elif command.startswith("save "):
                        spore_name = command.replace("save ", "").strip()
                        receiver.save_spore(spore_name)
                    elif command == "save_all":
                        for spore_name in receiver.received_spores.keys():
                            receiver.save_spore(spore_name)
                    else:
                        print("❌ Unknown command")

                except KeyboardInterrupt:
                    break

            listener_task.cancel()

        print("\n🎉 Spore reception complete!")

    except KeyboardInterrupt:
        print("\n🛑 Reception interrupted")
    except Exception as e:
        print(f"❌ Reception failed: {e}")
    finally:
        await receiver.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
