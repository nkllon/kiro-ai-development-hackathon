#!/usr/bin/env python3
"""
Direct WebSocket connectivity test
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

async def test_websocket_endpoint(uri):
    """Test WebSocket connection to specific endpoint"""
    print(f"🔌 Testing WebSocket connection to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to {uri}")
            
            # Send ping message
            ping_msg = {
                "type": "ping",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(ping_msg))
            print(f"📨 Sent ping: {ping_msg}")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 Received: {response}")
            
            return True
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")
        return False
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
        return False
    except asyncio.TimeoutError:
        print(f"❌ Timeout waiting for response")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def main():
    """Test all WebSocket endpoints"""
    print("🧪 Direct WebSocket Connectivity Test")
    print("=" * 50)
    
    base_url = "ws://localhost:8888"
    endpoints = [
        "/ws/emoji-rain",
        "/ws/observatory", 
        "/ws/anomalies",
        "/ws/doctor-status"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        uri = f"{base_url}{endpoint}"
        success = await test_websocket_endpoint(uri)
        results[endpoint] = success
        print()
    
    print("📊 Results Summary:")
    print("-" * 30)
    success_count = sum(results.values())
    total_count = len(results)
    
    for endpoint, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{endpoint}: {status}")
    
    print(f"\nOverall: {success_count}/{total_count} endpoints working")
    
    if success_count == 0:
        print("🚨 CRITICAL: No WebSocket endpoints are functional")
        sys.exit(1)
    elif success_count < total_count:
        print("⚠️  WARNING: Some WebSocket endpoints are not working")
        sys.exit(2)
    else:
        print("🎉 SUCCESS: All WebSocket endpoints are functional")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
