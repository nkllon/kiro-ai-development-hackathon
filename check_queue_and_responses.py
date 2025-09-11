#!/usr/bin/env python3
"""
Check the beast_mode_messages queue and analyze responses more carefully
"""

import redis
import json
from datetime import datetime

def check_queue_and_analyze():
    """Check the message queue and analyze what's happening"""
    print("📋 **CHECKING MESSAGE QUEUE AND RESPONSES**")
    print("=" * 50)
    
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    # 1. Check the beast_mode_messages queue
    print("📬 **BEAST_MODE_MESSAGES QUEUE ANALYSIS**")
    try:
        queue_length = r.llen('beast_mode_messages')
        print(f"  📊 Queue length: {queue_length} messages")
        
        if queue_length > 0:
            # Get all messages in the queue
            messages = r.lrange('beast_mode_messages', 0, -1)
            
            print(f"\n📨 **MESSAGES IN QUEUE:**")
            for i, msg in enumerate(messages):
                try:
                    decoded = json.loads(msg.decode('utf-8'))
                    sender = decoded.get('sender', decoded.get('sender_id', 'unknown'))
                    msg_type = decoded.get('type', decoded.get('message_type', 'unknown'))
                    timestamp = decoded.get('timestamp', 'no_timestamp')
                    
                    print(f"  {i+1}. [{timestamp}] {sender} → {msg_type}")
                    
                    # Show content if it's interesting
                    content = decoded.get('content', decoded.get('message', ''))
                    if content:
                        if isinstance(content, dict):
                            if 'message' in content:
                                print(f"     💬 {content['message'][:100]}...")
                        else:
                            print(f"     💬 {str(content)[:100]}...")
                    
                except json.JSONDecodeError:
                    print(f"  {i+1}. Raw: {msg.decode('utf-8')[:100]}...")
                except Exception as e:
                    print(f"  {i+1}. Error decoding: {e}")
        else:
            print(f"  ⚪ Queue is empty")
            
    except Exception as e:
        print(f"❌ Error checking queue: {e}")
    
    # 2. Send a message to the queue and see if anyone processes it
    print(f"\n📤 **TESTING QUEUE-BASED COMMUNICATION**")
    
    queue_test_message = {
        'type': 'QUEUE_TEST',
        'sender': 'HUMAN_TEAM',
        'timestamp': datetime.now().isoformat(),
        'message': 'Testing queue-based communication. Please respond if you process queue messages.',
        'request': 'queue_status_check'
    }
    
    try:
        # Add message to queue
        r.lpush('beast_mode_messages', json.dumps(queue_test_message))
        print(f"  ✅ Added test message to queue")
        
        # Check queue length
        new_length = r.llen('beast_mode_messages')
        print(f"  📊 New queue length: {new_length}")
        
        # Wait a moment and check if it was processed
        import time
        print(f"  ⏳ Waiting 3 seconds to see if message is processed...")
        time.sleep(3)
        
        final_length = r.llen('beast_mode_messages')
        print(f"  📊 Final queue length: {final_length}")
        
        if final_length < new_length:
            print(f"  ✅ Message was processed! ({new_length - final_length} messages consumed)")
        else:
            print(f"  ⚠️  Message not processed (queue length unchanged)")
            
    except Exception as e:
        print(f"❌ Error testing queue: {e}")
    
    # 3. Try to identify what agents are actually running
    print(f"\n🔍 **IDENTIFYING ACTIVE AGENTS**")
    
    # Send a specific message asking for agent identification
    identification_message = {
        'type': 'AGENT_IDENTIFICATION_REQUEST',
        'sender': 'HUMAN_TEAM',
        'timestamp': datetime.now().isoformat(),
        'message': 'Please identify yourself: agent name, capabilities, and current status',
        'request_id': f"id_req_{int(time.time())}"
    }
    
    try:
        # Send via both pub/sub and queue
        pub_result = r.publish('beast_mode_network', json.dumps(identification_message))
        r.lpush('beast_mode_messages', json.dumps(identification_message))
        
        print(f"  📤 Identification request sent:")
        print(f"    📡 Pub/Sub: {pub_result} subscribers")
        print(f"    📬 Queue: added to beast_mode_messages")
        
        print(f"  ⏳ Waiting 5 seconds for identification responses...")
        time.sleep(5)
        
        # Check for responses in queue
        current_length = r.llen('beast_mode_messages')
        recent_messages = r.lrange('beast_mode_messages', 0, 4)  # Get recent messages
        
        print(f"\n📋 **RECENT QUEUE ACTIVITY:**")
        for msg in recent_messages:
            try:
                decoded = json.loads(msg.decode('utf-8'))
                sender = decoded.get('sender', 'unknown')
                msg_type = decoded.get('type', 'unknown')
                
                if sender != 'HUMAN_TEAM':  # Not our message
                    print(f"  📨 Response from {sender}: {msg_type}")
                    
            except:
                continue
                
    except Exception as e:
        print(f"❌ Error sending identification request: {e}")
    
    # 4. Summary and next steps
    print(f"\n💡 **ANALYSIS SUMMARY**")
    print(f"  📊 Current queue length: {r.llen('beast_mode_messages')}")
    print(f"  📡 Active pub/sub subscribers: 2 on beast_mode_network")
    print(f"  🔍 Agent behavior observed:")
    
    if final_length < new_length:
        print(f"    ✅ Agents ARE processing queue messages")
        print(f"    💡 Try using the queue for communication instead of pub/sub")
    else:
        print(f"    ⚠️  Agents may not be processing queue messages")
        print(f"    💡 They might be pub/sub only, or using different message formats")
    
    print(f"\n🎯 **NEXT STEPS:**")
    print(f"  1. Monitor the queue for a longer period")
    print(f"  2. Try different message formats in the queue")
    print(f"  3. Check if agents are running but not responding")
    print(f"  4. Look for agent log files or status indicators")

if __name__ == "__main__":
    check_queue_and_analyze()