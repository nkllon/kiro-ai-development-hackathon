#!/usr/bin/env python3
"""
Test Lab Communication - Connect to Network Redis Cluster
Tests ability to communicate with other agents in the lab
"""

import os
import sys

try:
    import redis
except ImportError:
    print("❌ redis package not installed")
    print("   Run: pip install redis")
    sys.exit(1)

try:
    from beast_mailbox_core import RedisMailboxService
except ImportError:
    print("❌ beast-mailbox-core not installed")
    print("   Run: pip install beast-mailbox-core")
    sys.exit(1)


def test_lab_cluster():
    """Test connection to lab Redis cluster (port 6379)"""
    print("=" * 70)
    print("Testing Lab Redis Cluster Connection (Port 6379)")
    print("=" * 70)
    print()
    
    # Configuration
    lab_host = os.getenv('LAB_REDIS_HOST', '192.168.1.119')
    lab_port = int(os.getenv('LAB_REDIS_PORT', 6379))
    lab_password = os.getenv('LAB_REDIS_PASSWORD', '')
    agent_id = os.getenv('AGENT_ID', 'devbox')
    
    print(f"Configuration:")
    print(f"  Lab Redis Host: {lab_host}")
    print(f"  Lab Redis Port: {lab_port}")
    print(f"  Lab Password: {'*' * len(lab_password) if lab_password else '(not set)'}")
    print(f"  Your Agent ID: {agent_id}")
    print()
    
    if not lab_password:
        print("⚠️  LAB_REDIS_PASSWORD not set!")
        print()
        print("To connect to the lab cluster, set:")
        print("  export LAB_REDIS_HOST=<cluster_ip>")
        print("  export LAB_REDIS_PASSWORD=<cluster_password>")
        print("  export AGENT_ID=devbox")
        print()
        print("Then run this script again.")
        return False
    
    try:
        # Connect to network Redis cluster
        print("1. Testing cluster connection...")
        network_redis = redis.Redis(
            host=lab_host,
            port=lab_port,
            password=lab_password,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Test PING
        result = network_redis.ping()
        print(f"   ✅ PING cluster: {result}")
        
        # List all agent mailboxes
        print("\n2. Discovering lab agents...")
        agent_keys = network_redis.keys('beast:mailbox:*:in')
        
        if agent_keys:
            agents = sorted([k.split(':')[2] for k in agent_keys])
            print(f"   ✅ Found {len(agents)} agent(s) in lab:")
            for agent in agents:
                stream_len = network_redis.xlen(f'beast:mailbox:{agent}:in')
                print(f"      - {agent:15} ({stream_len} messages)")
        else:
            print("   ℹ️  No agent mailboxes found yet")
            print("      (This might be the first agent!)")
        
        # Create mailbox service
        print("\n3. Creating mailbox service...")
        mailbox = RedisMailboxService(network_redis)
        print(f"   ✅ Mailbox service ready for '{agent_id}'")
        
        # Check your inbox
        print("\n4. Checking inbox...")
        inbox_stream = f'beast:mailbox:{agent_id}:in'
        
        # Check if inbox exists
        if network_redis.exists(inbox_stream):
            message_count = network_redis.xlen(inbox_stream)
            print(f"   ✅ Your inbox exists with {message_count} message(s)")
            
            if message_count > 0:
                # Read latest messages (non-destructive)
                messages = network_redis.xrevrange(inbox_stream, count=5)
                print(f"\n   Latest messages:")
                for msg_id, msg_data in messages:
                    sender = msg_data.get('sender', 'unknown')
                    msg_type = msg_data.get('message_type', 'unknown')
                    print(f"      📬 {msg_id}: From {sender} ({msg_type})")
        else:
            print(f"   ℹ️  Inbox doesn't exist yet (will be created on first message)")
        
        # Test send capability
        print("\n5. Testing send capability...")
        print(f"   ℹ️  To send a test message, run:")
        print(f"      beast-mailbox-send {agent_id} <recipient> \\")
        print(f"        --redis-host {lab_host} --redis-port {lab_port} \\")
        print(f"        --redis-password <password> \\")
        print(f"        --message 'Hello from {agent_id}!'")
        
        print("\n" + "=" * 70)
        print("✅ LAB CLUSTER CONNECTION SUCCESSFUL!")
        print("=" * 70)
        print()
        print(f"You can now communicate with lab agents:")
        if agent_keys:
            other_agents = [a for a in agents if a != agent_id]
            if other_agents:
                print(f"  Available: {', '.join(other_agents)}")
            else:
                print(f"  (Only you are in the lab so far)")
        print()
        print(f"Your mailbox: beast:mailbox:{agent_id}:in")
        print(f"Network cluster: {lab_host}:{lab_port}")
        print()
        
        return True
        
    except redis.ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print()
        print("Troubleshooting:")
        print(f"  1. Verify cluster is accessible:")
        print(f"     redis-cli -h {lab_host} -p {lab_port} -a <password> ping")
        print()
        print(f"  2. Check network connectivity:")
        print(f"     ping {lab_host}")
        print()
        print(f"  3. Verify credentials:")
        print(f"     echo $LAB_REDIS_PASSWORD")
        print()
        print(f"  4. Check firewall rules for port {lab_port}")
        return False
        
    except redis.AuthenticationError as e:
        print(f"\n❌ Authentication Error: {e}")
        print()
        print("Check LAB_REDIS_PASSWORD environment variable")
        print("It should match the cluster's requirepass setting")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_local_redis():
    """Quick check of local Redis (6380)"""
    print("=" * 70)
    print("Quick Check: Local Redis (Port 6380)")
    print("=" * 70)
    print()
    
    try:
        local_redis = redis.Redis(
            host='localhost',
            port=6380,
            password='beastmode2025',
            decode_responses=True,
            socket_connect_timeout=2
        )
        result = local_redis.ping()
        print(f"✅ Local Redis (6380): {result}")
        print(f"   Purpose: App internal state (Observatory, Task Queue, AI Consultation)")
    except Exception as e:
        print(f"❌ Local Redis (6380): Not running")
        print(f"   Run: docker-compose -f docker-compose.redis.yml up -d")
    
    print()


if __name__ == '__main__':
    print()
    
    # Quick check of local Redis
    test_local_redis()
    
    # Test lab cluster connection
    success = test_lab_cluster()
    
    if success:
        print("🎉 You're connected to the lab cluster!")
        print("   You can now send and receive messages to/from other agents")
        print()
        print("Next steps:")
        print("  - Send test message: beast-mailbox-send devbox herbert --message 'hi!'")
        print("  - Listen for messages: beast-mailbox-service devbox --verbose")
        print("  - Check your inbox: beast-mailbox-service devbox --latest --count 5")
    else:
        print("ℹ️  Lab cluster not accessible (yet)")
        print("   This is fine - local Redis (6380) still works for app functionality")
        print()
        print("To enable lab communication:")
        print("  1. Get cluster credentials from questionnaire")
        print("  2. Set LAB_REDIS_* environment variables")
        print("  3. Run this test again")
    
    print()
    sys.exit(0 if success else 1)



