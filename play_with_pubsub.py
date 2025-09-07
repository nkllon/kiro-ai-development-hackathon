#!/usr/bin/env python3
"""
Play with Beast Mode Pub/Sub System
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode.messaging.pubsub import PubSubManager, BeastModeMessage, MessageType, MessageHandler
from datetime import datetime
import uuid
from typing import List, Optional


class PlaygroundHandler(MessageHandler):
    """Handler for playing with messages"""
    
    def __init__(self, name: str):
        self.name = name
        self.messages_handled = 0
    
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle incoming message"""
        self.messages_handled += 1
        
        print(f"\n🎮 {self.name} Handler received message:")
        print(f"   ID: {message.id}")
        print(f"   Type: {message.type}")
        print(f"   From: {message.source}")
        print(f"   Payload: {message.payload}")
        print(f"   Priority: {message.priority}")
        print(f"   Handled: {self.messages_handled} messages")
        
        # Send back a response for prompts
        if message.type == MessageType.PROMPT_REQUEST:
            response = BeastModeMessage(
                id=f"response_{message.id}",
                type=MessageType.PROMPT_RESPONSE,
                source=f"{self.name}_handler",
                target=message.source,
                payload={
                    "original_prompt": message.payload.get("prompt", ""),
                    "response": f"🧬 Beast Mode {self.name} processed your prompt!",
                    "handler": self.name,
                    "processed_at": datetime.now().isoformat()
                },
                timestamp=datetime.now(),
                correlation_id=message.id,
                priority=message.priority
            )
            return response
        
        return None
    
    def get_supported_types(self) -> List[MessageType]:
        """Return supported message types"""
        return [MessageType.PROMPT_REQUEST, MessageType.SPORE_SPAWN, MessageType.SYSTEM_HEALTH]


async def play_with_pubsub():
    """Interactive pub/sub playground"""
    print("🧬 Beast Mode Pub/Sub Playground")
    print("=" * 40)
    
    # Initialize pub/sub manager
    pubsub = PubSubManager("redis://localhost:6379")
    
    try:
        await pubsub.initialize()
        print("✅ Connected to Redis")
        
        # Create some handlers
        prompt_handler = PlaygroundHandler("PromptMaster")
        spore_handler = PlaygroundHandler("SporeSpawner")
        
        # Register handlers
        pubsub.register_handler(prompt_handler, "beast_mode")
        pubsub.register_handler(spore_handler, "spores")
        
        print("✅ Handlers registered")
        
        # Start listening
        await pubsub.start_listening(["beast_mode", "spores", "playground"])
        print("✅ Started listening on channels")
        
        print("\n🎮 Playground Commands:")
        print("  1 - Send prompt request")
        print("  2 - Spawn spore")
        print("  3 - Send health check")
        print("  4 - Show stats")
        print("  5 - Process queue")
        print("  q - Quit")
        
        while True:
            print("\n" + "=" * 40)
            command = input("🧬 Enter command (1-5, q): ").strip()
            
            if command == "q":
                break
            elif command == "1":
                prompt = input("Enter prompt: ")
                message_id = await pubsub.send_prompt_request(prompt, "playground", priority=8)
                print(f"✅ Sent prompt request: {message_id}")
                
            elif command == "2":
                spore_type = input("Enter spore type (default: tidb): ") or "tidb"
                message_id = await pubsub.send_spore_spawn_request(spore_type, {"test": True})
                print(f"✅ Sent spore spawn request: {message_id}")
                
            elif command == "3":
                health_message = BeastModeMessage(
                    id=str(uuid.uuid4()),
                    type=MessageType.SYSTEM_HEALTH,
                    source="playground",
                    target="health_monitor",
                    payload={
                        "status": "testing",
                        "component": "playground",
                        "timestamp": datetime.now().isoformat()
                    },
                    timestamp=datetime.now(),
                    priority=3
                )
                await pubsub.publish_message(health_message, "beast_mode")
                print(f"✅ Sent health check: {health_message.id}")
                
            elif command == "4":
                health = pubsub.get_health_status()
                print(f"\n📊 Pub/Sub Stats:")
                print(f"   Status: {health['status']}")
                print(f"   Listening: {health['is_listening']}")
                print(f"   Handlers: {health['registered_handlers']}")
                print(f"   Messages sent: {health['metrics']['messages_sent']}")
                print(f"   Messages received: {health['metrics']['messages_received']}")
                print(f"   Messages processed: {health['metrics']['messages_processed']}")
                print(f"   Errors: {health['metrics']['processing_errors']}")
                
            elif command == "5":
                processed = await pubsub.process_queue("beast_mode_queue", 5)
                print(f"✅ Processed {processed} messages from queue")
                
            else:
                print("❌ Invalid command")
            
            # Give messages time to process
            await asyncio.sleep(0.5)
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await pubsub.shutdown()
        print("🔌 Pub/Sub playground shutdown")


if __name__ == "__main__":
    asyncio.run(play_with_pubsub())