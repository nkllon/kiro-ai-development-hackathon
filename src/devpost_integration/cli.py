#!/usr/bin/env python3
"""
CLI - Unified CLI imports for Devpost Integration

Refactored for RM-DDD compliance by importing from decomposed modules.
Single responsibility: CLI imports and re-exports.
"""

# Import all CLI components from decomposed modules
from .cli_main import DevPostCLI, main

# Re-export everything for backward compatibility
__all__ = [
    'DevPostCLI',
    'main'
]
