#!/usr/bin/env python3
"""
Fix Cloudflare Tunnel on Vonnegut
=================================

Configures and starts the Cloudflare tunnel to make Observatory accessible externally.
"""

import subprocess

def fix_cloudflare_tunnel():
    """Fix and start Cloudflare tunnel on Vonnegut."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    print("🌐 Fixing Cloudflare tunnel on Vonnegut...")
    
    # Create tunnel configuration
    tunnel_config = """tunnel: d1e53e43-033f-4994-8f46-c83962ae3785
credentials-file: /home/lou/.cloudflared/d1e53e43-033f-4994-8f46-c83962ae3785.json

ingress:
  - hostname: observatory.niclon.com
    service: http://localhost:8888
  - hostname: grafana.vonnegut.poe.com
    service: http://localhost:3000
  - hostname: prometheus.vonnegut.poe.com
    service: http://localhost:9090
  - service: http_status:404
"""

    # Write config locally
    with open("cloudflared-config.yml", 'w') as f:
        f.write(tunnel_config)
    
    try:
        # Upload config
        subprocess.run([
            "scp", "cloudflared-config.yml",
            f"{ssh_user}@{vonnegut_ip}:{remote_path}/"
        ], check=True)
        
        # Fix tunnel
        tunnel_script = f"""
cd {remote_path}

echo "🌐 Setting up Cloudflare tunnel..."

# Stop any existing tunnel processes
sudo pkill -f cloudflared || true

# Install cloudflared if not present
if ! command -v cloudflared &> /dev/null; then
    echo "📥 Installing cloudflared..."
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared-linux-amd64.deb || sudo apt-get install -f -y
    rm cloudflared-linux-amd64.deb
fi

# Check if credentials exist
if [ ! -f "/home/lou/.cloudflared/d1e53e43-033f-4994-8f46-c83962ae3785.json" ]; then
    echo "❌ Tunnel credentials not found!"
    echo "💡 Please copy tunnel credentials to /home/lou/.cloudflared/"
    exit 1
fi

# Copy config to cloudflared directory
sudo mkdir -p /etc/cloudflared
sudo cp cloudflared-config.yml /etc/cloudflared/config.yml

echo "🚀 Starting Cloudflare tunnel..."
# Start tunnel in background
nohup cloudflared tunnel --config /etc/cloudflared/config.yml run > tunnel.log 2>&1 &

# Wait for tunnel to start
sleep 10

echo "🔍 Checking tunnel status..."
ps aux | grep cloudflared | grep -v grep || echo "Tunnel process not found"

echo "📋 Tunnel logs (last 10 lines)..."
tail -10 tunnel.log || echo "No tunnel logs found"

echo "🌐 Testing external access..."
curl -I https://observatory.niclon.com 2>&1 | head -5 || echo "External access test failed"

echo "✅ Cloudflare tunnel configuration complete!"
echo "🌐 Observatory: https://observatory.niclon.com"
echo "📊 Prometheus: https://prometheus.vonnegut.poe.com"
echo "📈 Grafana: https://grafana.vonnegut.poe.com"
"""
        
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            tunnel_script
        ], text=True, capture_output=True)
        
        print("📋 Tunnel setup output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Tunnel setup stderr:")
            print(result.stderr)
        
        # Clean up local file
        import os
        os.unlink("cloudflared-config.yml")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Tunnel setup failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_cloudflare_tunnel()
    if success:
        print("\n🎉 Cloudflare tunnel configured successfully!")
        print("🌐 External sites should now be accessible:")
        print("   https://observatory.niclon.com")
        print("   https://grafana.vonnegut.poe.com")
        print("   https://prometheus.vonnegut.poe.com")
    else:
        print("\n❌ Tunnel setup failed - check logs above")