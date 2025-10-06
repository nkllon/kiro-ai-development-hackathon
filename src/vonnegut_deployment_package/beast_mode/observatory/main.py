#!/usr/bin/env python3
"""
Observatory Main Entry Point
Simple launcher for the Observatory server.
"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())