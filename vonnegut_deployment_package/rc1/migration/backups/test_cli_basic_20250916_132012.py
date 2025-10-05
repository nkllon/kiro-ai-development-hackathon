#!/usr/bin/env python3
"""
Basic CLI test for Beast Mode DAG orchestration.
"""

import subprocess
import sys
from pathlib import Path


def test_cli_import():
    """Test that CLI can be imported successfully."""
    try:
        from src.beast_mode.dag_orchestration.cli import beast_dag

        print("✅ CLI import successful")
        return True
    except Exception as e:
        print(f"❌ CLI import failed: {e}")
        return False


def test_cli_help():
    """Test CLI help command."""
    try:
        # Test help command
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from src.beast_mode.dag_orchestration.cli import beast_dag; beast_dag(['--help'])",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if "BEAST MODE DAG Orchestration CLI" in result.stdout:
            print("✅ CLI help command works")
            return True
        else:
            print(f"❌ CLI help failed: {result.stdout}")
            return False
    except Exception as e:
        print(f"❌ CLI help test failed: {e}")
        return False


def test_cli_analyze_dry_run():
    """Test CLI analyze command with current specs directory."""
    try:
        specs_dir = Path(".kiro/specs")
        if not specs_dir.exists():
            print("⚠️ No specs directory found, skipping analyze test")
            return True

        # Test analyze command
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f"from src.beast_mode.dag_orchestration.cli import beast_dag; beast_dag(['analyze', '{specs_dir}', '--output', 'json'])",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("✅ CLI analyze command works")
            return True
        else:
            print(f"❌ CLI analyze failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI analyze test failed: {e}")
        return False


if __name__ == "__main__":
    print("🔥 BEAST MODE CLI TESTING")

    tests = [test_cli_import, test_cli_help, test_cli_analyze_dry_run]

    passed = 0
    for test in tests:
        if test():
            passed += 1

    print(f"\n📊 CLI Tests: {passed}/{len(tests)} passed")

    if passed == len(tests):
        print("🏆 ALL CLI TESTS PASSED - SYSTEMATIC SUPERIORITY DEMONSTRATED")
    else:
        print("⚠️ Some CLI tests failed - systematic improvements needed")
