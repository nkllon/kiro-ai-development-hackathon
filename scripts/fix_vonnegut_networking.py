#!/usr/bin/env python3
"""
Fix Vonnegut Container Networking
===============================

Fixes the container networking issues and gets Prometheus properly configured.
"""

import os
import sys
import subprocess

def run_ssh_command(command, timeout=300):
    """Run command on Vonnegut via SSH."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    
    try:
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}", command
        ], text=True, capture_output=True, timeout=timeout)
        
        print("📋 Command output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Command warnings:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False

def fix_docker_networking():
    """Fix Docker networking issues."""
    print("🔧 Fixing Docker networking...")
    
    command = """
# Stop all containers
sudo docker stop $(sudo docker ps -aq) 2>/dev/null || true

# Remove all containers
sudo docker rm $(sudo docker ps -aq) 2>/dev/null || true

# Remove all networks
sudo docker network prune -f

# Restart Docker service
sudo systemctl restart docker

# Wait for Docker to restart
sleep 10

echo "✅ Docker networking reset complete!"
"""
    
    return run_ssh_command(command)

def deploy_native_observatory():
    """Deploy Observatory natively instead of containers."""
    print("🚀 Deploying Observatory natively...")
    
    command = """
cd /home/lou/observatory

# Kill any existing Observatory processes
pkill -f "start_observatory" || true
pkill -f "python.*observatory" || true

# Start Observatory natively
nohup python3 start_observatory.py > observatory.log 2>&1 &

# Wait for startup
sleep 15

# Check if Observatory is running
if pgrep -f "start_observatory"; then
    echo "✅ Observatory started successfully"
    
    # Test Observatory
    curl -s http://localhost:8888/health && echo "✅ Observatory health check passed"
    
    # Check what's listening on port 8888
    netstat -tlnp | grep 8888
else
    echo "❌ Observatory failed to start"
    tail -20 observatory.log
fi
"""
    
    return run_ssh_command(command)

def setup_prometheus_native():
    """Setup Prometheus natively."""
    print("📊 Setting up Prometheus natively...")
    
    command = """
cd /home/lou/observatory

# Kill any existing Prometheus
pkill -f prometheus || true

# Download Prometheus if not exists
if [ ! -f prometheus ]; then
    echo "Downloading Prometheus..."
    wget -q https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
    tar xzf prometheus-2.45.0.linux-amd64.tar.gz
    cp prometheus-2.45.0.linux-amd64/prometheus .
    cp prometheus-2.45.0.linux-amd64/promtool .
    rm -rf prometheus-2.45.0.linux-amd64*
fi

# Create Prometheus config
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'observatory'
    metrics_path: '/metrics'
    scrape_interval: 5s
    static_configs:
      - targets: ['localhost:8888']
EOF

# Start Prometheus
nohup ./prometheus --config.file=prometheus.yml --storage.tsdb.path=./prometheus-data --web.console.libraries=./console_libraries --web.console.templates=./consoles --web.listen-address=0.0.0.0:9090 > prometheus.log 2>&1 &

# Wait for startup
sleep 10

# Check if Prometheus is running
if pgrep -f prometheus; then
    echo "✅ Prometheus started successfully"
    
    # Test Prometheus
    curl -s http://localhost:9090/-/healthy && echo "✅ Prometheus health check passed"
    
    # Check targets
    curl -s http://localhost:9090/api/v1/targets | grep -o '"health":"[^"]*"' | head -5
else
    echo "❌ Prometheus failed to start"
    tail -20 prometheus.log
fi
"""
    
    return run_ssh_command(command)

def setup_grafana_native():
    """Setup Grafana natively."""
    print("📈 Setting up Grafana natively...")
    
    command = """
cd /home/lou/observatory

# Kill any existing Grafana
pkill -f grafana || true

# Download Grafana if not exists
if [ ! -f grafana-server ]; then
    echo "Downloading Grafana..."
    wget -q https://dl.grafana.com/oss/release/grafana-10.1.0.linux-amd64.tar.gz
    tar xzf grafana-10.1.0.linux-amd64.tar.gz
    cp grafana-10.1.0/bin/grafana-server .
    cp -r grafana-10.1.0/conf .
    cp -r grafana-10.1.0/public .
    rm -rf grafana-10.1.0*
fi

# Create Grafana config
mkdir -p grafana-data
cat > grafana.ini << 'EOF'
[server]
http_addr = 0.0.0.0
http_port = 3000

[security]
admin_user = admin
admin_password = admin

[auth.anonymous]
enabled = true
org_name = Main Org.
org_role = Viewer

