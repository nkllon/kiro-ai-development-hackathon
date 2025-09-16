#!/usr/bin/env python3
"""
Beast Mode Spore Distributor
Broadcasts spores to the Beast Mode network for systematic collaboration
"""

import asyncio
import json
import sys
import os
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

from typing import Dict, Any, Optional, List
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


class SporeDistributor:
    """Distribute Beast Mode spores across the network"""

    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis_url = redis_url
        self.client = None
        self.instance_id = f"spore_distributor_{uuid.uuid4().hex[:8]}"
        self.spore_catalog = {}

    async def connect(self):
        """Connect to Redis"""
        self.client = redis.from_url(self.redis_url)
        await self.client.ping()
        print(f"🧬 {self.instance_id} connected to Beast Mode network")

    async def load_spore_catalog(self):
        """Load all available spores"""
        spores_dir = Path("spores")
        if not spores_dir.exists():
            print("❌ No spores directory found")
            return

        print("📋 Loading spore catalog...")
        for spore_file in spores_dir.glob("*.md"):
            if spore_file.stat().st_size > 0:  # Skip empty files
                with open(spore_file, "r", encoding="utf-8") as f:
                    content = f.read()

                self.spore_catalog[spore_file.stem] = {
                    "name": spore_file.stem,
                    "size": len(content.encode("utf-8")),
                    "content": content,
                    "file_path": str(spore_file),
                    "last_modified": datetime.fromtimestamp(
                        spore_file.stat().st_mtime
                    ).isoformat(),
                }

        print(f"✅ Loaded {len(self.spore_catalog)} spores")
        for name, info in self.spore_catalog.items():
            print(f"   📦 {name}: {info['size']:,} bytes")

    async def broadcast_spore_catalog(self):
        """Broadcast available spores to the network"""
        catalog_info = {
            spore_name: {
                "name": info["name"],
                "size": info["size"],
                "last_modified": info["last_modified"],
                "description": self.extract_spore_description(info["content"]),
            }
            for spore_name, info in self.spore_catalog.items()
        }

        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.SPORE_CATALOG,
            source=self.instance_id,
            target=None,  # Broadcast to all
            payload={
                "catalog": catalog_info,
                "distributor_id": self.instance_id,
                "total_spores": len(catalog_info),
                "message": f"🧬 Beast Mode Spore Catalog available! {len(catalog_info)} spores ready for distribution.",
            },
            timestamp=datetime.now(),
            priority=6,
        )

        await self.client.publish("beast_mode_network", message.model_dump_json())
        print(f"📡 Broadcast spore catalog: {len(catalog_info)} spores available")

    async def broadcast_spore(self, spore_name: str):
        """Broadcast a specific spore to the network"""
        if spore_name not in self.spore_catalog:
            print(f"❌ Spore '{spore_name}' not found in catalog")
            return

        spore_info = self.spore_catalog[spore_name]

        message = BeastModeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.SPORE_BROADCAST,
            source=self.instance_id,
            target=None,  # Broadcast to all
            payload={
                "spore_name": spore_name,
                "spore_content": spore_info["content"],
                "spore_size": spore_info["size"],
                "last_modified": spore_info["last_modified"],
                "description": self.extract_spore_description(spore_info["content"]),
                "message": f"🧬 Broadcasting Beast Mode spore: {spore_name} ({spore_info['size']:,} bytes)",
            },
            timestamp=datetime.now(),
            priority=7,  # High priority for spore distribution
        )

        await self.client.publish("beast_mode_network", message.model_dump_json())
        print(f"📤 Broadcast spore: {spore_name} ({spore_info['size']:,} bytes)")

    def extract_spore_description(self, content: str) -> str:
        """Extract spore description from content"""
        lines = content.split("\n")
        for line in lines:
            if line.startswith("- **Purpose**:"):
                return line.replace("- **Purpose**:", "").strip()
        return "Beast Mode spore for systematic excellence"

    async def handle_spore_requests(self):
        """Listen for spore requests and respond"""
        pubsub = self.client.pubsub()
        await pubsub.subscribe("beast_mode_network")

        print("📥 Listening for spore requests...")

        async for raw_message in pubsub.listen():
            if raw_message["type"] == "message":
                try:
                    data = json.loads(raw_message["data"])
                    message = BeastModeMessage(**data)

                    # Don't process our own messages
                    if message.source == self.instance_id:
                        continue

                    if message.type == MessageType.SPORE_REQUEST:
                        await self.handle_spore_request(message)

                except Exception as e:
                    print(f"❌ Error processing message: {e}")

    async def handle_spore_request(self, message: BeastModeMessage):
        """Handle individual spore requests"""
        requesting_agent = message.source
        requested_spore = message.payload.get("spore_name", "")

        print(f"📨 Spore request from {requesting_agent}: {requested_spore}")

        if requested_spore in self.spore_catalog:
            spore_info = self.spore_catalog[requested_spore]

            response = BeastModeMessage(
                id=str(uuid.uuid4()),
                type=MessageType.SPORE_RESPONSE,
                source=self.instance_id,
                target=requesting_agent,
                payload={
                    "spore_name": requested_spore,
                    "spore_content": spore_info["content"],
                    "spore_size": spore_info["size"],
                    "last_modified": spore_info["last_modified"],
                    "message": f"🧬 Here's your requested spore: {requested_spore}",
                },
                timestamp=datetime.now(),
                priority=8,
            )

            await self.client.publish("beast_mode_network", response.model_dump_json())
            print(f"✅ Sent spore {requested_spore} to {requesting_agent}")
        else:
            print(f"❌ Requested spore {requested_spore} not available")

    async def disconnect(self):
        """Disconnect from network"""
        if self.client:
            await self.client.aclose()
        print(f"🔌 {self.instance_id} disconnected")


