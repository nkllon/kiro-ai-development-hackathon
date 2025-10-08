#!/usr/bin/env python3
"""
Start Observatory in Background
==============================
Simple script to start Observatory in background and verify it's working.
"""

import subprocess
import sys
import time
import requests
import os

def start_observatory_background():
    """Start Observatory in background."""
    print("🚀 Starting Observatory in background...")
    
    # Start Observatory in background with output redirection
    process = subprocess.Popen(
        [sys.executable, "start_observatory.py"],
        stdout=open("observatory.log", "w"),
        stderr=subprocess.STDOUT,
        env=dict(os.environ, PYTHONUNBUFFERED="1")
    )
    
    # Save PID
    with open("observatory.pid", "w") as f:
        f.write(str(process.pid))
    
    print(f"✅ Observatory started with PID {process.pid}")
    print("📋 Logs: observatory.log")
    
    # Wait a bit for startup
    print("⏳ Waiting for Observatory to start...")
    time.sleep(10)
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8888/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Observatory is healthy: {health}")
            return True
        else:
            print(f"⚠️  Observatory health check returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Observatory health check failed: {e}")
        return False

if __name__ == "__main__":
    success = start_observatory_background()
    sys.exit(0 if success else 1)