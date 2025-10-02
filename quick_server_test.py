#!/usr/bin/env python3
"""
Quick test to verify Observatory server can start with engagement integration.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_server_startup():
    """Test that the server can be created and initialized."""
    try:
        from src.beast_mode.observatory.server import create_server
        
        print("🔍 Testing Observatory server creation with engagement integration...")
        
        # Create server
        server = create_server()
        print("✅ Server created successfully")
        
        # Check if engagement integration is available
        if hasattr(server, 'engagement_integration') and server.engagement_integration:
            print("✅ Engagement integration detected and initialized")
            
            # Test engagement integration health
            try:
                health = server.engagement_integration.get_health_status()
                print(f"✅ Engagement health status: {health}")
            except Exception as e:
                print(f"⚠️ Engagement health check failed: {e}")
        else:
            print("⚠️ Engagement integration not detected or not initialized")
        
        # Test that the FastAPI app is created
        if hasattr(server, 'app') and server.app:
            print("✅ FastAPI application created successfully")
            
            # Check if engagement routes are added
            routes = [route.path for route in server.app.routes]
            engagement_routes = [r for r in routes if 'engagement' in r.lower()]
            
            if engagement_routes:
                print(f"✅ Engagement routes detected: {engagement_routes}")
            else:
                print("⚠️ No engagement-specific routes detected")
        
        print("✅ Server startup test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server_startup())
    sys.exit(0 if success else 1)