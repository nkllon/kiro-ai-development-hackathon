#!/usr/bin/env python3
"""
Test Redis Connection - Beast Mode Observatory
Tests connection to Beast Mode Redis on port 6380
"""

import os
import sys

try:
    import redis
except ImportError:
    print("❌ redis package not installed")
    print("   Run: pip install redis")
    sys.exit(1)


def test_beast_mode_redis():
    """Test Beast Mode Redis instance on port 6380"""
    print("=" * 60)
    print("Testing Beast Mode Redis Connection (Port 6380)")
    print("=" * 60)
    print()
    
    # Configuration
    host = os.getenv('REDIS_HOST', 'localhost')
    port = int(os.getenv('REDIS_PORT', 6380))
    password = os.getenv('REDIS_PASSWORD', 'beastmode2025')
    
    print(f"Configuration:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Password: {'*' * len(password)}")
    print()
    
    try:
        # Connect to Beast Mode Redis
        print("1. Testing connection...")
        r = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Test PING
        result = r.ping()
        print(f"   ✅ PING: {result}")
        
        # Test SET/GET
        print("\n2. Testing basic operations...")
        test_key = 'beast_mode:connection_test'
        test_value = 'Connection successful!'
        
        r.set(test_key, test_value)
        retrieved = r.get(test_key)
        
        if retrieved == test_value:
            print(f"   ✅ SET/GET: Working")
        else:
            print(f"   ❌ SET/GET: Failed (expected '{test_value}', got '{retrieved}')")
            return False
        
        # Test stream operations
        print("\n3. Testing stream operations...")
        stream_name = 'test_stream'
        message_id = r.xadd(stream_name, {'test': 'message', 'timestamp': 'now'})
        print(f"   ✅ XADD: {message_id}")
        
        length = r.xlen(stream_name)
        print(f"   ✅ XLEN: {length}")
        
        # Clean up test stream
        r.delete(stream_name)
        
        # Test pub/sub (basic check)
        print("\n4. Testing pub/sub...")
        pubsub = r.pubsub()
        pubsub.subscribe('test_channel')
        print(f"   ✅ SUBSCRIBE: test_channel")
        
        r.publish('test_channel', 'test message')
        print(f"   ✅ PUBLISH: test message")
        
        pubsub.unsubscribe('test_channel')
        pubsub.close()
        
        # Get server info
        print("\n5. Server information...")
        info = r.info('server')
        print(f"   Redis Version: {info.get('redis_version', 'unknown')}")
        print(f"   OS: {info.get('os', 'unknown')}")
        print(f"   Uptime: {info.get('uptime_in_seconds', 0)} seconds")
        
        # Memory info
        memory_info = r.info('memory')
        used_memory = memory_info.get('used_memory_human', 'unknown')
        print(f"   Memory Used: {used_memory}")
        
        # Database info
        print("\n6. Database information...")
        dbsize = r.dbsize()
        print(f"   Total Keys: {dbsize}")
        
        # Clean up test key
        r.delete(test_key)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("Beast Mode Redis is ready to use on port 6380")
        print()
        
        return True
        
    except redis.ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check if Redis container is running:")
        print("     docker ps | grep beast-mode-redis")
        print()
        print("  2. Check port mapping:")
        print("     docker port beast-mode-redis")
        print()
        print("  3. Check if port 6380 is accessible:")
        print("     redis-cli -p 6380 -a beastmode2025 ping")
        print()
        print("  4. Check Docker logs:")
        print("     docker-compose -f docker-compose.redis.yml logs redis")
        return False
        
    except redis.AuthenticationError as e:
        print(f"\n❌ Authentication Error: {e}")
        print()
        print("Check REDIS_PASSWORD environment variable or password in docker-compose.redis.yml")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_existing_cluster():
    """Check if existing Redis cluster is accessible (optional)"""
    print("=" * 60)
    print("Checking Existing Redis Cluster (Port 6379)")
    print("=" * 60)
    print()
    
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=2)
        result = r.ping()
        print(f"✅ Existing cluster on 6379: Accessible ({result})")
        print("   Note: Beast Mode Redis on 6380 will not interfere")
    except Exception as e:
        print(f"ℹ️  Existing cluster on 6379: Not accessible from localhost")
        print(f"   (This is fine - may be network-only or protected)")
    
    print()


if __name__ == '__main__':
    print()
    
    # Check existing cluster (informational)
    check_existing_cluster()
    
    # Test Beast Mode Redis
    success = test_beast_mode_redis()
    
    sys.exit(0 if success else 1)


