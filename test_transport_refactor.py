#!/usr/bin/env python3
"""
Test the transport refactor to see if it actually works as designed.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from beast_mode.messaging.transport import TransportFactory
from beast_mode.messaging.redis_transport import RedisTransport
from beast_mode.messaging.models import BeastModeMessage, MessageType


async def test_transport_abstraction():
    """Test if our transport abstraction actually works"""
    print("🧪 Testing Beast Mode Transport Abstraction")
    print("=" * 50)
    
    try:
        # Register Redis transport
        print("1. Registering Redis transport...")
        TransportFactory.register_transport('redis', RedisTransport)
        available = TransportFactory.get_available_transports()
        print(f"   Available transports: {available}")
        
        # Create transport via factory
        print("2. Creating Redis transport via factory...")
        transport = TransportFactory.create_transport('redis', agent_id='TestAgent')
        print(f"   Created: {type(transport).__name__}")
        
        # Test capabilities
        print("3. Testing transport capabilities...")
        capabilities = transport.get_capabilities()
        print(f"   Capabilities: {capabilities}")
        
        # Test status (before initialization)
        print("4. Testing transport status...")
        status = transport.get_status()
        print(f"   Status: {status}")
        
        # Try to initialize
        print("5. Testing transport initialization...")
        init_result = await transport.initialize({})
        print(f"   Initialization result: {init_result}")
        
        print("\n✅ Basic transport abstraction works!")
        return True
        
    except Exception as e:
        print(f"\n❌ Transport abstraction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_message_sending():
    """Test if we can actually send messages through the transport"""
    print("\n🧪 Testing Message Sending")
    print("=" * 30)
    
    try:
        # Create transport
        transport = TransportFactory.create_transport('redis', agent_id='TestSender')
        
        # Create a test message
        test_message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source='TestSender',
            payload={'test': 'Hello from transport abstraction!'}
        )
        
        print(f"1. Created test message: {test_message.type}")
        
        # Try to send (this will probably fail since daemon isn't started)
        print("2. Attempting to send message...")
        send_result = await transport.send_message(test_message)
        print(f"   Send result: {send_result}")
        
        return send_result
        
    except Exception as e:
        print(f"❌ Message sending failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("🚀 Testing Beast Mode Transport Refactor")
    print("=" * 60)
    
    # Test 1: Basic abstraction
    abstraction_works = await test_transport_abstraction()
    
    # Test 2: Message sending
    messaging_works = await test_message_sending()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Transport Abstraction: {'✅ PASS' if abstraction_works else '❌ FAIL'}")
    print(f"Message Sending: {'✅ PASS' if messaging_works else '❌ FAIL'}")
    
    if abstraction_works:
        print("\n🎯 The transport abstraction approach looks viable!")
        print("   Next step: Fix the integration issues and test with real Redis")
    else:
        print("\n⚠️  The transport abstraction needs work before proceeding")
        print("   The spec might be too optimistic about the refactor complexity")


if __name__ == "__main__":
    asyncio.run(main())