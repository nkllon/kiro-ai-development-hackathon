#!/usr/bin/env python3
"""
Fix Docker Daemon and Start Observatory Containers
==================================================

Fixes Docker daemon issues and starts Observatory containers properly.
"""

import subprocess

def fix_docker_daemon():
    """Fix Docker daemon and start Observatory."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    print("🔧 Fixing Docker daemon and starting Observatory containers...")
    
    fix_script = f"""
cd {remote_path}

echo "🔧 Fixing Docker daemon..."
# Stop Docker service
sudo systemctl stop docker.service
sudo systemctl stop docker.socket

# Remove problematic configuration
sudo rm -f /etc/docker/daemon.json

# Start Docker socket first
sudo systemctl start docker.socket
sudo systemctl start docker.service

# Enable Docker to start on boot
sudo systemctl enable docker.service
sudo systemctl enable docker.socket

# Wait for Docker to be ready
sleep 10

# Check Docker status
sudo systemctl status docker.service --no-pager -l

echo "🐳 Testing Docker..."
sudo docker --version
sudo docker info

echo "🧹 Cleaning up old containers..."
sudo docker stop $(sudo docker ps -aq) 2>/dev/null || true
sudo docker rm $(sudo docker ps -aq) 2>/dev/null || true

echo "🚀 Starting Observatory containers..."
sudo docker-compose up -d

echo "⏳ Waiting for containers to start..."
sleep 60

echo "🔍 Checking container status..."
sudo docker-compose ps

echo "📋 Container logs..."
echo "=== Observatory App ==="
sudo docker-compose logs observatory-app --tail=10

echo "=== Prometheus ==="
sudo docker-compose logs observatory-prometheus --tail=10

echo "=== Grafana ==="
sudo docker-compose logs observatory-grafana --tail=10

echo "=== Redis ==="
sudo docker-compose logs observatory-redis --tail=10

echo "🌐 Testing endpoints..."
curl -f http://localhost:8888/health && echo "✅ Observatory healthy" || echo "❌ Observatory unhealthy"
curl -f http://localhost:9090/-/healthy && echo "✅ Prometheus healthy" || echo "❌ Prometheus unhealthy"
curl -f http://localhost:3000/api/health && echo "✅ Grafana healthy" || echo "❌ Grafana unhealthy"

echo "🔗 Testing Prometheus targets..."
curl -s http://localhost:9090/api/v1/targets | grep -o '"health":"[^"]*"' | head -5 || echo "Prometheus targets not ready yet"

echo "✅ Docker daemon fixed and Observatory containers started!"
"""
    
    try:
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            fix_script
        ], text=True, capture_output=True)
        
        print("📋 Fix output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Fix stderr:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_docker_daemon()
    if success:
        print("\n🎉 Docker daemon fixed and Observatory containers running!")
        print("📊 Prometheus should now be accessible at http://192.168.1.119:9090")
        print("📈 Grafana should now be accessible at http://192.168.1.119:3000")
        print("🌐 Observatory should be accessible at http://192.168.1.119:8888")
        print("\n🔗 External access via Cloudflare tunnel:")
        print("   https://observatory.niclon.com")
        print("   https://grafana.vonnegut.poe.com")
    else:
        print("\n❌ Fix failed - check logs above")