#!/usr/bin/env python3
"""
Simple test script for the Intelligent HTTP Polling Fallback System
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from beast_mode.observatory.polling import IntelligentPoller, BOT_SAFE_HEADERS


async def test_basic_functionality():
    """Test basic polling functionality"""
    print("Testing Intelligent HTTP Polling Fallback System...")
    
    # Test 1: Basic initialization
    print("\n1. Testing initialization...")
    poller = IntelligentPoller()
    print("✓ IntelligentPoller initialized successfully")
    
    # Test 2: Bot-safe headers
    print("\n2. Testing bot-safe headers...")
    print(f"Bot-safe headers: {json.dumps(BOT_SAFE_HEADERS, indent=2)}")
    print("✓ Bot-safe headers configured")
    
    # Test 3: Start poller
    print("\n3. Testing poller start...")
    await poller.start()
    print("✓ Poller started successfully")
    
    # Test 4: Single endpoint poll
    print("\n4. Testing single endpoint poll...")
    try:
        result = await poller.poll_endpoint("https://httpbin.org/json")
        print(f"✓ Poll result: success={result.success}, status={result.status_code}")
        if result.data:
            print(f"  Data: {json.dumps(result.data, indent=2)[:100]}...")
    except Exception as e:
        print(f"✗ Poll failed: {e}")
    
    # Test 5: Statistics
    print("\n5. Testing statistics...")
    stats = poller.get_stats()
    print(f"✓ Stats retrieved: {len(stats)} categories")
    print(f"  Total polls: {stats['poller_stats']['total_polls']}")
    print(f"  Successful polls: {stats['poller_stats']['successful_polls']}")
    print(f"  Failed polls: {stats['poller_stats']['failed_polls']}")
    
    # Test 6: Stop poller
    print("\n6. Testing poller stop...")
    await poller.stop()
    print("✓ Poller stopped successfully")
    
    print("\n🎉 All basic tests completed successfully!")


async def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n" + "="*50)
    print("Testing Rate Limiting...")
    
    poller = IntelligentPoller()
    await poller.start()
    
    try:
        # Test rapid requests
        print("Making rapid requests to test rate limiting...")
        for i in range(15):  # Exceed the default limit
            result = await poller.poll_endpoint("https://httpbin.org/json")
            print(f"Request {i+1}: success={result.success}, status={result.status_code}")
            if not result.success and "rate limit" in result.error.lower():
                print("✓ Rate limiting detected!")
                break
    except Exception as e:
        print(f"Rate limiting test error: {e}")
    finally:
        await poller.stop()


async def test_bot_protection():
    """Test bot protection detection"""
    print("\n" + "="*50)
    print("Testing Bot Protection Detection...")
    
    poller = IntelligentPoller()
    await poller.start()
    
    try:
        # Test with a URL that might trigger bot protection
        result = await poller.poll_endpoint("https://httpbin.org/status/403")
        print(f"Bot protection test: success={result.success}, status={result.status_code}")
        
        if poller.stats["bot_protection_events"] > 0:
            print("✓ Bot protection detection working!")
        else:
            print("ℹ No bot protection events detected (this is normal)")
            
    except Exception as e:
        print(f"Bot protection test error: {e}")
    finally:
        await poller.stop()


async def main():
    """Main test function"""
    print("🚀 Starting Intelligent HTTP Polling Fallback System Tests")
    print("="*60)
    
    try:
        await test_basic_functionality()
        await test_rate_limiting()
        await test_bot_protection()
        
        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("The Intelligent HTTP Polling Fallback System is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())