#!/usr/bin/env python3
"""
Install and Configure Cloudflare Tunnel on Vonnegut
==================================================

Installs cloudflared and configures the tunnel for Observatory access.
"""

import subprocess
import yaml
import time

def ssh_command(command: str) -> tuple[bool, str, str]:
    """Execute SSH command on Vonnegut."""
    try:
        result = subprocess.run([
            "ssh", "lou@192.168.1.119", command
        ], capture_output=True, text=True, timeout=120)
        
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

def install_cloudflared():
    """Install cloudflared on Vonnegut."""
    print("📦 Installing cloudflared...")
    
    install_commands = """
# Download and install cloudflared
cd /tmp
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb || sudo apt-get install -f -y
which cloudflared
cloudflared version
"""
    
    success, stdout, stderr = ssh_command(install_commands)
    
    if success:
        print("✅ Cloudflared installed successfully")
        print(f"📋 Version info: {stdout}")
        return True
    else:
        print("❌ Failed to install cloudflared:")
        print(f"Error: {stderr}")
        return False

def setup_tunnel():
    """Set up and start the Cloudflare tunnel."""
    print("☁️ Setting up Cloudflare tunnel...")
    
    # 1. Create tunnel configuration
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
    
    # 2. Start tunnel
    print("🚀 Starting Cloudflare tunnel...")
    
    start_tunnel_command = """
cd /home/lou/observatory
# Stop any existing tunnel
pkill -f cloudflared 2>/dev/null || true
sleep 2

# Start new tunnel
nohup cloudflared tunnel --config cloudflared-config.yml run > tunnel.log 2>&1 &
echo "Tunnel started with PID: $!"
sleep 5

# Check if it's running
ps aux | grep cloudflared | grep -v grep
"""
    
    success, stdout, stderr = ssh_command(start_tunnel_command)
    
    if success:
        print("✅ Tunnel started")
        print(f"📋 Output: {stdout}")
    else:
        print("❌ Failed to start tunnel:")
        print(f"Error: {stderr}")
        return False
    
    # 3. Wait and check logs
    print("⏳ Waiting for tunnel to connect...")
    time.sleep(20)
    
    success, stdout, stderr = ssh_command("cd /home/lou/observatory && tail -15 tunnel.log")
    if success:
        print("📋 Tunnel logs:")
        print(stdout)
    
    return True

def test_access():
    """Test external access to Observatory."""
    print("🌐 Testing external access...")
    
    # Wait a bit more for DNS propagation
    time.sleep(10)
    
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
        print("💡 DNS may still be propagating. Try accessing manually:")
        print("   https://observatory.niclon.com")
        return False

def main():
    """Main setup process."""
    print("🔧 Setting up Observatory with Cloudflare tunnel on Vonnegut")
    print("=" * 60)
    
    # 1. Install cloudflared
    if not install_cloudflared():
        return False
    
    # 2. Set up tunnel
    if not setup_tunnel():
        return False
    
    # 3. Test access
    test_access()
    
    print("\n🎉 Setup completed!")
    print("🌐 Observatory: https://observatory.niclon.com")
    print("📊 Local access: http://192.168.1.119:8888")
    print("\n💡 Next steps:")
    print("1. Set up Prometheus to scrape Observatory metrics")
    print("2. Configure Grafana with Prometheus data source")
    print("3. Create Observatory dashboards in Grafana")
    
    return True

if __name__ == "__main__":
    main()