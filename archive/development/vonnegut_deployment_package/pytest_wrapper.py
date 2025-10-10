#!/usr/bin/env python3
"""
pytest wrapper - only allows execution through make
"""

import os
import sys

import psutil


def check_parent_process():
    """Check if we're being called by make"""
    try:
        # Get current process
        current_process = psutil.Process()

        # Check parent process
        parent = current_process.parent()
        if parent:
            parent_name = parent.name()

            # Allow if parent is make
            if parent_name == "make":
                return True

            # Allow if we're in a make environment
            if os.environ.get("MAKEFLAGS") or os.environ.get("MAKELEVEL"):
                return True

        # Block direct execution
        print("❌ ERROR: pytest can only be executed through make")
        print("✅ Use: make test")
        print("📋 Available test targets:")
        print("   - make test")
        print("   - make test-all")
        print("   - make test-python")
        print("   - make test-model-driven")
        sys.exit(1)

    except Exception as e:
        # If we can't check, allow execution (fail open)
        print(f"⚠️  Warning: Could not check parent process: {e}")
        return True


def main():
    """Main function"""
    # Check parent process before executing
    if not check_parent_process():
        sys.exit(1)

    # If we get here, execution is allowed
    # Execute the original pytest
    original_pytest = "/home/lou/.local/bin/pytest.original"

    if not os.path.exists(original_pytest):
        print("❌ ERROR: Original pytest not found")
        sys.exit(1)

    # Execute the original pytest with all arguments
    os.execv(original_pytest, [original_pytest] + sys.argv[1:])


if __name__ == "__main__":
    main()
