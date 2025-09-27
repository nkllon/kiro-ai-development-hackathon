#!/usr/bin/env python3
"""
WebSocket Connectivity Test Script

This script tests WebSocket connectivity through the Cloudflare tunnel
for all Observatory WebSocket endpoints.
"""

import asyncio
import websockets
import json
import time
import sys
from typing import List, Dict, Any

# WebSocket endpoints to test
WEBSOCKET_ENDPOINTS = [
    "/ws/emoji-rain",
    "/ws/observatory", 
    "/ws/anomalies",
    "/ws/doctor-status"
]

# Test URLs
LOCAL_URL = "ws://localhost:8888"
TUNNEL_URL = "wss://observatory.nkllon.com"

class WebSocketTester:
    """WebSocket connectivity tester."""
    
    def __init__(self):
        self.results = {}
    
    async def test_endpoint(self, endpoint: str, base_url: str) -> Dict[str, Any]:
        """Test a single WebSocket endpoint."""
        url = f"{base_url}{endpoint}"
        result = {
            "endpoint": endpoint,
            "url": url,
            "success": False,
            "error": None,
            "response_time": None,
            "message_received": False
        }
        
        try:
            print(f"🔍 Testing {url}...")
            start_time = time.time()
            
            async with websockets.connect(url, timeout=10) as websocket:
                result["response_time"] = time.time() - start_time
                result["success"] = True
                
                # Try to receive a message
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5)
                    result["message_received"] = True
                    result["first_message"] = message[:100] + "..." if len(message) > 100 else message
                except asyncio.TimeoutError:
                    result["message_received"] = False
                    result["note"] = "No message received within 5 seconds"
                
        except websockets.exceptions.ConnectionClosed as e:
            result["error"] = f"Connection closed: {e}"
        except websockets.exceptions.InvalidURI as e:
            result["error"] = f"Invalid URI: {e}"
        except websockets.exceptions.WebSocketException as e:
            result["error"] = f"WebSocket error: {e}"
        except asyncio.TimeoutError:
            result["error"] = "Connection timeout"
        except Exception as e:
            result["error"] = f"Unexpected error: {e}"
        
        return result
    
    async def test_all_endpoints(self, base_url: str) -> List[Dict[str, Any]]:
        """Test all WebSocket endpoints."""
        print(f"\n🌐 Testing WebSocket endpoints at {base_url}")
        print("-" * 50)
        
        results = []
        for endpoint in WEBSOCKET_ENDPOINTS:
            result = await self.test_endpoint(endpoint, base_url)
            results.append(result)
            
            # Print result
            if result["success"]:
                print(f"✅ {endpoint}: Connected ({result['response_time']:.2f}s)")
                if result["message_received"]:
                    print(f"   📨 Message received: {result.get('first_message', 'N/A')}")
                else:
                    print(f"   ⏳ {result.get('note', 'No message received')}")
            else:
                print(f"❌ {endpoint}: Failed - {result['error']}")
        
        return results
    
    def print_summary(self, local_results: List[Dict[str, Any]], 
                     tunnel_results: List[Dict[str, Any]]):
        """Print test summary."""
        print("\n📊 Test Summary")
        print("=" * 50)
        
        # Local results
        local_success = sum(1 for r in local_results if r["success"])
        print(f"🏠 Local WebSocket Tests: {local_success}/{len(local_results)} successful")
        
        # Tunnel results  
        tunnel_success = sum(1 for r in tunnel_results if r["success"])
        print(f"🌐 Tunnel WebSocket Tests: {tunnel_success}/{len(tunnel_results)} successful")
        
        # Detailed comparison
        print("\n📋 Detailed Results:")
        for i, endpoint in enumerate(WEBSOCKET_ENDPOINTS):
            local = local_results[i]
            tunnel = tunnel_results[i]
            
            print(f"\n🔗 {endpoint}:")
            print(f"   Local:   {'✅' if local['success'] else '❌'} {local.get('error', 'Connected')}")
            print(f"   Tunnel:  {'✅' if tunnel['success'] else '❌'} {tunnel.get('error', 'Connected')}")
            
            if local['success'] and tunnel['success']:
                print(f"   🎉 Both working! Local: {local['response_time']:.2f}s, Tunnel: {tunnel['response_time']:.2f}s")
            elif local['success'] and not tunnel['success']:
                print(f"   ⚠️  Tunnel issue detected - WebSocket proxy may not be configured")
            elif not local['success'] and tunnel['success']:
                print(f"   🤔 Unexpected: Tunnel works but local doesn't")
            else:
                print(f"   ❌ Both failed - check Observatory server")
    
    async def run_tests(self):
        """Run all WebSocket tests."""
        print("🧪 WebSocket Connectivity Test")
        print("=" * 50)
        
        # Test local endpoints
        local_results = await self.test_all_endpoints(LOCAL_URL)
        
        # Test tunnel endpoints
        tunnel_results = await self.test_all_endpoints(TUNNEL_URL)
        
        # Print summary
        self.print_summary(local_results, tunnel_results)
        
        # Return success status
        tunnel_success = sum(1 for r in tunnel_results if r["success"])
        return tunnel_success == len(WEBSOCKET_ENDPOINTS)

async def main():
    """Main function."""
    tester = WebSocketTester()
    success = await tester.run_tests()
    
    if success:
        print("\n🎉 All WebSocket endpoints are working through the tunnel!")
        return 0
    else:
        print("\n⚠️  Some WebSocket endpoints failed. Check the configuration.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)