#!/usr/bin/env python3
"""
Model Management CLI - Parameterized Model Operations

This is a thin wrapper around the model_management domain capabilities.
All actual logic is delegated to the domain implementation.

Usage Examples:
  model -m project read
  model -m project list-domains
  model -m project add-item my_item -d "description" -c domains
  model -m my_new_model -d "this model is awesome and only tracks awesomeness" -t JSON -s my_new_model_schema

Single responsibility: Provide parameterized CLI interface to model_management domain.
"""

import sys
from pathlib import Path

# Add src to path for domain imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from model_management.model_crud import ModelManagementCLI


def main():
    """Main entry point - delegates to domain implementation."""
    cli = ModelManagementCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
