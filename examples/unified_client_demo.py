#!/usr/bin/env python3
"""
Unified Beast Mode Client Demo

Demonstrates the new unified client interface with pluggable transports.
"""

import asyncio
import logging
from src.beast_mode.messaging.unified_client import BeastModeClient
from src.beast_mode.messaging.models import BeastModeMessage, MessageType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_unified_client():
    """Demonstrate unified client capabilities"""
    
    print("🚀 Beast Mode Unified Client Demo")
    print("=" * 50)
    
    # Create client with Redis transport (default)
    client = BeastModeClient(
        agent_id="demo_agent",
        transport_type="redis",  # Could be 'nats', 'kafka', etc.
        capabilities=["demonstration", "testing"],
        specializations=["unified_client"]
    )
    
    try:
        # Start the client
        print("\n1. Starting unified client...")
        success = await client.start()
        
        if not success:
            print("❌ Failed to start client")
            return
        
        print("✅ Client started successfully")
        
        # Show status
        print("\n2. Client Status:")
        status = client.get_status()
        print(f"   Agent ID: {status['agent_id']}")
        print(f"   Transport: {status['transport_type']}")
        print(f"   Started: {status['is_started']}")
        print(f"   Capabilities: {status['capabilities']}")
        
        # Show capabilities
        print("\n3. Client Capabilities:")
        capabilities = client.get_capabilities()
        print(f"   Agent Capabilities: {capabilities['agent_capabilities']}")
        print(f"   Transport Features: {list(capabilities['transport_capabilities'].keys())}")
        print(f"   Client Features: {capabilities['client_features']}")
        
        # Register message handlers
        print("\n4. Registering message handlers...")
        
        def handle_simple_message(message):
            print(f"   📨 Received: {message.payload.get('text', 'No text')}")
        
        def handle_help_request(message):
            print(f"   🆘 Help requested: {message.payload.get('topic', 'Unknown')}")
        
        client.register_handler(MessageType.SIMPLE_MESSAGE, handle_simple_message)
        client.register_handler(MessageType.HELP_WANTED, handle_help_request)
        
        print("✅ Handlers registered")
        
        # Discover other agents
        print("\n5. Discovering agents...")
        agents = await client.discover_agents()
        print(f"   Found {len(agents)} active agents: {agents}")
        
        # Send some messages
        print("\n6. Sending messages...")
        
        # Send a simple message
        await client.send_simple_message("other_agent", "Hello from unified client!")
        print("   ✅ Simple message sent")
        
        # Broadcast a message
        await client.broadcast_message("Broadcasting from unified client!")
        print("   ✅ Broadcast message sent")
        
        # Request help
        await client.request_help("unified_client_demo", "Testing the new unified client")
        print("   ✅ Help request sent")
        
        # Send a custom message
        custom_message = BeastModeMessage(
            type=MessageType.TECHNICAL_EXCHANGE,
            source=client.agent_id,
            payload={
                "topic": "unified_client_architecture",
                "details": "Demonstrating pluggable transport architecture",
                "transport_used": client.transport_type
            }
        )
        
        await client.send_message(custom_message)
        print("   ✅ Custom message sent")
        
        # Show updated statistics
        print("\n7. Updated Statistics:")
        status = client.get_status()
        stats = status['stats']
        print(f"   Messages sent: {stats['messages_sent']}")
        print(f"   Messages received: {stats['messages_received']}")
        print(f"   Last activity: {stats.get('last_activity', 'None')}")
        
        # Wait a bit for any incoming messages
        print("\n8. Listening for messages (5 seconds)...")
        await asyncio.sleep(5)
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        logger.exception("Demo failed")
        
    finally:
        # Clean shutdown
        print("\n9. Shutting down...")
        await client.stop()
        print("✅ Client stopped")


async def demo_transport_switching():
    """Demonstrate switching between different transports"""
    
    print("\n🔄 Transport Switching Demo")
    print("=" * 30)
    
    transports_to_test = ['redis']  # Add 'nats', 'kafka' when available
    
    for transport_type in transports_to_test:
        print(f"\n📡 Testing {transport_type} transport...")
        
        client = BeastModeClient(
            agent_id=f"test_{transport_type}",
            transport_type=transport_type,
            capabilities=[f"{transport_type}_testing"]
        )
        
        try:
            success = await client.start()
            if success:
                print(f"   ✅ {transport_type} transport working")
                
                # Send a test message
                await client.broadcast_message(f"Hello from {transport_type} transport!")
                
                # Show transport-specific capabilities
                caps = client.get_capabilities()
                transport_caps = caps['transport_capabilities']
                print(f"   📊 Transport capabilities: {list(transport_caps.keys())}")
                
            else:
                print(f"   ❌ {transport_type} transport failed to start")
                
        except Exception as e:
            print(f"   ❌ {transport_type} transport error: {e}")
            
        finally:
            await client.stop()


async def main():
    """Run all demos"""
    try:
        await demo_unified_client()
        await demo_transport_switching()
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.exception("Main demo failed")


if __name__ == "__main__":
    print("🎯 Starting Beast Mode Unified Client Demo")
    print("   This demonstrates the new pluggable transport architecture")
    print("   Press Ctrl+C to stop\n")
    
    asyncio.run(main())