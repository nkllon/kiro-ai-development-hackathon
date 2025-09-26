#!/usr/bin/env python3
"""
Observatory Server Entry Point

Properly starts the Observatory server with correct module imports.
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Set working directory to project root
os.chdir(str(project_root))

# Import and run the server
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Beast Mode Coordination Observatory Server")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, help="Port to bind to")
    
    args = parser.parse_args()
    
    # Set environment variable for config path if provided
    if args.config and os.path.exists(args.config):
        os.environ['OBSERVATORY_CONFIG_PATH'] = args.config
    
    from beast_mode.observatory.server import main
    import asyncio
    asyncio.run(main())