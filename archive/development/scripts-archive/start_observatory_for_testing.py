#!/usr/bin/env python3
"""
Start Observatory server for engagement integration testing.

This script starts the Observatory server with engagement integration
and provides a way to test the integration.
"""

import asyncio
import logging
import signal
import sys
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.beast_mode.observatory.server import create_server

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ObservatoryTestServer:
    """Observatory server wrapper for testing."""
    
    def __init__(self):
        self.server = None
        self.running = False
        
    async def start_server(self, host: str = "localhost", port: int = 8888):
        """Start the Observatory server for testing."""
        try:
            logger.info("🚀 Starting Observatory server for engagement integration testing...")
            
            # Create server instance
            self.server = create_server()
            
            # Start the server
            logger.info(f"🌐 Server starting on http://{host}:{port}")
            logger.info("🎯 Engagement integration will be tested...")
            
            self.running = True
            await self.server.run_server(host=host, port=port)
            
        except KeyboardInterrupt:
            logger.info("👋 Server interrupted by user")
            self.running = False
        except Exception as e:
            logger.error(f"💥 Server failed to start: {e}")
            logger.error("🔍 This might indicate engagement integration issues")
            self.running = False
            raise
    
    async def stop_server(self):
        """Stop the server gracefully."""
        if self.server and self.running:
            logger.info("🛑 Stopping Observatory server...")
            self.running = False

async def main():
    """Main function to start server for testing."""
    print("🧪 Observatory Server - Engagement Integration Testing")
    print("=" * 60)
    print("This server will start with engagement integration enabled.")
    print("Use Ctrl+C to stop the server.")
    print("Run the integration tests in another terminal with:")
    print("  python test_engagement_integration.py")
    print()
    
    server = ObservatoryTestServer()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(server.stop_server())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await server.start_server()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)