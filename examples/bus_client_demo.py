#!/usr/bin/env python3
"""
Beast Mode Bus Client Demo

Demonstrates the basic functionality of the BeastModeBusClient including:
- Connection management
- Message sending and receiving
- Agent discovery
- Help requests
- Error handling
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.messaging import BeastModeBusClient, BeastModeMessage, MessageType


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_basic_functionality():
    """Demonstrate basic bus client functionality"""
    print("🧬 Beast Mode Bus Client Demo")
    print("=" * 50)
    
    # Create two clients to demonstrate communication
    client1 = BeastModeBusClient(
        agent_id="demo_agent_1",
        capabilities=["python_coding", "testing", "documentation"]
    )
    
    client2 = BeastModeBusClient(
        agent_id="demo_agent_2", 
        capabilities=["data_analysis", "testing", "optimization"]
    )
    
    try:
        # Connect both clients
        print("\n📡 Connecting to Redis...")
        connected1 = await client1.connect()
        connected2 = await client2.connect()
        
        if not (connected1 and connected2):
            print("❌ Failed to connect to Redis. Make sure Redis is running on localhost:6379")
            return
        
        print("✅ Both clients connected successfully")
        
        # Demonstrate health status
        print("\n📊 Client Health Status:")
        health1 = client1.get_health_status()
        print(f"   Agent 1: {health1['agent_id']} - Connected: {health1['is_connected']}")
        print(f"   Capabilities: {health1['capabilities']}")
        
        # Set up message collection for client2
        received_messages = []
        
        def message_callback(message: BeastModeMessage):
            received_messages.append(message)
            print(f"\n📨 Agent 2 received {message.type} from {message.source}")
            if message.payload:
                print(f"   Payload: {message.payload}")
        
        # Start listening on client2
        print("\n👂 Starting message listener on Agent 2...")
        listen_task = asyncio.create_task(
            client2.listen_for_messages(message_callback)
        )
        
        # Give listener time to start
        await asyncio.sleep(0.2)
        
        # Demonstrate agent discovery
        print("\n🔍 Demonstrating Agent Discovery...")
        await client1.announce_presence()
        await asyncio.sleep(0.5)  # Wait for response
        
        # Demonstrate simple messaging
        print("\n💬 Demonstrating Simple Messaging...")
        await client1.send_simple_message(
            "Hello from Agent 1! This is a test message.",
            target="demo_agent_2"
        )
        await asyncio.sleep(0.3)
        
        # Demonstrate help requests
        print("\n🆘 Demonstrating Help Requests...")
        await client1.send_help_request(
            required_capabilities=["testing", "data_analysis"],
            description="Need help with test data analysis"
        )
        await asyncio.sleep(0.5)
        
        # Demonstrate broadcast message
        print("\n📢 Demonstrating Broadcast Message...")
        await client1.send_simple_message(
            "This is a broadcast message to all agents!"
        )
        await asyncio.sleep(0.3)
        
        # Show statistics
        print("\n📈 Message Statistics:")
        stats1 = client1.get_health_status()['stats']
        stats2 = client2.get_health_status()['stats']
        
        print(f"   Agent 1 - Sent: {stats1['messages_sent']}, Received: {stats1['messages_received']}")
        print(f"   Agent 2 - Sent: {stats2['messages_sent']}, Received: {stats2['messages_received']}")
        
        # Show recent messages
        print(f"\n📋 Agent 2 Recent Messages ({len(received_messages)} total):")
        for i, msg in enumerate(received_messages[-3:], 1):  # Show last 3
            print(f"   {i}. {msg.type} from {msg.source}")
            if 'content' in msg.payload:
                print(f"      Content: {msg.payload['content']}")
        
        # Stop listening
        print("\n🛑 Stopping message listener...")
        client2.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(f"❌ Demo failed: {e}")
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        await client1.disconnect()
        await client2.disconnect()
        print("✅ Cleanup complete")


async def demo_error_handling():
    """Demonstrate error handling capabilities"""
    print("\n🚨 Error Handling Demo")
    print("=" * 30)
    
    # Test connection to non-existent Redis
    print("\n1. Testing connection failure handling...")
    bad_client = BeastModeBusClient(
        redis_url="redis://nonexistent:6379",
        agent_id="error_test"
    )
    
    result = await bad_client.connect()
    print(f"   Connection result: {result}")
    print(f"   Connection errors: {bad_client.stats['connection_errors']}")
    
    # Test sending without connection
    print("\n2. Testing send without connection...")
    try:
        await bad_client.send_simple_message("This should fail")
        print("   ❌ Unexpected success")
    except RuntimeError as e:
        print(f"   ✅ Correctly caught error: {e}")
    
    print("\n✅ Error handling demo complete")


async def main():
    """Main demo function"""
    try:
        await demo_basic_functionality()
        await demo_error_handling()
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    print("Starting Beast Mode Bus Client Demo...")
    print("Make sure Redis is running on localhost:6379")
    print("Press Ctrl+C to interrupt\n")
    
    asyncio.run(main())