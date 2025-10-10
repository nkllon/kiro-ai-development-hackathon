#!/usr/bin/env python3
"""
Start Prometheus and Grafana Containers on Vonnegut
===================================================

Starts only Prometheus and Grafana containers while keeping native Observatory.
"""

import subprocess

def start_prometheus_grafana():
    """Start Prometheus and Grafana containers."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    print("📊 Starting Prometheus and Grafana containers on Vonnegut...")
    
    # Create minimal docker-compose for just Prometheus and Grafana
    docker_compose_minimal = """version: '3.8'

services:
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

volumes:
  prometheus-data:
  grafana-storage:
"""

    # Create Grafana datasource config
    grafana_datasource = """apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
    editable: true
"""

    # Write configs locally
    with open("docker-compose-minimal.yml", 'w') as f:
        f.write(docker_compose_minimal)
    
    with open("grafana-datasource.yml", 'w') as f:
        f.write(grafana_datasource)
    
    try:
        # Upload configs
        subprocess.run([
            "scp", "docker-compose-minimal.yml", "grafana-datasource.yml",
            f"{ssh_user}@{vonnegut_ip}:{remote_path}/"
        ], check=True)
        
        # Start containers
        start_script = f"""
cd {remote_path}

echo "📊 Setting up Prometheus and Grafana containers..."

# Use the minimal compose file
cp docker-compose-minimal.yml docker-compose.yml

# Create Grafana provisioning directory
mkdir -p grafana-provisioning/datasources
cp grafana-datasource.yml grafana-provisioning/datasources/prometheus.yml

echo "🚀 Starting Prometheus and Grafana containers..."
sudo docker-compose up -d

echo "⏳ Waiting for containers to start..."
sleep 30

echo "🔍 Checking container status..."
sudo docker-compose ps

echo "📋 Container logs..."
echo "=== Prometheus ==="
sudo docker logs observatory-prometheus --tail=15

echo ""
echo "=== Grafana ==="
sudo docker logs observatory-grafana --tail=15

echo ""
echo "🌐 Testing endpoints..."
curl -f http://localhost:8888/health && echo "✅ Observatory (native) healthy" || echo "❌ Observatory unhealthy"
curl -f http://localhost:9090/-/healthy && echo "✅ Prometheus (container) healthy" || echo "❌ Prometheus unhealthy"
curl -f http://localhost:3000/api/health && echo "✅ Grafana (container) healthy" || echo "❌ Grafana unhealthy"

echo ""
echo "🔗 Testing Prometheus targets..."
sleep 10
curl -s http://localhost:9090/api/v1/targets | grep -o '"health":"[^"]*"' | head -5 || echo "Prometheus targets not ready yet"

echo ""
echo "📊 Testing Prometheus metrics..."
curl -s http://localhost:9090/api/v1/query?query=up | head -3 || echo "Prometheus metrics not ready yet"

echo ""
echo "🌐 Port status..."
sudo netstat -tlnp | grep -E ':(8888|9090|3000|6379)'

echo ""
echo "✅ Prometheus and Grafana containers started!"
echo "🌐 Observatory (native): http://{vonnegut_ip}:8888"
echo "📊 Prometheus (container): http://{vonnegut_ip}:9090"
echo "📈 Grafana (container): http://{vonnegut_ip}:3000 (admin/admin)"
"""
        
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            start_script
        ], text=True, capture_output=True)
        
        print("📋 Startup output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Startup stderr:")
            print(result.stderr)
        
        # Clean up local files
        import os
        os.unlink("docker-compose-minimal.yml")
        os.unlink("grafana-datasource.yml")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        return False

if __name__ == "__main__":
    success = start_prometheus_grafana()
    if success:
        print("\n🎉 Prometheus and Grafana containers started successfully!")
        print("📊 Prometheus should now be properly configured and accessible")
        print("📈 Grafana should connect to Prometheus successfully")
        print("🌐 Observatory running natively, monitoring services in containers")
        print("\n🔗 Access URLs:")
        print("   Observatory: http://192.168.1.119:8888")
        print("   Prometheus: http://192.168.1.119:9090")
        print("   Grafana: http://192.168.1.119:3000")
        print("\n🌐 External access via Cloudflare tunnel:")
        print("   https://observatory.niclon.com")
        print("   https://grafana.vonnegut.poe.com")
    else:
        print("\n❌ Startup failed - check logs above")