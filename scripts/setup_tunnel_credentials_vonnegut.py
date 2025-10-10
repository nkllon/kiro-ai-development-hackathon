#!/usr/bin/env python3
"""
Setup Tunnel Credentials on Vonnegut
====================================

Sets up Cloudflare tunnel credentials and configuration on Vonnegut.
"""

import subprocess
from pathlib import Path

def setup_tunnel_credentials():
    """Setup tunnel credentials on Vonnegut."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    print("🔑 Setting up tunnel credentials on Vonnegut...")
    
    # Check if we have local credentials
    local_creds = Path.home() / ".cloudflared" / "d1e53e43-033f-4994-8f46-c83962ae3785.json"
    
    if not local_creds.exists():
        print(f"❌ Local tunnel credentials not found: {local_creds}")
        print("💡 Please ensure tunnel credentials are available locally first")
        return False
    
    print(f"✅ Found local credentials: {local_creds}")
    
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
        # Upload credentials and config
        subprocess.run([
            "scp", str(local_creds), "cloudflared-config.yml",
            f"{ssh_user}@{vonnegut_ip}:{remote_path}/"
        ], check=True)
        
        # Setup tunnel
        setup_script = f"""
cd {remote_path}

echo "🔑 Setting up tunnel credentials and configuration..."

# Create cloudflared directory
mkdir -p /home/lou/.cloudflared

# Copy credentials
cp d1e53e43-033f-4994-8f46-c83962ae3785.json /home/lou/.cloudflared/
chmod 600 /home/lou/.cloudflared/d1e53e43-033f-4994-8f46-c83962ae3785.json

# Setup system config
sudo mkdir -p /etc/cloudflared
sudo cp cloudflared-config.yml /etc/cloudflared/config.yml

echo "🛑 Stopping any existing tunnel..."
sudo pkill -f cloudflared || true
sleep 5

echo "🚀 Starting tunnel..."
nohup cloudflared tunnel --config /etc/cloudflared/config.yml run > tunnel.log 2>&1 &

echo "⏳ Waiting for tunnel to start..."
sleep 15

echo "🔍 Checking tunnel status..."
ps aux | grep cloudflared | grep -v grep || echo "No tunnel process found"

echo "📋 Recent tunnel logs..."
tail -15 tunnel.log || echo "No tunnel logs"

echo "🌐 Testing local services..."
curl -f http://localhost:8888/health > /dev/null 2>&1 && echo "✅ Observatory OK" || echo "❌ Observatory failed"
curl -f http://localhost:9090/-/healthy > /dev/null 2>&1 && echo "✅ Prometheus OK" || echo "❌ Prometheus failed"  
curl -f http://localhost:3000/api/health > /dev/null 2>&1 && echo "✅ Grafana OK" || echo "❌ Grafana failed"

echo "🔗 Testing external access (may take a moment)..."
sleep 10
curl -I https://observatory.niclon.com --max-time 10 2>&1 | head -3 || echo "External access not ready yet"

echo "✅ Tunnel setup complete!"
echo "🌐 External URLs:"
echo "   https://observatory.niclon.com"
echo "   https://grafana.vonnegut.poe.com"
echo "   https://prometheus.vonnegut.poe.com"
"""
        
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            setup_script
        ], text=True, capture_output=True)
        
        print("📋 Setup output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Setup stderr:")
            print(result.stderr)
        
        # Clean up local files
        import os
        os.unlink("cloudflared-config.yml")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_tunnel_credentials()
    if success:
        print("\n🎉 Tunnel credentials and configuration setup complete!")
        print("🌐 External sites should be accessible shortly:")
        print("   https://observatory.niclon.com")
        print("   https://grafana.vonnegut.poe.com")
        print("   https://prometheus.vonnegut.poe.com")
        print("\n💡 It may take a few minutes for DNS to propagate")
    else:
        print("\n❌ Setup failed - check logs above")