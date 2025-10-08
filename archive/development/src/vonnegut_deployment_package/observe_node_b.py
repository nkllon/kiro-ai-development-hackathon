#!/usr/bin/env python3
"""
Node B Observer - Non-Blocking Diagnostics
==========================================

Observer-mode script to check Node B status without blocking operations.
"""

import os
import subprocess
import time
from pathlib import Path


def check_node_b_processes():
    """Check what Node B processes are running."""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        node_b_processes = [line for line in result.stdout.split('\n') 
                           if 'node_b' in line.lower() and 'grep' not in line]
        
        print("🔍 Node B Processes:")
        for process in node_b_processes:
            print(f"  {process}")
        
        return len(node_b_processes) > 0
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
        return False


def check_redis_activity():
    """Check Redis for Node B activity."""
    try:
        import redis
        from src.security.secure_credentials import get_redis_password
        
        client = redis.Redis(
            host="192.168.1.119",
            port=6379,
            password=get_redis_password(),
            decode_responses=True
        )
        
        # Check for Node B channels
        channels = client.pubsub_channels("*node*")
        print(f"🔍 Redis channels with 'node': {channels}")
        
        # Check for recent messages
        info = client.info()
        print(f"🔍 Redis connected clients: {info.get('connected_clients', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Redis check failed: {e}")
        return False


def generate_node_b_status_check():
    """Generate a status check script that can be run independently."""
    
    status_script = '''#!/usr/bin/env python3
"""
Quick Node B Status Check
========================
"""

import subprocess
import sys

def main():
    print("🔍 Node B Status Check")
    print("=" * 30)
    
    # Check processes
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        node_processes = [line for line in result.stdout.split('\\n') 
                         if 'launch_node_b' in line and 'grep' not in line]
        
        if node_processes:
            print("✅ Node B processes running:")
            for proc in node_processes:
                print(f"  {proc.split()[1]} - {proc.split()[-1]}")
        else:
            print("❌ No Node B processes found")
    except Exception as e:
        print(f"❌ Process check failed: {e}")
    
    # Check log files
    log_files = ['node_b_launch.log', 'node_b_infrastructure_fix.log']
    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                content = f.read().strip()
                if content:
                    print(f"📄 {log_file}: {len(content)} bytes")
                    print(f"   Last line: {content.split('\\n')[-1][:50]}...")
                else:
                    print(f"📄 {log_file}: Empty")
        except FileNotFoundError:
            print(f"📄 {log_file}: Not found")
    
    print("\\n🔧 To interact with Node B:")
    print("1. Check: python scripts/observe_node_b.py")
    print("2. Kill: pkill -f launch_node_b")
    print("3. Restart: python launch_node_b.py &")

if __name__ == "__main__":
    main()
'''
    
    with open('check_node_b_status.py', 'w') as f:
        f.write(status_script)
    
    print("✅ Generated: check_node_b_status.py")


def generate_node_b_interaction_script():
    """Generate script to interact with running Node B."""
    
    interaction_script = '''#!/usr/bin/env python3
"""
Node B Interaction Script
========================
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

async def send_test_message():
    """Send a test message to Node B."""
    try:
        from beast_mode.messaging import BeastModeBusClient, MessageType
        
        # Create test client
        client = BeastModeBusClient(
            agent_id="test-client",
            capabilities=["testing"]
        )
        
        print("📨 Sending test message to Node B...")
        
        # Send coordination message
        await client.send_message(
            "robust-node-b",
            MessageType.COORDINATION,
            {"test": "Hello Node B!", "timestamp": asyncio.get_event_loop().time()}
        )
        
        print("✅ Test message sent")
        client.close()
        
    except Exception as e:
        print(f"❌ Failed to send message: {e}")

if __name__ == "__main__":
    asyncio.run(send_test_message())
'''
    
    with open('interact_with_node_b.py', 'w') as f:
        f.write(interaction_script)
    
    print("✅ Generated: interact_with_node_b.py")


def main():
    """Main observer function - non-blocking diagnostics."""
    print("🔍 OBSERVING NODE B STATUS (Non-Blocking)")
    print("=" * 50)
    
    # Check if Node B is running
    has_processes = check_node_b_processes()
    
    # Check Redis activity
    redis_ok = check_redis_activity()
    
    # Generate helper scripts
    generate_node_b_status_check()
    generate_node_b_interaction_script()
    
    print("\n" + "=" * 50)
    print("📊 OBSERVER SUMMARY:")
    print(f"  Node B Processes: {'✅ Running' if has_processes else '❌ Not found'}")
    print(f"  Redis Connection: {'✅ OK' if redis_ok else '❌ Failed'}")
    
    print("\n🛠️ GENERATED TOOLS:")
    print("  • check_node_b_status.py - Quick status check")
    print("  • interact_with_node_b.py - Send test messages")
    
    print("\n🔧 SUGGESTED ACTIONS:")
    if has_processes:
        print("  1. Run: python check_node_b_status.py")
        print("  2. Test: python interact_with_node_b.py")
    else:
        print("  1. Restart: python launch_node_b.py &")
        print("  2. Monitor: tail -f node_b_launch.log")


if __name__ == "__main__":
    main()