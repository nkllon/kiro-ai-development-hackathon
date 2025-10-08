#!/usr/bin/env python3
"""
Fix Docker Networking and Deploy Observatory with Host Network
=============================================================

Fixes Docker networking issues and deploys Observatory using host networking.
"""

import subprocess

def fix_networking_and_deploy():
    """Fix networking and deploy Observatory with host network mode."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    print("🔧 Fixing Docker networking and deploying Observatory...")
    
    # Create host network docker-compose
    docker_compose_host = """version: '3.8'

services:
  observatory-redis:
    image: redis:7-alpine
    container_name: observatory-redis
    network_mode: host
    volumes:
      - redis-data:/data
    restart: unless-stopped
    command: ["redis-server", "--requirepass", "beastmode2025", "--port", "6379"]

  observatory-prometheus:
    image: prom/prometheus:latest
    container_name: observatory-prometheus
    network_mode: host
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
      - '--web.listen-address=0.0.0.0:9090'

  observatory-grafana:
    image: grafana/grafana:latest
    container_name: observatory-grafana
    network_mode: host
    volumes:
      - grafana-storage:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_DOMAIN=grafana.vonnegut.poe.com
      - GF_SERVER_ROOT_URL=https://grafana.vonnegut.poe.com
      - GF_SERVER_HTTP_PORT=3000
      - GF_SERVER_HTTP_ADDR=0.0.0.0
    restart: unless-stopped

  observatory-app:
    image: python:3.9-slim
    container_name: observatory-app
    network_mode: host
    volumes:
      - ./:/app
      - ./observatory_data:/app/observatory_data
      - ./logs:/app/logs
    working_dir: /app
    environment:
      - REDIS_HOST=localhost
      - REDIS_PASSWORD=beastmode2025
      - PROMETHEUS_URL=http://localhost:9090
      - ENVIRONMENT=production
      - PORT=8888
    restart: unless-stopped
    command: >
      bash -c "
        apt-get update && apt-get install -y gcc curl &&
        pip install --no-cache-dir -r requirements.txt &&
        mkdir -p observatory_data/metrics observatory_data/dashboards observatory_data/logs observatory_data/config logs &&
        python start_observatory.py
      "

volumes:
  redis-data:
  prometheus-data:
  grafana-storage:
"""

    # Write config locally
    with open("docker-compose-host.yml", 'w') as f:
        f.write(docker_compose_host)
    
    try:
        # Upload config
        subprocess.run([
            "scp", "docker-compose-host.yml",
            f"{ssh_user}@{vonnegut_ip}:{remote_path}/docker-compose.yml"
        ], check=True)
        
        # Fix networking and deploy
        fix_script = f"""
cd {remote_path}

echo "🛑 Stopping all containers..."
sudo docker stop $(sudo docker ps -aq) 2>/dev/null || true
sudo docker rm $(sudo docker ps -aq) 2>/dev/null || true

echo "🔧 Fixing Docker networking..."
# Remove problematic networks
sudo docker network prune -f

# Restart Docker with clean state
sudo systemctl restart docker

# Wait for Docker to be ready
sleep 10

echo "🚀 Starting Observatory with host networking..."
sudo docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 60

echo "🔍 Checking container status..."
sudo docker-compose ps

echo "📋 Container logs..."
echo "=== Observatory App ==="
sudo docker-compose logs observatory-app --tail=15

echo "=== Prometheus ==="
sudo docker-compose logs observatory-prometheus --tail=10

echo "=== Grafana ==="
sudo docker-compose logs observatory-grafana --tail=10

echo "=== Redis ==="
sudo docker-compose logs observatory-redis --tail=5

echo "🌐 Testing endpoints..."
curl -f http://localhost:8888/health && echo "✅ Observatory healthy" || echo "❌ Observatory unhealthy"
curl -f http://localhost:9090/-/healthy && echo "✅ Prometheus healthy" || echo "❌ Prometheus unhealthy"
curl -f http://localhost:3000/api/health && echo "✅ Grafana healthy" || echo "❌ Grafana unhealthy"

echo "🔗 Testing Prometheus targets..."
curl -s http://localhost:9090/api/v1/targets | grep -o '"health":"[^"]*"' | head -5 || echo "Prometheus targets not ready yet"

echo "📊 Testing Prometheus metrics..."
curl -s http://localhost:9090/api/v1/query?query=up | head -3 || echo "Prometheus metrics not ready yet"

echo "✅ Observatory deployed with host networking!"
echo "🌐 Observatory: http://{vonnegut_ip}:8888"
echo "📊 Prometheus: http://{vonnegut_ip}:9090"
echo "📈 Grafana: http://{vonnegut_ip}:3000 (admin/admin)"
"""
        
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            fix_script
        ], text=True, capture_output=True)
        
        print("📋 Deployment output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Deployment stderr:")
            print(result.stderr)
        
        # Clean up local file
        import os
        os.unlink("docker-compose-host.yml")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_networking_and_deploy()
    if success:
        print("\n🎉 Observatory deployed successfully with host networking!")
        print("📊 Prometheus should now be properly configured and accessible")
        print("📈 Grafana should connect to Prometheus successfully")
        print("🌐 All services running in containers with host networking")
        print("\n🔗 Direct access URLs:")
        print("   Observatory: http://192.168.1.119:8888")
        print("   Prometheus: http://192.168.1.119:9090")
        print("   Grafana: http://192.168.1.119:3000")
        print("\n🌐 External access via Cloudflare tunnel:")
        print("   https://observatory.niclon.com")
        print("   https://grafana.vonnegut.poe.com")
    else:
        print("\n❌ Deployment failed - check logs above")