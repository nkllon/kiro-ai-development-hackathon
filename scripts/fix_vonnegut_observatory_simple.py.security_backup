#!/usr/bin/env python3
"""
Simple Vonnegut Observatory Fix
==============================

Gets the Observatory working on Vonnegut by:
1. Starting the Observatory application directly
2. Configuring Prometheus properly
3. Setting up Grafana with correct data sources
4. Ensuring Cloudflare tunnel routes correctly
"""

import subprocess
import time
import json

def ssh_command(command: str) -> tuple[bool, str, str]:
    """Execute SSH command on Vonnegut."""
    try:
        result = subprocess.run([
            "ssh", "lou@192.168.1.119", command
        ], capture_output=True, text=True, timeout=60)
        
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def upload_file(local_path: str, remote_path: str) -> bool:
    """Upload file to Vonnegut."""
    try:
        subprocess.run([
            "scp", local_path, f"lou@192.168.1.119:{remote_path}"
        ], check=True)
        return True
    except Exception as e:
        print(f"❌ Failed to upload {local_path}: {e}")
        return False

def fix_observatory():
    """Fix Observatory deployment on Vonnegut."""
    print("🔧 Fixing Observatory on Vonnegut...")
    
    # 1. Stop any existing processes
    print("🛑 Stopping existing processes...")
    ssh_command("pkill -f observatory 2>/dev/null || true")
    ssh_command("pkill -f prometheus 2>/dev/null || true")
    ssh_command("pkill -f grafana 2>/dev/null || true")
    ssh_command("pkill -f cloudflared 2>/dev/null || true")
    
    # 2. Create proper Prometheus config
    print("📊 Creating Prometheus configuration...")
    prometheus_config = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'observatory'
    static_configs:
      - targets: ['localhost:8888']
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
"""
    
    with open("/tmp/prometheus.yml", "w") as f:
        f.write(prometheus_config)
    
    upload_file("/tmp/prometheus.yml", "/home/lou/observatory/prometheus.yml")
    
    # 3. Create startup script
    print("🚀 Creating startup script...")
    startup_script = """#!/bin/bash
cd /home/lou/observatory

# Set environment variables
export REDIS_PASSWORD="beastmode2025"
export PROMETHEUS_URL="http://localhost:9090"

# Start Redis
echo "Starting Redis..."
redis-server --daemonize yes --requirepass $REDIS_PASSWORD --port 6379

# Start Prometheus
echo "Starting Prometheus..."
prometheus --config.file=prometheus.yml --storage.tsdb.path=./prometheus-data --web.listen-address=:9090 &

# Start Grafana
echo "Starting Grafana..."
grafana-server --homepath=/usr/share/grafana --config=/etc/grafana/grafana.ini &

# Wait for services to start
sleep 10

# Start Observatory
echo "Starting Observatory..."
python3 start_observatory_production.py &

# Start Cloudflare tunnel
echo "Starting Cloudflare tunnel..."
cloudflared tunnel --config cloudflared-config.yml run &

echo "All services started!"
"""
    
    with open("/tmp/start_observatory_vonnegut.sh", "w") as f:
        f.write(startup_script)
    
    upload_file("/tmp/start_observatory_vonnegut.sh", "/home/lou/observatory/start_observatory_vonnegut.sh")
    
    # 4. Make script executable and run it
    print("▶️ Starting Observatory services...")
    ssh_command("chmod +x /home/lou/observatory/start_observatory_vonnegut.sh")
    
    success, stdout, stderr = ssh_command("cd /home/lou/observatory && ./start_observatory_vonnegut.sh")
    
    if success:
        print("✅ Observatory services started")
        print("📋 Output:")
        print(stdout)
    else:
        print("❌ Failed to start services:")
        print(stderr)
    
    # 5. Wait and check status
    print("⏳ Waiting for services to initialize...")
    time.sleep(30)
    
    # 6. Check service status
    print("🔍 Checking service status...")
    
    services = [
        ("Redis", "redis-cli -a beastmode2025 ping"),
        ("Prometheus", "curl -s http://localhost:9090/api/v1/status/config | head -1"),
        ("Observatory", "curl -s http://localhost:8888/health"),
        ("Grafana", "curl -s http://localhost:3000/api/health")
    ]
    
    for service, test_cmd in services:
        success, stdout, stderr = ssh_command(test_cmd)
        if success and stdout.strip():
            print(f"✅ {service} is running")
        else:
            print(f"❌ {service} test failed")
    
    # 7. Test external access
    print("🌐 Testing external access...")
    try:
        import requests
        response = requests.get("https://observatory.niclon.com/health", timeout=30)
        if response.status_code == 200:
            print("✅ External access working!")
            print(f"📊 Health status: {response.json()}")
        else:
            print(f"❌ External access failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ External access test failed: {e}")
    
    print("\n🎉 Observatory fix completed!")
    print("🌐 Observatory: https://observatory.niclon.com")
    print("📊 Prometheus: https://prometheus.vonnegut.poe.com")
    print("📈 Grafana: https://grafana.vonnegut.poe.com")

if __name__ == "__main__":
    fix_observatory()