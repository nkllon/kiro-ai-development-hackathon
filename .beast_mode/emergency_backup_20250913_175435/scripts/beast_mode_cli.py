#!/usr/bin/env python3
"""
Beast Mode Agent Collaboration Network CLI Entry Point

Simple script to launch the Beast Mode CLI interface.
"""

import sys
from pathlib import Path

# Add src to path so we can import beast_mode modules
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from beast_mode.messaging.cli import cli

if __name__ == '__main__':
    cli()