#!/usr/bin/env python3
"""
Prepare Spec for Execution - Main CLI Entry Point
================================================

Convenience script for the prepare-spec CLI tool.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.spec_framework.cli.prepare_spec_cli import main

if __name__ == "__main__":
    sys.exit(main())