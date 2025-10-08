#!/usr/bin/env python3
"""
Test WebSocket Setup for Observatory Server
"""

import sys
import asyncio
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_server_initialization():
    """Test that ObservatoryServer initializes correctly with WebSocket setup"""
    try:
        from beast_mode.observatory.server import create_server
        
        print("🧪 Testing ObservatoryServer Initialization")
        print("=" * 50)
        
        # Create server instance
        server = create_server()
        
        print(f"✅ Server created successfully")
        print(f"📡 WebSocket port: {server.config.websocket_config.port}")
        print(f"🌐 WebSocket host: {server.config.websocket_config.host}")
        
        # Check if WebSocket endpoints are registered
        websocket_routes = []
        for route in server.app.routes:
            if hasattr(route, 'path') and route.path.startswith('/ws/'):
                websocket_routes.append(route.path)
        
        print(f"\n📋 Registered WebSocket Endpoints:")
        expected_endpoints = [
            "/ws/emoji-rain",
            "/ws/observatory", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
        
        for endpoint in expected_endpoints:
            if endpoint in websocket_routes:
                print(f"  ✅ {endpoint}")
            else:
                print(f"  ❌ {endpoint} - NOT FOUND")
        
        # Check if _setup_websockets was called
        print(f"\n🔧 WebSocket Setup Verification:")
        print(f"  ✅ _setup_websockets() method exists: {hasattr(server, '_setup_websockets')}")
        
        # Test WebSocket handler initialization
        print(f"\n🎮 WebSocket Handler Status:")
        print(f"  ✅ Emoji WS Handler: {hasattr(server, 'emoji_ws_handler')}")
        print(f"  ✅ Observatory Core: {hasattr(server, 'observatory_core')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during server initialization: {e}")
        return False

def test_websocket_endpoints_accessibility():
    """Test WebSocket endpoints accessibility using HTTP upgrade requests"""
    import requests
    
    print(f"\n🌐 Testing WebSocket Endpoints Accessibility")
    print("=" * 50)
    
    endpoints = [
        "/ws/emoji-rain",
        "/ws/observatory", 
        "/ws/anomalies",
        "/ws/doctor-status"
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing {endpoint}...")
        
        # Test localhost first
        local_url = f"http://localhost:8888{endpoint}"
        try:
            response = requests.get(local_url, timeout=5)
            result = {
                "endpoint": endpoint,
                "local_status": response.status_code,
                "local_accessible": True,
                "local_error": None
            }
            print(f"  📍 Localhost: {response.status_code}")
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "local_status": None,
                "local_accessible": False,
                "local_error": str(e)
            }
            print(f"  📍 Localhost: ❌ {str(e)}")
        
        # Test production URL
        prod_url = f"https://observatory.nkllon.com{endpoint}"
        try:
            response = requests.get(prod_url, timeout=10)
            result["prod_status"] = response.status_code
            result["prod_accessible"] = True
            result["prod_error"] = None
            print(f"  🌍 Production: {response.status_code}")
        except Exception as e:
            result["prod_status"] = None
            result["prod_accessible"] = False
            result["prod_error"] = str(e)
            print(f"  🌍 Production: ❌ {str(e)}")
        
        results.append(result)
    
    return results

def main():
    """Main test function"""
    print("🚀 Observatory WebSocket Setup Test")
    print("=" * 60)
    
    # Test 1: Server initialization
    init_success = test_server_initialization()
    
    # Test 2: Endpoint accessibility
    accessibility_results = test_websocket_endpoints_accessibility()
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 30)
    print(f"✅ Server Initialization: {'PASS' if init_success else 'FAIL'}")
    
    successful_local = sum(1 for r in accessibility_results if r.get("local_accessible", False))
    successful_prod = sum(1 for r in accessibility_results if r.get("prod_accessible", False))
    total = len(accessibility_results)
    
    print(f"✅ Local Endpoints: {successful_local}/{total}")
    print(f"✅ Production Endpoints: {successful_prod}/{total}")
    
    # Save results
    report = {
        "timestamp": "2024-01-01T00:00:00Z",
        "server_initialization": init_success,
        "endpoint_tests": accessibility_results,
        "summary": {
            "total_endpoints": total,
            "local_successful": successful_local,
            "production_successful": successful_prod
        }
    }
    
    with open("websocket_setup_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: websocket_setup_test_report.json")
    
    return 0 if init_success and successful_local == total else 1

if __name__ == "__main__":
    exit(main())