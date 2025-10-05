#!/usr/bin/env python3
"""
Check Tunnel Status on Vonnegut
===============================

Checks the current status of Cloudflare tunnel on Vonnegut.
"""

import subprocess

def check_tunnel_status():
    """Check tunnel status on Vonnegut."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    print("🔍 Checking tunnel status on Vonnegut...")
    
    status_script = f"""
cd {remote_path}

echo "🌐 Cloudflared installation status..."
which cloudflared || echo "cloudflared not found in PATH"
cloudflared --version 2>/dev/null || echo "cloudflared not working"

echo ""
echo "🔑 Tunnel credentials status..."
ls -la /home/lou/.cloudflared/ 2>/dev/null || echo "Cloudflared directory not found"

echo ""
echo "📋 Tunnel processes..."
ps aux | grep cloudflared | grep -v grep || echo "No cloudflared processes running"

echo ""
echo "📄 Tunnel logs..."
if [ -f "tunnel.log" ]; then
    echo "=== Last 20 lines of tunnel.log ==="
    tail -20 tunnel.log
else
    echo "No tunnel.log file found"
fi

echo ""
echo "🔧 Tunnel configuration..."
if [ -f "/etc/cloudflared/config.yml" ]; then
    echo "=== Tunnel config exists ==="
    sudo cat /etc/cloudflared/config.yml
else
    echo "No tunnel config found at /etc/cloudflared/config.yml"
fi

echo ""
echo "🌐 Network connectivity..."
curl -I https://www.cloudflare.com 2>&1 | head -3 || echo "No internet connectivity"

echo ""
echo "🔗 Local services status..."
curl -f http://localhost:8888/health > /dev/null 2>&1 && echo "✅ Observatory local OK" || echo "❌ Observatory local failed"
curl -f http://localhost:9090/-/healthy > /dev/null 2>&1 && echo "✅ Prometheus local OK" || echo "❌ Prometheus local failed"
curl -f http://localhost:3000/api/health > /dev/null 2>&1 && echo "✅ Grafana local OK" || echo "❌ Grafana local failed"
"""
    
    try:
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            status_script
        ], text=True, capture_output=True)
        
        print("📋 Tunnel status output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Tunnel status stderr:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

if __name__ == "__main__":
    check_tunnel_status()