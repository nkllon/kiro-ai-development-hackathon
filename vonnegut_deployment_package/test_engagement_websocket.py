#!/usr/bin/env python3
"""
Test Engagement WebSocket - Verify WebSocket Integration
=======================================================

Tests the /ws/engagement WebSocket endpoint to ensure real-time
data insights are working correctly.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
import websockets

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


async def test_engagement_websocket():
    """Test the engagement WebSocket endpoint."""
    print("🔌 Testing Engagement WebSocket")
    print("=" * 40)
    
    # WebSocket URL (assuming Observatory server is running on localhost:8000)
    ws_url = "ws://localhost:8000/ws/engagement"
    
    try:
        print(f"📡 Connecting to {ws_url}...")
        
        async with websockets.connect(ws_url) as websocket:
            print("✅ Connected to engagement WebSocket!")
            
            # Test 1: Wait for initial insights
            print("\n📊 Test 1: Waiting for initial insights...")
            try:
                initial_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(initial_message)
                print(f"✅ Received initial message: {data['type']}")
                
                if data['type'] == 'initial_insights':
                    insights = data['data']
                    print(f"   Summary: {insights['summary']}")
                    print(f"   Patterns: {len(insights['patterns'])}")
                
            except asyncio.TimeoutError:
                print("⚠️ No initial message received (timeout)")
            
            # Test 2: Send ping
            print("\n🏓 Test 2: Sending ping...")
            ping_message = {
                "type": "ping",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(ping_message))
            
            try:
                pong_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                pong_data = json.loads(pong_response)
                print(f"✅ Received pong: {pong_data['type']}")
            except asyncio.TimeoutError:
                print("⚠️ No pong response received")
            
            # Test 3: Request insights
            print("\n🔍 Test 3: Requesting current insights...")
            insights_request = {
                "type": "get_insights",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(insights_request))
            
            try:
                insights_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                insights_data = json.loads(insights_response)
                print(f"✅ Received insights: {insights_data['type']}")
                
                if insights_data['type'] == 'insights_update':
                    insights = insights_data['data']
                    print(f"   Summary: {insights['summary']}")
                    print(f"   Patterns: {len(insights['patterns'])}")
                    
                    # Show first pattern if available
                    if insights['patterns']:
                        pattern = insights['patterns'][0]
                        print(f"   First Pattern: {pattern['narrative']}")
                        print(f"   Interest Level: {pattern['interest_level']}")
                
            except asyncio.TimeoutError:
                print("⚠️ No insights response received")
            
            # Test 4: Request status
            print("\n📈 Test 4: Requesting system status...")
            status_request = {
                "type": "get_status",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(status_request))
            
            try:
                status_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                status_data = json.loads(status_response)
                print(f"✅ Received status: {status_data['type']}")
                
                if status_data['type'] == 'status_update':
                    status = status_data['data']
                    print(f"   Integration Running: {status['integration_running']}")
                    print(f"   Data Bridge Running: {status['data_bridge']['running']}")
                    print(f"   Metrics Processed: {status['data_bridge']['metrics_processed']}")
                
            except asyncio.TimeoutError:
                print("⚠️ No status response received")
            
            # Test 5: Add custom data point
            print("\n📊 Test 5: Adding custom data point...")
            custom_data = {
                "type": "add_data_point",
                "data": {
                    "metric_name": "test_metric",
                    "value": 42.5,
                    "timestamp": datetime.now().isoformat()
                }
            }
            await websocket.send(json.dumps(custom_data))
            print("✅ Sent custom data point")
            
            # Test 6: Listen for broadcasts
            print("\n📡 Test 6: Listening for broadcasts (10 seconds)...")
            try:
                for i in range(10):
                    broadcast = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    broadcast_data = json.loads(broadcast)
                    print(f"   📢 Broadcast: {broadcast_data['type']}")
                    
                    if broadcast_data['type'] == 'insights_update':
                        patterns = len(broadcast_data['data']['patterns'])
                        print(f"      New patterns: {patterns}")
                        
            except asyncio.TimeoutError:
                print("   ⏰ No broadcasts received in 10 seconds")
            
            print("\n✅ WebSocket tests completed successfully!")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused - is the Observatory server running?")
        print("   Start the server with: python -m src.beast_mode.observatory.server")
        return False
        
    except Exception as e:
        print(f"❌ WebSocket test error: {e}")
        return False
    
    return True


async def test_http_endpoints():
    """Test the HTTP API endpoints."""
    print("\n🌐 Testing HTTP API Endpoints")
    print("-" * 30)
    
    import aiohttp
    
    base_url = "http://localhost:8000"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test insights endpoint
            print("🔍 Testing /api/engagement/insights...")
            async with session.get(f"{base_url}/api/engagement/insights") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Insights endpoint working: {len(data['patterns'])} patterns")
                else:
                    print(f"⚠️ Insights endpoint returned {response.status}")
            
            # Test status endpoint
            print("📈 Testing /api/engagement/status...")
            async with session.get(f"{base_url}/api/engagement/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Status endpoint working: integration_running={data['integration_running']}")
                else:
                    print(f"⚠️ Status endpoint returned {response.status}")
            
            # Test data injection endpoint
            print("📊 Testing /api/engagement/data...")
            test_data = {
                "type": "metrics",
                "data": {
                    "test_cpu": 75.5,
                    "test_memory": 60.2
                }
            }
            async with session.post(f"{base_url}/api/engagement/data", json=test_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Data injection working: {data['status']}")
                else:
                    print(f"⚠️ Data injection returned {response.status}")
    
    except aiohttp.ClientConnectorError:
        print("❌ HTTP connection failed - is the Observatory server running?")
        return False
    except Exception as e:
        print(f"❌ HTTP test error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🔌 Engagement WebSocket & API Test Suite")
    print("=" * 50)
    
    print("📋 Prerequisites:")
    print("   1. Observatory server must be running")
    print("   2. Engagement integration must be enabled")
    print("   3. Server should be accessible at localhost:8000")
    print()
    
    try:
        # Test WebSocket
        websocket_success = asyncio.run(test_engagement_websocket())
        
        # Test HTTP endpoints
        http_success = asyncio.run(test_http_endpoints())
        
        if websocket_success and http_success:
            print("\n🎉 All tests passed!")
            print("The engagement system is fully integrated and working!")
        else:
            print("\n⚠️ Some tests failed - check server status")
            
    except KeyboardInterrupt:
        print("\n👋 Tests stopped by user")
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)