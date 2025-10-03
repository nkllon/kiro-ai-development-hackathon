#!/usr/bin/env python3
"""
WebSocket Connectivity Test Script
Tests WebSocket endpoints through Cloudflare tunnel
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime
import ssl

# WebSocket endpoints to test
WEBSOCKET_ENDPOINTS = [
    "wss://observatory.nkllon.com/ws/emoji-rain",
    "wss://observatory.nkllon.com/ws/observatory", 
    "wss://observatory.nkllon.com/ws/anomalies",
    "wss://observatory.nkllon.com/ws/doctor-status"
]

# Local endpoints for comparison
LOCAL_ENDPOINTS = [
    "ws://localhost:8888/ws/emoji-rain",
    "ws://localhost:8888/ws/observatory",
    "ws://localhost:8888/ws/anomalies", 
    "ws://localhost:8888/ws/doctor-status"
]

async def test_websocket_endpoint(uri, timeout=10):
    """Test a single WebSocket endpoint"""
    try:
        print(f"🔗 Testing: {uri}")
        
        # Create SSL context that doesn't verify certificates for testing
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Connect to WebSocket
        if uri.startswith('wss://'):
            websocket = await asyncio.wait_for(
                websockets.connect(uri, ssl=ssl_context), 
                timeout=timeout
            )
        else:
            websocket = await asyncio.wait_for(
                websockets.connect(uri), 
                timeout=timeout
            )
        
        print(f"✅ Connected to {uri}")
        
        # Send a test message
        test_message = {
            "type": "test",
            "timestamp": datetime.now().isoformat(),
            "message": "WebSocket connectivity test"
        }
        
        await websocket.send(json.dumps(test_message))
        print(f"📤 Sent test message to {uri}")
        
        # Try to receive a response (with timeout)
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"📥 Received response from {uri}: {response[:100]}...")
        except asyncio.TimeoutError:
            print(f"⏰ No response received from {uri} (timeout)")
        
        # Close connection
        await websocket.close()
        print(f"🔌 Closed connection to {uri}")
        
        return True, "Success"
        
    except asyncio.TimeoutError:
        return False, f"Connection timeout after {timeout}s"
    except websockets.exceptions.InvalidStatusCode as e:
        return False, f"Invalid status code: {e.status_code}"
    except websockets.exceptions.ConnectionClosedError as e:
        return False, f"Connection closed: {e.code} {e.reason}"
    except Exception as e:
        return False, f"Error: {str(e)}"

async def test_all_endpoints():
    """Test all WebSocket endpoints"""
    print("🔭 WebSocket Connectivity Test")
    print("=" * 50)
    
    results = {}
    
    # Test tunnel endpoints
    print("\n🌐 Testing Cloudflare Tunnel Endpoints:")
    print("-" * 40)
    for endpoint in WEBSOCKET_ENDPOINTS:
        success, message = await test_websocket_endpoint(endpoint)
        results[endpoint] = (success, message)
        if success:
            print(f"✅ {endpoint}: {message}")
        else:
            print(f"❌ {endpoint}: {message}")
        print()
    
    # Test local endpoints for comparison
    print("\n🏠 Testing Local Endpoints:")
    print("-" * 30)
    for endpoint in LOCAL_ENDPOINTS:
        success, message = await test_websocket_endpoint(endpoint)
        results[endpoint] = (success, message)
        if success:
            print(f"✅ {endpoint}: {message}")
        else:
            print(f"❌ {endpoint}: {message}")
        print()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 50)
    
    tunnel_success = sum(1 for ep in WEBSOCKET_ENDPOINTS if results[ep][0])
    local_success = sum(1 for ep in LOCAL_ENDPOINTS if results[ep][0])
    
    print(f"Tunnel Endpoints: {tunnel_success}/{len(WEBSOCKET_ENDPOINTS)} successful")
    print(f"Local Endpoints:  {local_success}/{len(LOCAL_ENDPOINTS)} successful")
    
    if tunnel_success == len(WEBSOCKET_ENDPOINTS):
        print("🎉 All tunnel WebSocket endpoints are working!")
        return True
    else:
        print("⚠️  Some tunnel WebSocket endpoints failed")
        return False

def test_http_endpoints():
    """Test HTTP endpoints for comparison"""
    import requests
    
    print("\n🌐 Testing HTTP Endpoints:")
    print("-" * 30)
    
    http_endpoints = [
        "https://observatory.nkllon.com/health",
        "http://localhost:8888/health"
    ]
    
    for endpoint in http_endpoints:
        try:
            response = requests.get(endpoint, timeout=10, verify=False)
            if response.status_code == 200:
                print(f"✅ {endpoint}: HTTP {response.status_code}")
            else:
                print(f"⚠️  {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")

if __name__ == "__main__":
    print("🔭 Observatory WebSocket Connectivity Test")
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    print()
    
    # Test HTTP endpoints first
    test_http_endpoints()
    
    # Test WebSocket endpoints
    try:
        success = asyncio.run(test_all_endpoints())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)