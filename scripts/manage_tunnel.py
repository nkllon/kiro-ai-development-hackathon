#!/usr/bin/env python3
"""
Cloudflare Tunnel Management Script
"""

import subprocess
import sys
import time
import os
import signal

TUNNEL_PID_FILE = "cloudflare_tunnel.pid"
CONFIG_FILE = "cloudflared-config.yml"

def start_tunnel():
    """Start Cloudflare tunnel."""
    if is_running():
        print("Tunnel is already running")
        return True
    
    print("Starting Cloudflare tunnel...")
    process = subprocess.Popen([
        'cloudflared', 'tunnel', '--config', CONFIG_FILE, 'run'
    ])
    
    with open(TUNNEL_PID_FILE, 'w') as f:
        f.write(str(process.pid))
    
    print(f"Tunnel started with PID {process.pid}")
    return True

def stop_tunnel():
    """Stop Cloudflare tunnel."""
    if not os.path.exists(TUNNEL_PID_FILE):
        print("Tunnel PID file not found")
        return False
    
    with open(TUNNEL_PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Sent SIGTERM to tunnel process {pid}")
        
        time.sleep(5)
        
        try:
            os.kill(pid, 0)
            print("Process still running, sending SIGKILL")
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            print("Tunnel stopped gracefully")
        
        os.remove(TUNNEL_PID_FILE)
        return True
        
    except ProcessLookupError:
        print("Tunnel process not found")
        os.remove(TUNNEL_PID_FILE)
        return False

def is_running():
    """Check if tunnel is running."""
    if not os.path.exists(TUNNEL_PID_FILE):
        return False
    
    with open(TUNNEL_PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        os.remove(TUNNEL_PID_FILE)
        return False

def status():
    """Show tunnel status."""
    if is_running():
        print("Cloudflare tunnel is running")
    else:
        print("Cloudflare tunnel is not running")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage_tunnel.py [start|stop|status|restart]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        start_tunnel()
    elif command == "stop":
        stop_tunnel()
    elif command == "status":
        status()
    elif command == "restart":
        stop_tunnel()
        time.sleep(2)
        start_tunnel()
    else:
        print("Unknown command. Use: start, stop, status, or restart")
