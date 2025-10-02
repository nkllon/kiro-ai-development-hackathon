#!/usr/bin/env python3
"""
Start Observatory server directly for testing engagement integration.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def start_observatory_server():
    """Start the Observatory server."""
    try:
        print("🔭 Starting Observatory Server with Engagement Integration")
        print("=" * 60)
        
        from src.beast_mode.observatory.server import create_server
        
        # Create and start server
        server = create_server()
        print("✅ Observatory server created with engagement integration")
        
        # Start the server
        print("🚀 Starting server on http://localhost:8888")
        print("🎯 Engagement integration enabled")
        print("Press Ctrl+C to stop the server")
        print()
        
        await server.run_server(host="localhost", port=8888)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(start_observatory_server())
    sys.exit(exit_code)