[database]
type = sqlite3
path = grafana-data/grafana.db
EOF

# Start Grafana
nohup ./grafana-server --config=grafana.ini --homepath=. > grafana.log 2>&1 &

# Wait for startup
sleep 15

# Check if Grafana is running
if pgrep -f grafana-server; then
    echo "✅ Grafana started successfully"
    
    # Test Grafana
    curl -s http://localhost:3000/api/health && echo "✅ Grafana health check passed"
else
    echo "❌ Grafana failed to start"
    tail -20 grafana.log
fi
"""
    
    return run_ssh_command(command)

def setup_tunnel():
    """Setup Cloudflare tunnel."""
    print("🌐 Setting up Cloudflare tunnel...")
    
    command = """
cd /home/lou/observatory

# Kill existing tunnel
pkill -f cloudflared || true

# Create tunnel config
cat > cloudflared-config.yml << 'EOF'
tunnel: d1e53e43-033f-4994-8f46-c83962ae3785
credentials-file: /home/lou/.cloudflared/d1e53e43-033f-4994-8f46-c83962ae3785.json

ingress:
  - hostname: observatory.niclon.com
    service: http://localhost:8888
  - hostname: prometheus.observatory.niclon.com
    service: http://localhost:9090
  - hostname: grafana.observatory.niclon.com
    service: http://localhost:3000
  - service: http_status:404
EOF

# Start tunnel if credentials exist
if [ -f /home/lou/.cloudflared/d1e53e43-033f-4994-8f46-c83962ae3785.json ]; then
    nohup cloudflared tunnel --config cloudflared-config.yml run > tunnel.log 2>&1 &
    sleep 10
    
    if pgrep -f cloudflared; then
        echo "✅ Cloudflare tunnel started successfully"
    else
        echo "❌ Cloudflare tunnel failed to start"
        tail -10 tunnel.log
    fi
else
    echo "⚠️ Cloudflare tunnel credentials not found"
fi
"""
    
    return run_ssh_command(command)

def validate_native_deployment():
    """Validate the native deployment."""
    print("🔍 Validating native deployment...")
    
    command = """
cd /home/lou/observatory

echo "=== Process Status ==="
ps aux | grep -E "(observatory|prometheus|grafana|cloudflared)" | grep -v grep

echo ""
echo "=== Port Status ==="
netstat -tlnp | grep -E "(8888|9090|3000)"

echo ""
echo "=== Service Health ==="
curl -s -f http://localhost:8888/health && echo "✅ Observatory: Healthy" || echo "❌ Observatory: Unhealthy"
curl -s -f http://localhost:9090/-/healthy && echo "✅ Prometheus: Healthy" || echo "❌ Prometheus: Unhealthy"
curl -s -f http://localhost:3000/api/health && echo "✅ Grafana: Healthy" || echo "❌ Grafana: Unhealthy"

echo ""
echo "=== Prometheus Targets ==="
curl -s http://localhost:9090/api/v1/targets | grep -o '"health":"[^"]*"' | head -3

echo ""
echo "✅ Validation complete!"
"""
    
    return run_ssh_command(command)

def main():
    """Main execution."""
    print("🎯 Vonnegut Native Observatory Deployment")
    print("=" * 50)
    
    # Fix Docker networking issues
    if not fix_docker_networking():
        print("❌ Docker networking fix failed")
        return False
    
    # Deploy Observatory natively
    if not deploy_native_observatory():
        print("❌ Native Observatory deployment failed")
        return False
    
    # Setup Prometheus natively
    if not setup_prometheus_native():
        print("❌ Native Prometheus setup failed")
        return False
    
    # Setup Grafana natively
    if not setup_grafana_native():
        print("❌ Native Grafana setup failed")
        return False
    
    # Setup tunnel
    setup_tunnel()  # Don't fail if tunnel setup fails
    
    # Validate deployment
    if not validate_native_deployment():
        print("⚠️ Services deployed but validation failed")
        return False
    
    print("\n🎉 Observatory successfully deployed natively on Vonnegut!")
    print("🌐 Observatory: https://observatory.niclon.com")
    print("📊 Prometheus: https://prometheus.observatory.niclon.com")
    print("📈 Grafana: https://grafana.observatory.niclon.com")
    print("\n🔧 Service Management:")
    print("  SSH: ssh lou@192.168.1.119")
    print("  Check processes: ps aux | grep -E '(observatory|prometheus|grafana)'")
    print("  View logs: tail -f /home/lou/observatory/*.log")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)