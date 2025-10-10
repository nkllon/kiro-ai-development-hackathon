#!/usr/bin/env python3
"""
Fix Docker Configuration and Deploy Observatory on Vonnegut
==========================================================

Fixes Docker configuration issues and deploys containerized Observatory.
"""

import subprocess
import yaml
from pathlib import Path

def fix_docker_and_deploy():
    """Fix Docker configuration and deploy Observatory."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    print("🔧 Fixing Docker configuration and deploying Observatory on Vonnegut...")
    
    # Create complete deployment configuration
    docker_compose = """version: '3.8'

services:
  observatory-redis:
    image: redis:7-alpine
    container_name: observatory-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    command: ["redis-server", "--requirepass", "beastmode2025"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  observatory-prometheus:
    image: prom/prometheus:latest
    container_name: observatory-prometheus
    ports:
      - "9090:9090"
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
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9090/-/healthy"]
      interval: 10s
      timeout: 3s
      retries: 5

  observatory-grafana:
    image: grafana/grafana:latest
    container_name: observatory-grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-storage:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_DOMAIN=grafana.vonnegut.poe.com
      - GF_SERVER_ROOT_URL=https://grafana.vonnegut.poe.com
    restart: unless-stopped
    depends_on:
      observatory-prometheus:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1"]
      interval: 10s
      timeout: 3s
      retries: 5

  observatory-app:
    image: python:3.9-slim
    container_name: observatory-app
    ports:
      - "8888:8888"
    volumes:
      - ./:/app
      - ./observatory_data:/app/observatory_data
      - ./logs:/app/logs
    working_dir: /app
    environment:
      - REDIS_HOST=observatory-redis
      - REDIS_PASSWORD=beastmode2025
      - PROMETHEUS_URL=http://observatory-prometheus:9090
      - ENVIRONMENT=production
    depends_on:
      observatory-redis:
        condition: service_healthy
      observatory-prometheus:
        condition: service_healthy
    restart: unless-stopped
    command: >
      bash -c "
        apt-get update && apt-get install -y gcc curl &&
        pip install --no-cache-dir -r requirements.txt &&
        mkdir -p observatory_data/metrics observatory_data/dashboards observatory_data/logs observatory_data/config logs &&
        python start_observatory.py
      "
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8888/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  redis-data:
  prometheus-data:
  grafana-storage:

networks:
  default:
    driver: bridge
"""

    prometheus_config = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'observatory'
    static_configs:
      - targets: ['observatory-app:8888']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'redis'
    static_configs:
      - targets: ['observatory-redis:6379']
"""

    # Write configs locally
    with open("docker-compose.yml", 'w') as f:
        f.write(docker_compose)
    
    with open("prometheus.yml", 'w') as f:
        f.write(prometheus_config)
    
    try:
        # Upload configs
        subprocess.run([
            "scp", "docker-compose.yml", "prometheus.yml",
            f"{ssh_user}@{vonnegut_ip}:{remote_path}/"
        ], check=True)
        
        # Fix Docker and deploy
        fix_and_deploy_script = f"""
cd {remote_path}

echo "🔧 Fixing Docker configuration..."
# Fix Docker daemon configuration
sudo systemctl stop docker
sudo rm -f /var/lib/docker/daemon.json
echo '{{"hosts": ["unix:///var/run/docker.sock"]}}' | sudo tee /etc/docker/daemon.json
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group if not already
sudo usermod -aG docker {ssh_user}

# Wait for Docker to be ready
sleep 10

echo "🧹 Cleaning up old containers..."
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true
docker system prune -af

echo "🚀 Starting Observatory services..."
docker compose up -d

echo "⏳ Waiting for services to start..."
sleep 60

echo "🔍 Checking service status..."
docker compose ps

echo "🏥 Health checks..."
docker compose logs observatory-app --tail=20
docker compose logs observatory-prometheus --tail=10
docker compose logs observatory-grafana --tail=10

echo "🌐 Testing endpoints..."
curl -f http://localhost:8888/health && echo "✅ Observatory healthy" || echo "❌ Observatory unhealthy"
curl -f http://localhost:9090/-/healthy && echo "✅ Prometheus healthy" || echo "❌ Prometheus unhealthy"
curl -f http://localhost:3000/api/health && echo "✅ Grafana healthy" || echo "❌ Grafana unhealthy"

echo "✅ Deployment complete!"
echo "🌐 Observatory: http://{vonnegut_ip}:8888"
echo "📊 Prometheus: http://{vonnegut_ip}:9090"
echo "📈 Grafana: http://{vonnegut_ip}:3000"
"""
        
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            fix_and_deploy_script
        ], text=True, capture_output=True)
        
        print("📋 Deployment output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Deployment stderr:")
            print(result.stderr)
        
        # Clean up local files
        Path("docker-compose.yml").unlink()
        Path("prometheus.yml").unlink()
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_docker_and_deploy()
    if success:
        print("\n🎉 Observatory containerized deployment successful!")
        print("📊 Prometheus should now be properly configured")
        print("📈 Grafana should connect to Prometheus")
        print("🌐 All services running in containers")
    else:
        print("\n❌ Deployment failed - check logs above")