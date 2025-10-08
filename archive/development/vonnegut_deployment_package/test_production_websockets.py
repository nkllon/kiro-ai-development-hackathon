#!/usr/bin/env python3
"""
Production WebSocket connectivity test via Cloudflare
"""

import asyncio
import websockets
import json
import sys
import ssl
from datetime import datetime

async def test_production_websocket(uri):
    """Test production WebSocket connection through Cloudflare"""
    print(f"🌐 Testing production WebSocket: {uri}")
    
    try:
        # SSL context for secure connections
        ssl_context = ssl.create_default_context()
        
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            print(f"✅ Connected to {uri}")
            
            # Send ping message
            ping_msg = {
                "type": "ping",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(ping_msg))
            print(f"📨 Sent ping: {ping_msg}")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            print(f"📥 Received: {response}")
            
            return True
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")
        return False
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Invalid status code: {e}")
        print(f"   This likely means Cloudflare WebSocket support is not enabled")
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
    """Test production WebSocket endpoints through Cloudflare"""
    print("🌐 Production WebSocket Connectivity Test (Cloudflare)")
    print("=" * 60)
    
    base_url = "wss://observatory.nkllon.com"
    endpoints = [
        "/ws/emoji-rain",
        "/ws/observatory", 
        "/ws/anomalies",
        "/ws/doctor-status"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        uri = f"{base_url}{endpoint}"
        success = await test_production_websocket(uri)
        results[endpoint] = success
        print()
    
    print("📊 Production Results Summary:")
    print("-" * 40)
    success_count = sum(results.values())
    total_count = len(results)
    
    for endpoint, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{endpoint}: {status}")
    
    print(f"\nOverall: {success_count}/{total_count} production endpoints working")
    
    if success_count == 0:
        print("🚨 CRITICAL: Cloudflare WebSocket support not enabled")
        print("💡 Required: Enable WebSocket support in Cloudflare Dashboard")
        sys.exit(1)
    elif success_count < total_count:
        print("⚠️  WARNING: Some production WebSocket endpoints are not working")
        sys.exit(2)
    else:
        print("🎉 SUCCESS: All production WebSocket endpoints are functional")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
