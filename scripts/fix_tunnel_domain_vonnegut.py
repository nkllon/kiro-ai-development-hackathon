#!/usr/bin/env python3
"""
Fix Cloudflare tunnel domain configuration on Vonnegut
The tunnel is currently configured for observatory.niclon.com but should be observatory.nkllon.com
"""

import subprocess
import sys
import os
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

def fix_tunnel_configuration():
    """Fix the tunnel configuration to use correct domain"""
    print("🔧 Fixing Cloudflare tunnel domain configuration...")
    
    # Stop the current tunnel
    print("\n1. Stopping current tunnel...")
    run_ssh_command("sudo pkill -f cloudflared", "Stopping cloudflared process")
    time.sleep(2)
    
    # Create the correct tunnel configuration
    print("\n2. Creating correct tunnel configuration...")
    
    tunnel_config = """tunnel: d1e53e43-033f-4994-8f46-c83962ae3785
credentials-file: /home/lou/.cloudflared/d1e53e43-033f-4994-8f46-c83962ae3785.json

ingress:
  - hostname: observatory.nkllon.com
    service: http://localhost:8888
    originRequest:
      httpHostHeader: localhost:8888
      noTLSVerify: false
      connectTimeout: 30s
      tlsTimeout: 10s
      tcpKeepAlive: 30s
      keepAliveConnections: 100
      keepAliveTimeout: 90s
  - hostname: grafana.vonnegut.poe.com
    service: http://localhost:3000
    originRequest:
      httpHostHeader: localhost:3000
      noTLSVerify: false
      connectTimeout: 30s
      tlsTimeout: 10s
      tcpKeepAlive: 30s
      keepAliveConnections: 100
      keepAliveTimeout: 90s
  - hostname: prometheus.vonnegut.poe.com
    service: http://localhost:9090
    originRequest:
      httpHostHeader: localhost:9090
      noTLSVerify: false
      connectTimeout: 30s
      tlsTimeout: 10s
      tcpKeepAlive: 30s
      keepAliveConnections: 100
      keepAliveTimeout: 90s
  - service: http_status:404"""
    
    # Write the configuration file
    config_command = f'cat > /tmp/tunnel_config.yml << "EOF"\n{tunnel_config}\nEOF'
    run_ssh_command(config_command, "Creating tunnel configuration")
    
    # Move to proper location
    run_ssh_command("sudo mv /tmp/tunnel_config.yml /etc/cloudflared/config.yml", "Moving config to /etc/cloudflared/")
    run_ssh_command("sudo chown root:root /etc/cloudflared/config.yml", "Setting config ownership")
    run_ssh_command("sudo chmod 644 /etc/cloudflared/config.yml", "Setting config permissions")
    
    print("\n3. Starting tunnel with new configuration...")
    
    # Start the tunnel with new configuration
    start_command = "nohup cloudflared tunnel --config /etc/cloudflared/config.yml run > /tmp/tunnel.log 2>&1 &"
    run_ssh_command(start_command, "Starting cloudflared tunnel")
    
    # Wait a moment for startup
    time.sleep(5)
    
    print("\n4. Verifying tunnel status...")
    run_ssh_command("pgrep -f cloudflared", "Checking tunnel process")
    run_ssh_command("tail -10 /tmp/tunnel.log", "Checking tunnel logs")
    
    print("\n5. Testing local services...")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8888/health", "Testing Observatory")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/-/healthy", "Testing Prometheus")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing Grafana")

def main():
    print("🌐 Fixing Cloudflare Tunnel Domain Configuration")
    print("=" * 60)
    
    try:
        fix_tunnel_configuration()
        
        print("\n✅ Tunnel configuration fix completed!")
        print("\n🌐 External URLs should now work:")
        print("   Observatory: https://observatory.nkllon.com")
        print("   Grafana: https://grafana.vonnegut.poe.com") 
        print("   Prometheus: https://prometheus.vonnegut.poe.com")
        print("\n⏰ Note: DNS changes may take a few minutes to propagate")
        
    except Exception as e:
        print(f"\n❌ Error during tunnel fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())