async def main():
    """Main spore distribution function"""
    print("🧬 Beast Mode Spore Distributor")
    print("=" * 40)

    distributor = SporeDistributor()

    try:
        # Connect and load spores
        await distributor.connect()
        await distributor.load_spore_catalog()

        if not distributor.spore_catalog:
            print("❌ No spores to distribute")
            return

        print("\n🎯 Distribution Options:")
        print("1. Broadcast spore catalog")
        print("2. Broadcast specific spore")
        print("3. Broadcast all spores")
        print("4. Listen for spore requests")
        print("5. Interactive mode")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == "1":
            await distributor.broadcast_spore_catalog()

        elif choice == "2":
            print("\nAvailable spores:")
            for i, name in enumerate(distributor.spore_catalog.keys(), 1):
                print(f"  {i}. {name}")

            spore_choice = input("Enter spore name: ").strip()
            if spore_choice in distributor.spore_catalog:
                await distributor.broadcast_spore(spore_choice)
            else:
                print(f"❌ Spore '{spore_choice}' not found")

        elif choice == "3":
            print("📡 Broadcasting all spores...")
            await distributor.broadcast_spore_catalog()
            await asyncio.sleep(2)  # Give catalog time to propagate

            for spore_name in distributor.spore_catalog.keys():
                await distributor.broadcast_spore(spore_name)
                await asyncio.sleep(1)  # Pace the broadcasts

        elif choice == "4":
            await distributor.broadcast_spore_catalog()
            await distributor.handle_spore_requests()

        elif choice == "5":
            # Interactive mode
            await distributor.broadcast_spore_catalog()

            # Start request handler in background
            request_task = asyncio.create_task(distributor.handle_spore_requests())

            print("\n🎮 Interactive Mode Commands:")
            print("  catalog - Broadcast spore catalog")
            print("  broadcast <spore_name> - Broadcast specific spore")
            print("  list - List available spores")
            print("  quit - Exit")

            while True:
                try:
                    command = input("\n🧬 > ").strip().lower()

                    if command == "quit":
                        break
                    elif command == "catalog":
                        await distributor.broadcast_spore_catalog()
                    elif command == "list":
                        print("\nAvailable spores:")
                        for name, info in distributor.spore_catalog.items():
                            print(f"  📦 {name}: {info['size']:,} bytes")
                    elif command.startswith("broadcast "):
                        spore_name = command.replace("broadcast ", "").strip()
                        if spore_name in distributor.spore_catalog:
                            await distributor.broadcast_spore(spore_name)
                        else:
                            print(f"❌ Spore '{spore_name}' not found")
                    else:
                        print("❌ Unknown command")

                except KeyboardInterrupt:
                    break

            request_task.cancel()

        print("\n🎉 Spore distribution complete!")

    except KeyboardInterrupt:
        print("\n🛑 Distribution interrupted")
    except Exception as e:
        print(f"❌ Distribution failed: {e}")
    finally:
        await distributor.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
