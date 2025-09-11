#!/usr/bin/env python3
"""
Send a friendly hello message to the beast_mode_network
"""

import redis
import json
from datetime import datetime

def send_hello():
    """Send hello message to network"""
    print("👋 **SENDING HELLO TO BEAST MODE NETWORK**")
    
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    hello_message = {
        'type': 'HELLO',
        'sender': 'KIRO_HUMAN_TEAM',
        'timestamp': datetime.now().isoformat(),
        'message': 'Hello Beast Mode network! This is the human team checking in. Are you there TIDB?',
        'request': 'Please respond if you can see this message'
    }
    
    try:
        # Send to the main network channel
        result = r.publish('beast_mode_network', json.dumps(hello_message))
        print(f"📤 Hello message sent to beast_mode_network")
        print(f"📊 {result} subscribers received the message")
        
        if result > 0:
            print(f"✅ Message delivered to {result} agent(s)")
            print(f"💡 If they're programmed to respond, you should see a reply soon")
        else:
            print(f"⚠️  No subscribers received the message")
        
    except Exception as e:
        print(f"❌ Error sending message: {e}")

if __name__ == "__main__":
    send_hello()