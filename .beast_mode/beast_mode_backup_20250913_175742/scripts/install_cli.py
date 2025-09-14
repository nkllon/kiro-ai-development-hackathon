#!/usr/bin/env python3
"""
Beast Mode CLI Installation Script

Installs the Beast Mode CLI for system-wide usage.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command and return the result"""
    print(f"🔧 Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return e


def check_python_version():
    """Ensure Python 3.9+ is available"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Check if required system dependencies are available"""
    dependencies = {
        'redis-server': 'Redis server for message bus',
        'git': 'Git for version control',
    }
    
    missing = []
    for cmd, description in dependencies.items():
        if not shutil.which(cmd):
            missing.append((cmd, description))
        else:
            print(f"✅ {cmd} found")
    
    if missing:
        print("\n⚠️  Missing optional dependencies:")
        for cmd, desc in missing:
            print(f"   • {cmd}: {desc}")
        print("\n💡 Install with your package manager:")
        print("   macOS: brew install redis git")
        print("   Ubuntu: sudo apt install redis-server git")
        print("   CentOS: sudo yum install redis git")
    
    return len(missing) == 0


def install_package():
    """Install the Beast Mode package"""
    project_root = Path(__file__).parent.parent
    
    print(f"📦 Installing Beast Mode from {project_root}")
    
    # Install in development mode
    result = run_command(f"pip install -e '{project_root}'")
    
    if result.returncode == 0:
        print("✅ Beast Mode package installed successfully")
        return True
    else:
        print("❌ Package installation failed")
        return False


def verify_installation():
    """Verify the CLI is properly installed"""
    commands = ['beast-mode', 'bm', 'beast']
    
    for cmd in commands:
        result = run_command(f"{cmd} --help", check=False)
        if result.returncode == 0:
            print(f"✅ {cmd} command available")
        else:
            print(f"❌ {cmd} command not found")
            return False
    
    return True


def setup_redis():
    """Help user set up Redis if needed"""
    print("\n🔧 Redis Setup")
    
    # Check if Redis is running
    result = run_command("redis-cli ping", check=False)
    
    if result.returncode == 0 and "PONG" in result.stdout:
        print("✅ Redis is running")
        return True
    
    print("⚠️  Redis not running")
    print("\n💡 Start Redis:")
    print("   macOS: brew services start redis")
    print("   Ubuntu: sudo systemctl start redis-server")
    print("   Manual: redis-server")
    
    return False


def main():
    """Main installation process"""
    print("🚀 Beast Mode CLI Installation")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Install package
    if not install_package():
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Installation verification failed")
        print("💡 Try manual installation:")
        print("   pip install -e .")
        sys.exit(1)
    
    # Setup Redis
    redis_ok = setup_redis()
    
    print("\n🎉 Installation Complete!")
    print("=" * 40)
    
    print("\n📋 Available Commands:")
    print("   beast-mode --help    # Full command name")
    print("   bm --help           # Short alias")
    print("   beast --help        # Shorter alias")
    
    print("\n🚀 Quick Start:")
    print("   beast-mode status           # Check network status")
    print("   beast-mode start-agents     # Start collaboration agents")
    print("   beast-mode request-help     # Ask for help")
    print("   beast-mode listen          # Listen to network traffic")
    
    if not redis_ok:
        print("\n⚠️  Don't forget to start Redis before using the CLI!")
    
    if not deps_ok:
        print("\n💡 Consider installing optional dependencies for full functionality")


if __name__ == '__main__':
    main()