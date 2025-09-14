#!/usr/bin/env python3
"""
Quality Check Script for OpenFlow Playground
Called by pre-commit hooks to ensure code quality
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🎨 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  ✅ {description} complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ {description} failed: {e}")
        if e.stdout:
            print(f"    stdout: {e.stdout}")
        if e.stderr:
            print(f"    stderr: {e.stderr}")
        return False


def main():
    """Run all quality checks"""
    print("✨ Running Quality Checks...")

    # Get project root
    project_root = Path(__file__).parent.parent

    # Change to project root
    os.chdir(project_root)

    # Run quality checks
    checks = [
        # Python formatting
        (["uv", "run", "black", "--check", "src/", "tests/"], "Python formatting (Black)"),
        (["uv", "run", "ruff", "check", "src/", "tests/"], "Python linting (Ruff)"),
        # Documentation formatting
        (["uv", "run", "mdformat", "--check", "docs/", "*.md"], "Markdown formatting"),
        # YAML formatting
        (["uv", "run", "yamlfix", "--check", "*.yaml", "*.yml"], "YAML formatting"),
        # Go formatting (if Go files exist)
        (["find", ".", "-name", "*.go", "-exec", "gofmt", "-l", "{}", ";"], "Go formatting check"),
    ]

    all_passed = True
    for cmd, description in checks:
        if not run_command(cmd, description):
            all_passed = False

    if all_passed:
        print("  ✅ Quality checks complete")
        return 0
    else:
        print("  ❌ Some quality checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
