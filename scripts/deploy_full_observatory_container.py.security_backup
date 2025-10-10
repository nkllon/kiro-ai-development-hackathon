#!/usr/bin/env python3
"""
Deploy Full Observatory Container on Vonnegut
=============================================

Deploys the complete Observatory as a container with all dependencies.
"""

import subprocess

def deploy_full_observatory():
    """Deploy complete Observatory in container."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    print("🚀 Deploying full Observatory container on Vonnegut...")
    
    # Create complete docker-compose with Observatory container
    docker_compose_full = """version: '3.8'

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
      - ./grafana-provisioning:/etc/grafana/provisioning:ro
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_DOMAIN=grafana.vonnegut.poe.com
      - GF_SERVER_ROOT_URL=https://grafana.vonnegut.poe.com
      - GF_SERVER_HTTP_PORT=3000
      - GF_SERVER_HTTP_ADDR=0.0.0.0
    restart: unless-stopped

  observatory-app:
    build:
      context: .
      dockerfile: Dockerfile.observatory
    container_name: observatory-app
    network_mode: host
    volumes:
      - ./observatory_data:/app/observatory_data
      - ./logs:/app/logs
    environment:
      - REDIS_HOST=localhost
      - REDIS_PASSWORD=beastmode2025
      - PROMETHEUS_URL=http://localhost:9090
      - ENVIRONMENT=production
      - PORT=8888
    restart: unless-stopped
    depends_on:
      - observatory-redis
      - observatory-prometheus

volumes:
  redis-data:
  prometheus-data:
  grafana-storage:
"""

    # Create Dockerfile for Observatory
    dockerfile_observatory = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p observatory_data/metrics observatory_data/dashboards observatory_data/logs observatory_data/config logs

# Expose port
EXPOSE 8888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD curl -f http://localhost:8888/health || exit 1

# Start Observatory
CMD ["python", "start_observatory.py"]
"""

    # Write configs locally
    with open("docker-compose-full.yml", 'w') as f:
        f.write(docker_compose_full)
    
    with open("Dockerfile.observatory", 'w') as f:
        f.write(dockerfile_observatory)
    
    try:
        # Upload configs
        subprocess.run([
            "scp", "docker-compose-full.yml", "Dockerfile.observatory",
            f"{ssh_user}@{vonnegut_ip}:{remote_path}/"
        ], check=True)
        
        # Deploy full Observatory
        deploy_script = f"""
cd {remote_path}

echo "🛑 Stopping existing services..."
# Stop native Observatory process
sudo pkill -f "python.*start_observatory" || true
sudo pkill -f "redis-server" || true

# Stop existing containers
sudo docker-compose down 2>/dev/null || true

echo "🚀 Starting full containerized Observatory..."
# Use the full compose file
cp docker-compose-full.yml docker-compose.yml

# Build and start all services
sudo docker-compose up -d --build

echo "⏳ Waiting for services to start..."
sleep 90

echo "🔍 Checking container status..."
sudo docker-compose ps

echo "📋 Container logs..."
echo "=== Observatory App ==="
sudo docker logs observatory-app --tail=20

echo ""
echo "=== Prometheus ==="
sudo docker logs observatory-prometheus --tail=10

echo ""
echo "=== Grafana ==="
sudo docker logs observatory-grafana --tail=10

echo ""
echo "=== Redis ==="
sudo docker logs observatory-redis --tail=10

echo ""
echo "🌐 Testing endpoints..."
curl -f http://localhost:8888/health && echo "✅ Observatory healthy" || echo "❌ Observatory unhealthy"
curl -f http://localhost:9090/-/healthy && echo "✅ Prometheus healthy" || echo "❌ Prometheus unhealthy"
curl -f http://localhost:3000/api/health && echo "✅ Grafana healthy" || echo "❌ Grafana unhealthy"

echo ""
echo "🔗 Testing Observatory features..."
curl -s http://localhost:8888/api/status | head -5 || echo "Observatory API not ready"

echo ""
echo "📊 Testing Prometheus targets..."
curl -s http://localhost:9090/api/v1/targets | grep -o '"health":"[^"]*"' | head -5 || echo "Prometheus targets not ready"

echo ""
echo "🌐 Port status..."
sudo netstat -tlnp | grep -E ':(8888|9090|3000|6379)'

echo ""
echo "✅ Full Observatory deployment complete!"
echo "🌐 Observatory: http://{vonnegut_ip}:8888"
echo "📊 Prometheus: http://{vonnegut_ip}:9090"
echo "📈 Grafana: http://{vonnegut_ip}:3000 (admin/admin)"
"""
        
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            deploy_script
        ], text=True, capture_output=True)
        
        print("📋 Deployment output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Deployment stderr:")
            print(result.stderr)
        
        # Clean up local files
        import os
        os.unlink("docker-compose-full.yml")
        os.unlink("Dockerfile.observatory")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    success = deploy_full_observatory()
    if success:
        print("\n🎉 Full Observatory containerized deployment successful!")
        print("📊 All services now running in containers")
        print("🌐 Observatory should be fully functional")
        print("\n🔗 Access URLs:")
        print("   Observatory: http://192.168.1.119:8888")
        print("   Prometheus: http://192.168.1.119:9090")
        print("   Grafana: http://192.168.1.119:3000")
    else:
        print("\n❌ Deployment failed - check logs above")