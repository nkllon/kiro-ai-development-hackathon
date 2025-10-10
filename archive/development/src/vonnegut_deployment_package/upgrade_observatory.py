#!/usr/bin/env python3
"""
Observatory Upgrade Script
=========================

Upgrades from minimal Observatory to full Observatory when dependencies are resolved.
"""

import subprocess
import sys
import time
import requests

def stop_minimal_observatory():
    """Stop the minimal Observatory."""
    print("🛑 Stopping minimal Observatory...")
    subprocess.run(["pkill", "-f", "start_observatory_minimal"], capture_output=True)
    time.sleep(2)

def start_full_observatory():
    """Attempt to start full Observatory."""
    print("🚀 Starting full Observatory...")
    try:
        process = subprocess.Popen([sys.executable, "start_observatory.py"])
        time.sleep(10)
        
        # Test if it's working
        response = requests.get("http://localhost:8888/health", timeout=10)
        if response.status_code == 200:
            print("✅ Full Observatory started successfully")
            return True
        else:
            print("❌ Full Observatory failed health check")
            return False
    except Exception as e:
        print(f"❌ Full Observatory failed to start: {e}")
        return False

def fallback_to_minimal():
    """Fallback to minimal Observatory."""
    print("🔄 Falling back to minimal Observatory...")
    subprocess.Popen([sys.executable, "start_observatory_minimal.py"])
    time.sleep(5)
    
    try:
        response = requests.get("http://localhost:8888/health", timeout=10)
        if response.status_code == 200:
            print("✅ Minimal Observatory restored")
            return True
    except:
        pass
    
    print("❌ Failed to restore minimal Observatory")
    return False

def main():
    """Main upgrade process."""
    print("🔄 Observatory Upgrade Process")
    print("=" * 40)
    
    # Stop minimal
    stop_minimal_observatory()
    
    # Try full
    if start_full_observatory():
        print("🎉 Upgrade successful!")
        return True
    
    # Fallback to minimal
    if fallback_to_minimal():
        print("⚠️  Upgrade failed, restored minimal mode")
        return False
    
    print("❌ Upgrade failed completely")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
