#!/usr/bin/env python3
"""
Test Node B Communication
========================

Simple script to test communication with Node B.
"""

import json
import redis
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.security.secure_credentials import get_redis_password


def test_node_b():
    """Test communication with Node B."""
    try:
        # Connect to Redis
        redis_password = get_redis_password()
        client = redis.Redis(
            host="192.168.1.119",
            port=6379,
            password=redis_password,
            decode_responses=True
        )
        
        # Test connection
        client.ping()
        print("✅ Connected to Redis")
        
        # Send a test message
        test_message = {
            "node_id": "test-client",
            "timestamp": datetime.now().isoformat(),
            "message": "Hello Node B! This is a test message.",
            "test": True
        }
        
        print(f"📤 Sending test message: {test_message['message']}")
        client.publish("beast_mode_network", json.dumps(test_message))
        
        # Listen for responses briefly
        pubsub = client.pubsub()
        pubsub.subscribe("beast_mode_network")
        
        print("👂 Listening for Node B response...")
        
        for i in range(30):  # Listen for 3 seconds
            message = pubsub.get_message(timeout=0.1)
            if message and message['type'] == 'message':
                data = json.loads(message['data'])
                if data.get('node_id') != 'test-client':
                    print(f"📨 Response from {data.get('node_id')}: {data.get('message')}")
                    break
        else:
            print("⏰ No response received within timeout")
        
        pubsub.close()
        client.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🧪 Testing Node B Communication...")
    test_node_b()