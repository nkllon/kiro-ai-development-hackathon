#!/usr/bin/env python3
"""
Configure Vonnegut Cloudflare Tunnel
===================================

Configures the Cloudflare tunnel to route properly to the Observatory.
"""

import subprocess
import yaml
import time

def ssh_command(command: str) -> tuple[bool, str, str]:
    """Execute SSH command on Vonnegut."""
    try:
        result = subprocess.run([
            "ssh", "lou@192.168.1.119", command
        ], capture_output=True, text=True, timeout=60)
        
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def upload_file(local_path: str, remote_path: str) -> bool:
    """Upload file to Vonnegut."""
    try:
        subprocess.run([
            "scp", local_path, f"lou@192.168.1.119:{remote_path}"
        ], check=True)
        return True
    except Exception as e:
        print(f"❌ Failed to upload {local_path}: {e}")
        return False

def configure_tunnel():
    """Configure Cloudflare tunnel for Observatory."""
    print("☁️ Configuring Cloudflare tunnel...")
    
    # 1. Stop existing tunnel
    print("🛑 Stopping existing tunnel...")
    ssh_command("pkill -f cloudflared 2>/dev/null || true")
    
    # 2. Create tunnel configuration
    print("📝 Creating tunnel configuration...")
    
    tunnel_config = {
        'tunnel': 'd1e53e43-033f-4994-8f46-c83962ae3785',
        'credentials-file': '/home/lou/observatory/tunnel-credentials.json',
        'ingress': [
            {
                'hostname': 'observatory.niclon.com',
                'service': 'http://localhost:8888'
            },
            {
                'hostname': 'grafana.vonnegut.poe.com', 
                'service': 'http://localhost:3000'
            },
            {
                'hostname': 'prometheus.vonnegut.poe.com',
                'service': 'http://localhost:9090'
            },
            {
                'service': 'http_status:404'
            }
        ]
    }
    
    # Write config to temp file
    with open("/tmp/cloudflared-config.yml", 'w') as f:
        yaml.dump(tunnel_config, f, default_flow_style=False)
    
    # Upload to Vonnegut
    if not upload_file("/tmp/cloudflared-config.yml", "/home/lou/observatory/cloudflared-config.yml"):
        return False
    
    # 3. Start tunnel
    print("🚀 Starting Cloudflare tunnel...")
    
    start_tunnel_command = """
cd /home/lou/observatory
nohup cloudflared tunnel --config cloudflared-config.yml run > tunnel.log 2>&1 &
echo "Tunnel started with PID: $!"
"""
    
    success, stdout, stderr = ssh_command(start_tunnel_command)
    
    if success:
        print("✅ Tunnel started")
        print(f"📋 Output: {stdout}")
    else:
        print("❌ Failed to start tunnel:")
        print(f"Error: {stderr}")
        return False
    
    # 4. Wait and test
    print("⏳ Waiting for tunnel to connect...")
    time.sleep(15)
    
    # 5. Check tunnel status
    print("🔍 Checking tunnel status...")
    success, stdout, stderr = ssh_command("cd /home/lou/observatory && tail -10 tunnel.log")
    
    if success:
        print("📋 Tunnel logs:")
        print(stdout)
    
    # 6. Test external access
    print("🌐 Testing external access...")
    try:
        import requests
        response = requests.get("https://observatory.niclon.com/health", timeout=30)
        
        if response.status_code == 200:
            print("✅ External access working!")
            print(f"📊 Health status: {response.json()}")
            return True
        else:
            print(f"❌ External access failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ External access test failed: {e}")
        print("💡 The tunnel may still be connecting. Try again in a few minutes.")
        return False

if __name__ == "__main__":
    if configure_tunnel():
        print("\n🎉 Cloudflare tunnel configured successfully!")
        print("🌐 Observatory: https://observatory.niclon.com")
        print("📊 Prometheus: https://prometheus.vonnegut.poe.com")
        print("📈 Grafana: https://grafana.vonnegut.poe.com")
    else:
        print("\n❌ Tunnel configuration failed")
        print("Check the tunnel logs on Vonnegut for more details")