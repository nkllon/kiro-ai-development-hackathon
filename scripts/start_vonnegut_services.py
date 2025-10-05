#!/usr/bin/env python3
"""
Start Vonnegut Services
======================

Simple script to start Observatory, Prometheus, and Grafana on Vonnegut.
"""

import subprocess
import time

def run_ssh_command(command, timeout=120):
    """Run command on Vonnegut via SSH."""
    try:
        result = subprocess.run([
            "ssh", "lou@192.168.1.119", command
        ], text=True, capture_output=True, timeout=timeout)
        
        print("📋 Output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def check_current_status():
    """Check what's currently running."""
    print("🔍 Checking current status...")
    
    command = """
echo "=== Processes ==="
ps aux | grep -E "(observatory|prometheus|grafana)" | grep -v grep

echo ""
echo "=== Ports ==="
netstat -tlnp | grep -E "(8888|9090|3000)" || echo "No services listening"

echo ""
echo "=== Directory ==="
cd /home/lou/observatory && pwd && ls -la
"""
    
    return run_ssh_command(command)

def start_observatory():
    """Start Observatory service."""
    print("🚀 Starting Observatory...")
    
    command = """
cd /home/lou/observatory

# Kill existing
pkill -f "start_observatory" || true

# Check if start_observatory.py exists
if [ -f start_observatory.py ]; then
    echo "Found start_observatory.py"
    
    # Start Observatory
    nohup python3 start_observatory.py > observatory.log 2>&1 &
    
    # Wait and check
    sleep 10
    
    if pgrep -f "start_observatory"; then
        echo "✅ Observatory process started"
        
        # Test health
        sleep 5
        curl -s http://localhost:8888/health || echo "Health check failed"
    else
        echo "❌ Observatory process not found"
        echo "Log contents:"
        tail -10 observatory.log 2>/dev/null || echo "No log file"
    fi
else
    echo "❌ start_observatory.py not found"
    echo "Available files:"
    ls -la *.py 2>/dev/null || echo "No Python files found"
fi
"""
    
    return run_ssh_command(command)

def start_prometheus():
    """Start Prometheus service."""
    print("📊 Starting Prometheus...")
    
    command = """
cd /home/lou/observatory

# Kill existing
pkill -f prometheus || true

# Create simple Prometheus config
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  - job_name: 'observatory'
    static_configs:
      - targets: ['localhost:8888']
    metrics_path: '/metrics'
    scrape_interval: 5s
EOF

# Check if Prometheus binary exists
if command -v prometheus >/dev/null 2>&1; then
    echo "Using system Prometheus"
    nohup prometheus --config.file=prometheus.yml --storage.tsdb.path=./prometheus-data --web.listen-address=0.0.0.0:9090 > prometheus.log 2>&1 &
elif [ -f ./prometheus ]; then
    echo "Using local Prometheus binary"
    nohup ./prometheus --config.file=prometheus.yml --storage.tsdb.path=./prometheus-data --web.listen-address=0.0.0.0:9090 > prometheus.log 2>&1 &
else
    echo "Prometheus not found, installing..."
    wget -q https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
    tar xzf prometheus-2.45.0.linux-amd64.tar.gz
    cp prometheus-2.45.0.linux-amd64/prometheus .
    chmod +x prometheus
    rm -rf prometheus-2.45.0.linux-amd64*
    
    nohup ./prometheus --config.file=prometheus.yml --storage.tsdb.path=./prometheus-data --web.listen-address=0.0.0.0:9090 > prometheus.log 2>&1 &
fi

# Wait and check
sleep 10

if pgrep -f prometheus; then
    echo "✅ Prometheus process started"
    
    # Test health
    curl -s http://localhost:9090/-/healthy || echo "Health check failed"
else
    echo "❌ Prometheus process not found"
    echo "Log contents:"
    tail -10 prometheus.log 2>/dev/null || echo "No log file"
fi
"""
    
    return run_ssh_command(command, timeout=180)

def validate_services():
    """Validate all services."""
    print("🔍 Final validation...")
    
    command = """
cd /home/lou/observatory

echo "=== Final Status ==="
echo "Processes:"
ps aux | grep -E "(observatory|prometheus)" | grep -v grep

echo ""
echo "Ports:"
netstat -tlnp | grep -E "(8888|9090)"

echo ""
echo "Health Checks:"
curl -s -f http://localhost:8888/health && echo "✅ Observatory: OK" || echo "❌ Observatory: FAILED"
curl -s -f http://localhost:9090/-/healthy && echo "✅ Prometheus: OK" || echo "❌ Prometheus: FAILED"

echo ""
echo "Prometheus Targets:"
curl -s http://localhost:9090/api/v1/targets 2>/dev/null | grep -o '"health":"[^"]*"' | head -3 || echo "Could not get targets"
"""
    
    return run_ssh_command(command)

def main():
    """Main execution."""
    print("🎯 Starting Vonnegut Observatory Services")
    print("=" * 45)
    
    # Check current status
    check_current_status()
    
    # Start Observatory
    if not start_observatory():
        print("❌ Observatory startup failed")
        return False
    
    # Start Prometheus
    if not start_prometheus():
        print("❌ Prometheus startup failed")
        return False
    
    # Validate services
    validate_services()
    
    print("\n🎉 Services started on Vonnegut!")
    print("🌐 Observatory: http://192.168.1.119:8888")
    print("📊 Prometheus: http://192.168.1.119:9090")
    print("🔗 External: https://observatory.niclon.com (if tunnel is running)")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)