#!/usr/bin/env python3
"""
Install Docker and Deploy Observatory on Vonnegut
=================================================

Installs Docker properly and deploys containerized Observatory.
"""

import subprocess
import yaml
from pathlib import Path

def install_docker_and_deploy():
    """Install Docker and deploy Observatory."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    print("🐳 Installing Docker and deploying Observatory on Vonnegut...")
    
    # Create deployment configuration
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
    command: ["redis-server", "--requirepass", os.getenv('REDIS_PASSWORD', '')]

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
        
        # Install Docker and deploy
        install_and_deploy_script = f"""
cd {remote_path}

echo "🐳 Installing Docker..."
# Remove old Docker installations
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y \\
    ca-certificates \\
    curl \\
    gnupg \\
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \\
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \\
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker {ssh_user}

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "⏳ Waiting for Docker to be ready..."
sleep 10

echo "🧹 Cleaning up any existing containers..."
sudo docker stop $(sudo docker ps -aq) 2>/dev/null || true
sudo docker rm $(sudo docker ps -aq) 2>/dev/null || true
sudo docker system prune -af

echo "🚀 Starting Observatory services..."
sudo docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 60

echo "🔍 Checking service status..."
sudo docker-compose ps

echo "🏥 Health checks..."
sudo docker-compose logs observatory-app --tail=20
sudo docker-compose logs observatory-prometheus --tail=10
sudo docker-compose logs observatory-grafana --tail=10

echo "🌐 Testing endpoints..."
curl -f http://localhost:8888/health && echo "✅ Observatory healthy" || echo "❌ Observatory unhealthy"
curl -f http://localhost:9090/-/healthy && echo "✅ Prometheus healthy" || echo "❌ Prometheus unhealthy"
curl -f http://localhost:3000/api/health && echo "✅ Grafana healthy" || echo "❌ Grafana unhealthy"

echo "✅ Installation and deployment complete!"
echo "🌐 Observatory: http://{vonnegut_ip}:8888"
echo "📊 Prometheus: http://{vonnegut_ip}:9090"
echo "📈 Grafana: http://{vonnegut_ip}:3000 (admin/admin)"
"""
        
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            install_and_deploy_script
        ], text=True, capture_output=True)
        
        print("📋 Installation and deployment output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Installation stderr:")
            print(result.stderr)
        
        # Clean up local files
        Path("docker-compose.yml").unlink()
        Path("prometheus.yml").unlink()
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

if __name__ == "__main__":
    success = install_docker_and_deploy()
    if success:
        print("\n🎉 Docker installed and Observatory deployed successfully!")
        print("📊 Prometheus is now properly configured")
        print("📈 Grafana should connect to Prometheus")
        print("🌐 All services running in containers on Vonnegut")
        print("\n🔗 Access URLs:")
        print("   Observatory: http://192.168.1.119:8888")
        print("   Prometheus: http://192.168.1.119:9090")
        print("   Grafana: http://192.168.1.119:3000")
    else:
        print("\n❌ Installation failed - check logs above")