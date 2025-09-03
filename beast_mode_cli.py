#!/usr/bin/env python3
"""
Beast Mode Framework CLI Entry Point
Provides command-line interface for Beast Mode operations
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from beast_mode.cli.beast_mode_cli import main

if __name__ == "__main__":
    main()