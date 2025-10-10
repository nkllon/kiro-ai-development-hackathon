#!/usr/bin/env python3
"""
Validate WebSocket Routes in Observatory Server
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def validate_websocket_routes():
    """Validate that WebSocket routes are properly registered"""
    try:
        from beast_mode.observatory.server import create_server
        
        print("🔍 Validating WebSocket Routes in Observatory Server")
        print("=" * 60)
        
        # Create server instance
        server = create_server()
        
        # Get all routes
        routes = server.app.routes
        
        print(f"📋 Total routes registered: {len(routes)}")
        
        # Find WebSocket routes
        websocket_routes = []
        http_routes = []
        
        for route in routes:
            if hasattr(route, 'path'):
                if route.path.startswith('/ws/'):
                    websocket_routes.append({
                        'path': route.path,
                        'methods': getattr(route, 'methods', ['WebSocket']),
                        'endpoint': getattr(route, 'endpoint', {}).__name__ if hasattr(getattr(route, 'endpoint', None), '__name__') else 'Unknown'
                    })
                else:
                    http_routes.append(route.path)
        
        print(f"\n🌐 WebSocket Routes Found: {len(websocket_routes)}")
        print("-" * 40)
        
        expected_endpoints = [
            "/ws/emoji-rain",
            "/ws/observatory", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
        
        all_found = True
        for endpoint in expected_endpoints:
            found = False
            for route in websocket_routes:
                if route['path'] == endpoint:
                    print(f"✅ {endpoint}")
                    print(f"   Handler: {route['endpoint']}")
                    found = True
                    break
            
            if not found:
                print(f"❌ {endpoint} - NOT FOUND")
                all_found = False
        
        print(f"\n📊 Route Summary:")
        print(f"  Total routes: {len(routes)}")
        print(f"  WebSocket routes: {len(websocket_routes)}")
        print(f"  HTTP routes: {len(http_routes)}")
        print(f"  Expected WebSocket endpoints: {len(expected_endpoints)}")
        print(f"  All endpoints found: {'✅ YES' if all_found else '❌ NO'}")
        
        # Show some HTTP routes for context
        print(f"\n📄 Sample HTTP Routes:")
        for route in http_routes[:10]:  # Show first 10
            print(f"  {route}")
        
        return all_found
        
    except Exception as e:
        print(f"❌ Error validating routes: {e}")
        return False

if __name__ == "__main__":
    success = validate_websocket_routes()
    print(f"\n🎯 Validation Result: {'✅ PASS' if success else '❌ FAIL'}")
    exit(0 if success else 1)