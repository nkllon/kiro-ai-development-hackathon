#!/usr/bin/env python3
"""
Systematic MyPy Type Error Fixer using Round-Trip Engineering

This script follows the project rules by using the round-trip engineering system
to fix MyPy type errors at the model level rather than manually editing files.

Usage:
    python scripts/fix_mypy_type_errors_systematic.py [target_directory]
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def find_python_files(directory: str = ".") -> list[Path]:
    """Find all Python files in the directory"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["__pycache__", "node_modules", "venv", "env"]]

        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)

    return python_files


def run_round_trip_on_file(file_path: Path) -> dict[str, Any]:
    """Run round-trip engineering on a single file"""
    print(f"🔄 Processing: {file_path}")

    try:
        # Run the round-trip enforcement script
        result = subprocess.run(
            [sys.executable, "scripts/enforce_round_trip.py", str(file_path)],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=300,  # 5 minute timeout per file
        )

        success = result.returncode == 0
        output = result.stdout
        error = result.stderr

        return {
            "file": str(file_path),
            "success": success,
            "output": output,
            "error": error,
            "return_code": result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {
            "file": str(file_path),
            "success": False,
            "output": "",
            "error": "Timeout after 5 minutes",
            "return_code": -1,
        }
    except Exception as e:
        return {
            "file": str(file_path),
            "success": False,
            "output": "",
            "error": str(e),
            "return_code": -1,
        }


def main():
    """Main function to systematically fix MyPy type errors"""
    print("🚀 Systematic MyPy Type Error Fixer")
    print("📋 Using Round-Trip Engineering System (as required by project rules)")
    print("=" * 60)

    # Get target directory from command line or use current
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "src"

    print(f"🎯 Target directory: {target_dir}")
    print(f"📁 Project root: {project_root}")

    # Find all Python files
    print("\n🔍 Finding Python files...")
    python_files = find_python_files(target_dir)
    print(f"📄 Found {len(python_files)} Python files")

    # Process files systematically
    print("\n🔄 Starting systematic round-trip processing...")
    results = []

    for i, file_path in enumerate(python_files, 1):
        print(f"\n[{i}/{len(python_files)}] Processing: {file_path}")

        result = run_round_trip_on_file(file_path)
        results.append(result)

        if result["success"]:
            print(f"  ✅ Success: {file_path}")
        else:
            print(f"  ❌ Failed: {file_path}")
            print(f"     Error: {result['error']}")

        # Small delay to avoid overwhelming the system
        time.sleep(0.1)

    # Generate summary report
    print("\n" + "=" * 60)
    print("📊 PROCESSING SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"📊 Total: {len(results)}")

    if failed:
        print(f"\n🚨 Failed files:")
        for result in failed:
            print(f"  - {result['file']}: {result['error']}")

    # Save results to file
    report_file = f"mypy_type_fix_report_{int(time.time())}.json"
    with open(report_file, "w") as f:
        json.dump(
            {
                "timestamp": time.time(),
                "target_directory": target_dir,
                "total_files": len(results),
                "successful": len(successful),
                "failed": len(failed),
                "results": results,
            },
            f,
            indent=2,
        )

    print(f"\n📄 Detailed report saved to: {report_file}")

    if successful:
        print(f"\n🎉 Successfully processed {len(successful)} files!")
        print("💡 The round-trip system has added proper type annotations.")
        print("🔍 Run 'make lint-python' to check for remaining issues.")

    if failed:
        print(f"\n⚠️  {len(failed)} files failed processing.")
        print("🔍 Check the detailed report for specific errors.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
