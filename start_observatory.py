#!/usr/bin/env python3
"""
Start the Beast Mode Observatory server with custom configuration.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode.observatory.models import ObservatoryConfig, WebSocketConfig
from beast_mode.observatory.server import ObservatoryServer


async def main():
    """Start the Observatory server with custom configuration."""
    print("🚀 Starting Beast Mode Observatory...")
    
    # Create custom config with different port
    config = ObservatoryConfig()
    config.websocket_config = WebSocketConfig(
        host="0.0.0.0",
        port=8889,  # Use different port
        max_connections=100,
        heartbeat_interval=30
    )
    
    # Start the server
    server = ObservatoryServer(config)
    
    try:
        print("✅ Observatory server initialized!")
        print("🌐 Starting web server on http://localhost:8000")
        print("📡 WebSocket server will run on port 8889")
        print("Press Ctrl+C to stop...")
        
        # Run the server
        await server.run_server(host="0.0.0.0", port=8000)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Observatory server...")
        print("✅ Observatory server stopped gracefully")
    except Exception as e:
        print(f"❌ Error running Observatory server: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())