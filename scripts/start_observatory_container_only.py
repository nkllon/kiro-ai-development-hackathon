#!/usr/bin/env python3
"""
Start Observatory Container Only
===============================

Starts just the Observatory container since other services are running.
"""

import subprocess

def start_observatory_container():
    """Start Observatory container."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    print("🚀 Starting Observatory container on Vonnegut...")
    
    start_script = f"""
cd {remote_path}

echo "🔍 Current status..."
echo "Redis: $(curl -s http://localhost:6379 2>&1 | head -1 || echo 'Redis running on 6379')"
echo "Prometheus: $(curl -s http://localhost:9090/-/healthy 2>&1 || echo 'Not responding')"
echo "Grafana: $(curl -s http://localhost:3000/api/health 2>&1 || echo 'Not responding')"

echo ""
echo "🛑 Stopping any existing Observatory..."
sudo docker stop observatory-app 2>/dev/null || true
sudo docker rm observatory-app 2>/dev/null || true
sudo pkill -f "python.*start_observatory" || true

echo ""
echo "🚀 Starting Observatory container..."
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
  -e PORT=8888 \\
  python:3.9-slim \\
  bash -c "
    echo 'Installing dependencies...' &&
    apt-get update -qq &&
    apt-get install -y -qq gcc curl git &&
    echo 'Installing Python packages...' &&
    pip install -q -r requirements.txt &&
    echo 'Creating directories...' &&
    mkdir -p observatory_data/metrics observatory_data/dashboards observatory_data/logs observatory_data/config logs &&
    echo 'Starting Observatory...' &&
    python start_observatory.py
  "

echo ""
echo "⏳ Waiting for Observatory to start..."
sleep 45

echo ""
echo "🔍 Checking Observatory container..."
sudo docker ps | grep observatory-app

echo ""
echo "📋 Observatory container logs..."
sudo docker logs observatory-app --tail=25

echo ""
echo "🌐 Testing Observatory..."
for i in {{1..10}}; do
  if curl -f http://localhost:8888/health 2>/dev/null; then
    echo "✅ Observatory is responding!"
    break
  else
    echo "⏳ Attempt $i: Observatory not ready yet..."
    sleep 5
  fi
done

echo ""
echo "🔗 Final status check..."
curl -f http://localhost:8888/health && echo "✅ Observatory healthy" || echo "❌ Observatory unhealthy"
curl -f http://localhost:9090/-/healthy && echo "✅ Prometheus healthy" || echo "❌ Prometheus unhealthy"
curl -f http://localhost:3000/api/health && echo "✅ Grafana healthy" || echo "❌ Grafana unhealthy"

echo ""
echo "🌐 Port status..."
sudo netstat -tlnp | grep -E ':(8888|9090|3000|6379)'

echo ""
echo "✅ Observatory container started!"
echo "🌐 Observatory: http://{vonnegut_ip}:8888"
echo "📊 Prometheus: http://{vonnegut_ip}:9090"
echo "📈 Grafana: http://{vonnegut_ip}:3000"
"""
    
    try:
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            start_script
        ], text=True, capture_output=True)
        
        print("📋 Startup output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Startup stderr:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        return False

if __name__ == "__main__":
    success = start_observatory_container()
    if success:
        print("\n🎉 Observatory container started successfully!")
        print("📊 Observatory should now be fully functional")
        print("🌐 All services are now containerized")
    else:
        print("\n❌ Startup failed - check logs above")