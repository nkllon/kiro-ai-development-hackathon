#!/usr/bin/env python3
"""
Restart the Cloudflare tunnel on Vonnegut with proper configuration
"""

import subprocess
import sys
import time

def run_ssh_command(command, description=""):
    """Run command via SSH on Vonnegut server"""
    ssh_command = f'ssh -o StrictHostKeyChecking=no lou@192.168.1.119 "{command}"'
    print(f"🔧 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, timeout=30)
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        if result.stderr:
            print(f"⚠️ Stderr: {result.stderr.strip()}")
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out")
        return False, "", "Command timed out"
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, "", str(e)

def restart_tunnel():
    """Restart the Cloudflare tunnel"""
    print("🔄 Restarting Cloudflare tunnel...")
    
    # Kill any existing tunnel processes
    print("\n1. Stopping existing tunnel processes...")
    run_ssh_command("sudo pkill -f cloudflared", "Killing cloudflared processes")
    time.sleep(3)
    
    # Verify tunnel configuration exists
    print("\n2. Verifying tunnel configuration...")
    run_ssh_command("ls -la /etc/cloudflared/config.yml", "Checking config file")
    run_ssh_command("cat /etc/cloudflared/config.yml", "Showing config content")
    
    # Start tunnel in background
    print("\n3. Starting tunnel...")
    start_command = "nohup cloudflared tunnel --config /etc/cloudflared/config.yml run > /tmp/tunnel.log 2>&1 &"
    run_ssh_command(start_command, "Starting cloudflared tunnel")
    
    # Wait for startup
    time.sleep(5)
    
    # Check if tunnel is running
    print("\n4. Verifying tunnel status...")
    success, stdout, stderr = run_ssh_command("pgrep -f cloudflared", "Checking tunnel process")
    
    if success and stdout.strip():
        print("✅ Tunnel process is running")
        
        # Check tunnel logs
        run_ssh_command("tail -15 /tmp/tunnel.log", "Checking recent tunnel logs")
        
        # Test local services
        print("\n5. Testing local services...")
        run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8888/health", "Testing Observatory")
        run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/-/healthy", "Testing Prometheus")
        run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing Grafana")
        
        return True
    else:
        print("❌ Tunnel failed to start")
        run_ssh_command("tail -20 /tmp/tunnel.log", "Checking tunnel error logs")
        return False

def main():
    print("🌐 Restarting Cloudflare Tunnel on Vonnegut")
    print("=" * 50)
    
    try:
        if restart_tunnel():
            print("\n✅ Tunnel restart completed successfully!")
            print("\n🌐 External URLs should be accessible:")
            print("   Observatory: https://observatory.nkllon.com")
            print("   Grafana: https://grafana.vonnegut.poe.com")
            print("   Prometheus: https://prometheus.vonnegut.poe.com")
            print("\n⏰ Note: Allow 1-2 minutes for tunnel connections to stabilize")
        else:
            print("\n❌ Tunnel restart failed")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error during tunnel restart: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())