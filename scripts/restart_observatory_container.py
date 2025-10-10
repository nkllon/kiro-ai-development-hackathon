#!/usr/bin/env python3
"""
Restart Observatory Container on Vonnegut
=========================================

Restarts Observatory as a proper container.
"""

import subprocess

def restart_observatory_container():
    """Restart Observatory in container mode."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    print("🔄 Restarting Observatory container on Vonnegut...")
    
    restart_script = f"""
cd {remote_path}

echo "🛑 Stopping all services..."
# Stop native processes
sudo pkill -f "python.*start_observatory" || true
sudo pkill -f "redis-server.*6379" || true

# Stop containers
sudo docker stop observatory-app observatory-redis observatory-prometheus observatory-grafana 2>/dev/null || true
sudo docker rm observatory-app observatory-redis observatory-prometheus observatory-grafana 2>/dev/null || true

echo "🚀 Starting Observatory containers..."

# Start Redis container
sudo docker run -d \\
  --name observatory-redis \\
  --network host \\
  --restart unless-stopped \\
  redis:7-alpine \\
  redis-server --requirepass beastmode2025 --port 6379

# Wait for Redis
sleep 10

# Start Prometheus container
sudo docker run -d \\
  --name observatory-prometheus \\
  --network host \\
  --restart unless-stopped \\
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml:ro \\
  -v prometheus-data:/prometheus \\
  prom/prometheus:latest \\
  --config.file=/etc/prometheus/prometheus.yml \\
  --storage.tsdb.path=/prometheus \\
  --web.listen-address=0.0.0.0:9090

# Wait for Prometheus
sleep 15

# Start Grafana container
sudo docker run -d \\
  --name observatory-grafana \\
  --network host \\
  --restart unless-stopped \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_SECURITY_ADMIN_PASSWORD=admin \\
  -e GF_SERVER_HTTP_PORT=3000 \\
  grafana/grafana:latest

# Wait for Grafana
sleep 15

# Start Observatory container
sudo docker run -d \\
  --name observatory-app \\
  --network host \\
  --restart unless-stopped \\
  -v $(pwd):/app \\
  -v $(pwd)/observatory_data:/app/observatory_data \\
  -v $(pwd)/logs:/app/logs \\
  -w /app \\
  -e REDIS_HOST=localhost \\
  -e REDIS_PASSWORD=beastmode2025 \\
  -e PROMETHEUS_URL=http://localhost:9090 \\
  -e ENVIRONMENT=production \\
  python:3.9-slim \\
  bash -c "apt-get update && apt-get install -y gcc curl && pip install -r requirements.txt && mkdir -p observatory_data logs && python start_observatory.py"

echo "⏳ Waiting for Observatory to start..."
sleep 60

echo "🔍 Checking container status..."
sudo docker ps

echo "📋 Container logs..."
echo "=== Observatory App ==="
sudo docker logs observatory-app --tail=20

echo ""
echo "=== Redis ==="
sudo docker logs observatory-redis --tail=5

echo ""
echo "=== Prometheus ==="
sudo docker logs observatory-prometheus --tail=5

echo ""
echo "=== Grafana ==="
sudo docker logs observatory-grafana --tail=5

echo ""
echo "🌐 Testing endpoints..."
curl -f http://localhost:8888/health && echo "✅ Observatory healthy" || echo "❌ Observatory unhealthy"
curl -f http://localhost:9090/-/healthy && echo "✅ Prometheus healthy" || echo "❌ Prometheus unhealthy"
curl -f http://localhost:3000/api/health && echo "✅ Grafana healthy" || echo "❌ Grafana unhealthy"

echo ""
echo "🔗 Testing Observatory dashboard..."
curl -s http://localhost:8888/ | head -3 && echo "✅ Observatory dashboard responding" || echo "❌ Observatory dashboard not responding"

echo ""
echo "📊 Testing Observatory API..."
curl -s http://localhost:8888/api/status | head -3 && echo "✅ Observatory API responding" || echo "❌ Observatory API not responding"

echo ""
echo "🌐 Port status..."
sudo netstat -tlnp | grep -E ':(8888|9090|3000|6379)'

echo ""
echo "✅ Observatory containers restarted!"
echo "🌐 Observatory: http://{vonnegut_ip}:8888"
echo "📊 Prometheus: http://{vonnegut_ip}:9090"
echo "📈 Grafana: http://{vonnegut_ip}:3000"
"""
    
    try:
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            restart_script
        ], text=True, capture_output=True)
        
        print("📋 Restart output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Restart stderr:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Restart failed: {e}")
        return False

if __name__ == "__main__":
    success = restart_observatory_container()
    if success:
        print("\n🎉 Observatory containers restarted successfully!")
        print("📊 All services should now be fully containerized")
        print("🌐 Observatory should be fully functional")
    else:
        print("\n❌ Restart failed - check logs above")