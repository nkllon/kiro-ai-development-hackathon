#!/usr/bin/env python3
"""
Test WebSocket connectivity to Observatory
"""

import asyncio
import websockets
import json

async def test_websocket_endpoint(uri, endpoint_name):
    """Test a WebSocket endpoint."""
    try:
        print(f"🔌 Testing {endpoint_name} at {uri}")
        
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to {endpoint_name}")
            
            # Send test message
            test_message = {
                "type": "test",
                "message": f"Testing {endpoint_name}",
                "timestamp": str(asyncio.get_event_loop().time())
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent test message to {endpoint_name}")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                print(f"📥 Received from {endpoint_name}: {response[:100]}...")
                return True
            except asyncio.TimeoutError:
                print(f"⏰ No response from {endpoint_name} (timeout)")
                return True  # Connection worked, just no response
                
    except Exception as e:
        print(f"❌ Failed to connect to {endpoint_name}: {e}")
        return False

async def main():
    """Test all WebSocket endpoints."""
    print("🚀 Testing Observatory WebSocket endpoints...")
    
    endpoints = [
        ("ws://localhost:8888/ws/observatory", "Observatory WebSocket"),
        ("ws://localhost:8888/ws/emoji-rain", "Emoji Rain WebSocket"),
        ("ws://localhost:8888/ws/anomalies", "Anomalies WebSocket"),
        ("ws://localhost:8888/ws/doctor-status", "Doctor Status WebSocket")
    ]
    
    results = []
    for uri, name in endpoints:
        result = await test_websocket_endpoint(uri, name)
        results.append((name, result))
    
    print(f"\n🎯 WebSocket Test Results:")
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {name}")
    
    total_passed = sum(1 for _, success in results if success)
    print(f"\n📊 Summary: {total_passed}/{len(results)} WebSocket endpoints working")
    
    return total_passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)