#!/usr/bin/env python3
"""
Emergency Tunnel Restore
========================
Quickly restore the Observatory site with proper tunnel configuration.
"""

import subprocess
import time
import sys
import os
import signal

def kill_existing_tunnels():
    """Kill any existing cloudflared processes."""
    try:
        subprocess.run(["pkill", "-f", "cloudflared"], check=False)
        time.sleep(2)
        print("✅ Killed existing tunnels")
    except Exception as e:
        print(f"Warning: {e}")

def start_named_tunnel():
    """Start the named tunnel with correct configuration."""
    try:
        print("🚀 Starting named tunnel...")
        
        # Use the correct tunnel ID from config
        tunnel_id = "d1e53e43-033f-4994-8f46-c83962ae3785"
        
        process = subprocess.Popen([
            "cloudflared", "tunnel", "run", tunnel_id
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ Tunnel started with PID: {process.pid}")
        return process
        
    except Exception as e:
        print(f"❌ Error starting tunnel: {e}")
        return None

def test_connectivity():
    """Test if the site is accessible."""
    import requests
    
    endpoints = [
        "https://observatory.nkllon.com/health",
        "https://grafana.observatory.nkllon.com/api/health",
        "https://prometheus.observatory.nkllon.com/api/v1/query?query=up"
    ]
    
    print("\n🧪 Testing connectivity...")
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"⚠️ {endpoint} - HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - {e}")

def main():
    print("🚨 Emergency Tunnel Restore")
    print("=" * 40)
    
    # Kill existing tunnels
    kill_existing_tunnels()
    
    # Start named tunnel
    process = start_named_tunnel()
    
    if not process:
        print("❌ Failed to start tunnel")
        sys.exit(1)
    
    # Wait for tunnel to establish
    print("⏳ Waiting for tunnel to establish...")
    time.sleep(15)
    
    # Test connectivity
    test_connectivity()
    
    print("\n🎯 Tunnel is running. Press Ctrl+C to stop.")
    
    try:
        # Keep running
        process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping tunnel...")
        process.terminate()
        process.wait()
        print("✅ Tunnel stopped")

if __name__ == "__main__":
    main()