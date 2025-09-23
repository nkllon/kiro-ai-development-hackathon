#!/usr/bin/env python3
"""
Real test runner - finds and runs all working tests
"""
import subprocess
import sys
import os
from pathlib import Path

def run_all_tests():
    """Run all tests in the 'tests' directory."""
    print("🧪 Running pytest on test directory...")
    # Ensure src is in PYTHONPATH for test discovery and execution
    current_dir = Path(__file__).parent.absolute()
    src_path = current_dir / "src"
    env = os.environ.copy()
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{src_path}:{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = str(src_path)

    cmd = [sys.executable, "-m", "pytest", "tests", "-v", "--tb=short"]
    result = subprocess.run(cmd, capture_output=False, env=env)
    return result.returncode == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
