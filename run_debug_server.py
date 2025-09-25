#!/usr/bin/env python3
"""
Run the Observatory server for debugging frontend issues.
"""

import asyncio
import sys
import logging

# Add src to path
sys.path.insert(0, 'src')

from beast_mode.observatory.server import create_server

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Run the debug server."""
    print("🚀 Starting Observatory Server for debugging...")
    print("📱 Open http://localhost:8888 in your browser")
    print("🐛 Or open debug_frontend.html and point it to localhost:8888")
    
    server = create_server()
    await server.run_server(host="127.0.0.1", port=8888)

if __name__ == "__main__":
    asyncio.run(main())