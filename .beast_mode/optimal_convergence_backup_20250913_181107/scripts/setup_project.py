#!/usr/bin/env python3
"""
Project Setup Script for OpenFlow Playground
Ensures proper environment configuration for new installs
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, check=True):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        print(f"  ✅ {description} complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ {description} failed: {e}")
        if e.stdout:
            print(f"    stdout: {e.stdout}")
        if e.stderr:
            print(f"    stderr: {e.stderr}")
        return False


def check_uv_installed():
    """Check if UV is installed"""
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_uv():
    """Install UV if not present"""
    print("📦 Installing UV package manager...")
    try:
        subprocess.run(["curl", "-LsSf", "https://astral.sh/uv/install.sh"], input="sh", text=True, check=True)
        print("  ✅ UV installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ UV installation failed: {e}")
        return False


def setup_pre_commit():
    """Setup pre-commit hooks with UV"""
    print("🔧 Setting up pre-commit hooks...")

    # Install pre-commit via UV
    if not run_command(["uv", "add", "--dev", "pre-commit"], "Installing pre-commit"):
        return False

    # Install the hooks
    if not run_command(["uv", "run", "pre-commit", "install"], "Installing pre-commit hooks"):
        return False

    return True


def install_dependencies():
    """Install project dependencies"""
    print("📦 Installing project dependencies...")

    # Sync all dependencies
    if not run_command(["uv", "sync", "--all-extras"], "Installing dependencies"):
        return False

    return True


def verify_setup():
    """Verify the setup is working"""
    print("🔍 Verifying setup...")

    # Check if pre-commit works
    if not run_command(["uv", "run", "pre-commit", "--version"], "Checking pre-commit"):
        return False

    # Check if hooks are installed
    hooks_dir = Path(".git/hooks")
    if not hooks_dir.exists():
        print("  ❌ .git directory not found. Are you in a git repository?")
        return False

    pre_commit_hook = hooks_dir / "pre-commit"
    if not pre_commit_hook.exists():
        print("  ❌ Pre-commit hook not installed")
        return False

    print("  ✅ Pre-commit hook installed")
    return True


def main():
    """Main setup function"""
    print("🚀 OpenFlow Playground - Project Setup")
    print("=" * 50)

    # Check if we're in a git repository
    if not Path(".git").exists():
        print("❌ Error: Not in a git repository")
        print("   Please run: git init")
        return 1

    # Check/install UV
    if not check_uv_installed():
        if not install_uv():
            print("❌ Failed to install UV. Please install manually:")
            print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
            return 1
    else:
        print("✅ UV already installed")

    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return 1

    # Setup pre-commit
    if not setup_pre_commit():
        print("❌ Failed to setup pre-commit")
        return 1

    # Verify setup
    if not verify_setup():
        print("❌ Setup verification failed")
        return 1

    print("\n🎉 Project setup complete!")
    print("\n📋 Next steps:")
    print("   1. Run: uv run pre-commit run --all-files")
    print("   2. Run: make test")
    print("   3. Start developing!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
