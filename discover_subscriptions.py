#!/usr/bin/env python3
"""
Discover what channels and patterns the connected clients are subscribed to
"""

import redis
import json
import time
from datetime import datetime

def discover_active_subscriptions():
    """Try to discover what the connected clients are subscribed to"""
    print("🕵️ **DISCOVERING ACTIVE SUBSCRIPTIONS**")
    print("=" * 50)
    
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    # Strategy: Try publishing to many possible channels and see which ones have subscribers
    possible_channels = [
        # Standard Beast Mode channels
        'beast_mode_network',
        'beast_mode_general', 
        'beast_mode_messages',
        'beast_mode_heartbeats',
        'help_requests',
        
        # Agent-specific channels
        'agent_network',
        'agent_messages',
        'agent_status',
        'agent_heartbeat',
        
        # Collaboration channels
        'collaboration_network',
        'collaboration_messages',
        'spore_network',
        'spore_messages',
        
        # TIDB specific
        'tidb_network',
        'tidb_messages',
        'tidb_status',
        
        # Common patterns
        'network',
        'messages',
        'status',
        'heartbeat',
        'general',
        
        # Possible variations
        'beast-mode-network',
        'beast.mode.network',
        'beastmode_network',
        'beast_network',
        'mode_network'
    ]
    
    print("📡 **TESTING CHANNEL SUBSCRIPTIONS**")
    active_channels = []
    
    for channel in possible_channels:
        try:
            # Send a test message
            test_message = {
                'type': 'SUBSCRIPTION_TEST',
                'sender': 'DISCOVERY_TOOL',
                'timestamp': datetime.now().isoformat(),
                'channel_tested': channel,
                'message': f'Testing subscription to {channel}'
            }
            
            result = r.publish(channel, json.dumps(test_message))
            if result > 0:
                active_channels.append((channel, result))
                print(f"  ✅ {channel}: {result} subscriber(s)")
            else:
                print(f"  ⚪ {channel}: no subscribers")
                
        except Exception as e:
            print(f"  ❌ {channel}: error - {e}")
    
    print(f"\n📊 **ACTIVE CHANNELS FOUND: {len(active_channels)}**")
    for channel, count in active_channels:
        print(f"  📡 {channel}: {count} subscriber(s)")
    
    # Now test pattern subscriptions
    print(f"\n🔍 **TESTING PATTERN SUBSCRIPTIONS**")
    
    # Common patterns that might be used
    test_patterns = [
        'beast*',
        'agent*',
        'spore*', 
        'tidb*',
        'collaboration*',
        'network*',
        'message*',
        '*network',
        '*messages',
        '*status'
    ]
    
    pattern_matches = []
    
    for pattern in test_patterns:
        # Generate test channel names that would match this pattern
        test_channels = []
        
        if pattern.endswith('*'):
            base = pattern[:-1]
            test_channels = [
                f"{base}_test",
                f"{base}_network", 
                f"{base}_messages",
                f"{base}_status"
            ]
        elif pattern.startswith('*'):
            suffix = pattern[1:]
            test_channels = [
                f"test{suffix}",
                f"agent{suffix}",
                f"beast{suffix}",
                f"spore{suffix}"
            ]
        
        for test_channel in test_channels:
            try:
                result = r.publish(test_channel, json.dumps({
                    'type': 'PATTERN_TEST',
                    'pattern_tested': pattern,
                    'channel': test_channel
                }))
                
                if result > 0:
                    pattern_matches.append((pattern, test_channel, result))
                    print(f"  ✅ Pattern '{pattern}' matches '{test_channel}': {result} subscriber(s)")
                    
            except Exception as e:
                print(f"  ❌ Error testing {test_channel}: {e}")
    
    print(f"\n🎯 **PATTERN MATCHES FOUND: {len(pattern_matches)}**")
    for pattern, channel, count in pattern_matches:
        print(f"  🔍 Pattern '{pattern}' → '{channel}': {count} subscriber(s)")
    
    # Summary and recommendations
    print(f"\n💡 **DISCOVERY SUMMARY**")
    total_active = len(active_channels) + len(pattern_matches)
    
    if total_active > 0:
        print(f"  ✅ Found {total_active} active subscription(s)")
        print(f"  📡 Direct channels: {len(active_channels)}")
        print(f"  🔍 Pattern matches: {len(pattern_matches)}")
        
        if active_channels:
            print(f"\n  📋 **USE THESE CHANNELS TO COMMUNICATE:**")
            for channel, count in active_channels:
                print(f"    • {channel} ({count} listener(s))")
                
        if pattern_matches:
            print(f"\n  🎯 **THESE PATTERNS ARE ACTIVE:**")
            for pattern, channel, count in pattern_matches:
                print(f"    • Send to '{channel}' (matches pattern '{pattern}')")
    else:
        print(f"  ⚠️  No active subscriptions found")
        print(f"  💭 Agents might be using:")
        print(f"    • Different Redis instance")
        print(f"    • Queue-based messaging only") 
        print(f"    • Custom channel names not tested")
    
    return active_channels, pattern_matches

if __name__ == "__main__":
    discover_active_subscriptions()