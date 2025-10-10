#!/usr/bin/env python3
"""
Targeted Node B Test
===================

Direct test of both Node B instances to see their individual responses.
"""

import asyncio
import json
import redis
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.security.secure_credentials import get_redis_password


async def test_individual_nodes():
    """Test each Node B instance individually."""
    
    # Connect to Redis
    redis_password = get_redis_password()
    client = redis.Redis(
        host="192.168.1.119",
        port=6379,
        password=redis_password,
        decode_responses=True
    )
    
    print("🎯 Testing Individual Node B Instances")
    print("=" * 45)
    
    # Test 1: Send message and see who responds
    test_message = {
        "sender": "targeted-test",
        "timestamp": datetime.now().isoformat(),
        "message": "Direct test - please identify yourself!",
        "test_type": "identification"
    }
    
    print("📤 Sending identification request...")
    client.publish("beast_mode_network", json.dumps(test_message))
    
    # Listen for responses
    pubsub = client.pubsub()
    pubsub.subscribe("beast_mode_network")
    
    responses = []
    
    print("👂 Listening for 10 seconds...")
    
    for i in range(100):  # 10 seconds
        message = pubsub.get_message(timeout=0.1)
        if message and message['type'] == 'message':
            data = json.loads(message['data'])
            
            # Skip our own message
            if data.get('sender') != 'targeted-test':
                responses.append(data)
                print(f"📨 Response from {data.get('node_id', 'unknown')}: {data.get('message', 'No message')}")
        
        await asyncio.sleep(0.1)
    
    pubsub.close()
    client.close()
    
    print(f"\n📊 Test Results:")
    print(f"   Total responses: {len(responses)}")
    
    # Analyze unique responders
    responders = set()
    for response in responses:
        responders.add(response.get('node_id', 'unknown'))
    
    print(f"   Unique responders: {len(responders)}")
    for responder in sorted(responders):
        print(f"   • {responder}")
    
    # Check expected nodes
    expected = {"simple-node-b", "node-b-vonnegut-container"}
    found = responders & expected
    
    if len(found) == 2:
        print("✅ Both Node B instances are responding!")
    elif len(found) == 1:
        print(f"⚠️  Only {list(found)[0]} is responding")
    else:
        print("❌ No expected Node B instances responding")


if __name__ == "__main__":
    asyncio.run(test_individual_nodes())