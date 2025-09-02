#!/usr/bin/env python3
"""
Simple, clean project status script
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any


def run_command(cmd: list[str], capture_output: bool = True) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(cmd, capture_output=capture_output, text=True, check=False)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def get_git_status() -> Dict[str, Any]:
    """Get clean git status information"""
    status = {}

    # Current branch
    _, branch, _ = run_command(["git", "branch", "--show-current"])
    status["branch"] = branch

    # Uncommitted changes count
    _, changes, _ = run_command(["git", "status", "--porcelain"])
    status["uncommitted_changes"] = len(changes.splitlines()) if changes else 0

    # Last commit
    _, last_commit, _ = run_command(["git", "log", "-1", "--format=%h - %s (%cr)"])
    status["last_commit"] = last_commit

    return status


def get_code_quality_status() -> Dict[str, Any]:
    """Get code quality metrics without verbose output"""
    quality = {}

    # Check if UV is available
    _, uv_version, _ = run_command(["uv", "--version"])
    quality["uv_available"] = uv_version != ""

    # Flake8 count (quiet mode)
    _, flake8_output, _ = run_command(["uv", "run", "flake8", "--count", "--statistics", "src/"], capture_output=True)
    if flake8_output:
        try:
            # Extract count from last line
            lines = flake8_output.splitlines()
            if lines:
                last_line = lines[-1]
                count = last_line.split()[-1]  # Last number in the line
                quality["flake8_issues"] = int(count)
            else:
                quality["flake8_issues"] = 0
        except (ValueError, IndexError):
            quality["flake8_issues"] = 0
    else:
        quality["flake8_issues"] = 0

    # MyPy count (quiet mode)
    _, mypy_output, _ = run_command(
        ["uv", "run", "mypy", "--ignore-missing-imports", "--no-error-summary", "src/"],
        capture_output=True,
    )
    if mypy_output:
        error_count = mypy_output.count("error:")
        quality["mypy_errors"] = error_count
    else:
        quality["mypy_errors"] = 0

    # Black formatting check (quiet mode)
    _, black_output, _ = run_command(["uv", "run", "black", "--check", "--quiet", "src/"], capture_output=True)
    quality["black_formatted"] = black_output == ""

    return quality


def get_project_info() -> Dict[str, Any]:
    """Get basic project information"""
    info = {}

    # Python version
    _, python_version, _ = run_command(["python3", "--version"])
    info["python_version"] = python_version

    # Check key files
    info["pyproject_toml"] = Path("pyproject.toml").exists()
    info["uv_lock"] = Path("uv.lock").exists()

    # Check key directories
    info["ghostbusters"] = Path("src/ghostbusters").exists()
    info["artifact_forge"] = Path("src/artifact_forge").exists()
    info["model_driven"] = Path("src/model_driven_projection").exists()
    info["quality_system"] = Path("src/code_quality_system").exists()

    return info


def print_status():
    """Print clean, readable status"""
    print("🚀 OpenFlow Playground - Status")
    print("=" * 40)

    # Git Status
    print("\n📊 Git Status:")
    git_status = get_git_status()
    print(f"  Branch: {git_status['branch']}")
    print(f"  Changes: {git_status['uncommitted_changes']} uncommitted")
    print(f"  Last: {git_status['last_commit']}")

    # Code Quality
    print("\n🔍 Code Quality:")
    quality = get_code_quality_status()
    print(f"  Flake8: {quality['flake8_issues']} issues")
    print(f"  MyPy: {quality['mypy_errors']} errors")
    print(f"  Black: {'✅' if quality['black_formatted'] else '❌'} formatted")

    # Project Info
    print("\n🏗️  Project:")
    info = get_project_info()
    print(f"  Python: {info['python_version']}")
    print(f"  UV: {'✅' if quality['uv_available'] else '❌'}")
    print(f"  Dependencies: {'✅' if info['pyproject_toml'] and info['uv_lock'] else '❌'}")

    # System Components
    print("\n⚙️  Components:")
    print(f"  Ghostbusters: {'✅' if info['ghostbusters'] else '❌'}")
    print(f"  ArtifactForge: {'✅' if info['artifact_forge'] else '❌'}")
    print(f"  Model-Driven: {'✅' if info['model_driven'] else '❌'}")
    print(f"  Quality System: {'✅' if info['quality_system'] else '❌'}")

    # Quick Actions
    print("\n🎯 Quick Actions:")
    print("  make format-all    - Format code")
    print("  make lint-all      - Fix linting")
    print("  make test-all      - Run tests")

    print("\n✅ Status complete!")


if __name__ == "__main__":
    print_status()
