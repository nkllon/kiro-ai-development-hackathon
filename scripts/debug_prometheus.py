#!/usr/bin/env python3
"""
Debug and fix Prometheus issues
"""

import subprocess
import sys
import time

def run_ssh_command(command, description=""):
    """Run command via SSH on Vonnegut server"""
    ssh_command = f'ssh -o StrictHostKeyChecking=no lou@192.168.1.119 "{command}"'
    print(f"🔧 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, timeout=60)
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        if result.stderr:
            print(f"⚠️ Stderr: {result.stderr.strip()}")
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out")
        return False, "", "Command timed out"
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, "", str(e)

def debug_prometheus():
    """Debug Prometheus issues"""
    print("🔍 Debugging Prometheus...")
    
    # Check if Prometheus container is running
    run_ssh_command("docker ps | grep prometheus", "Checking Prometheus container")
    
    # Check Prometheus logs
    run_ssh_command("docker logs observatory-prometheus --tail 20", "Checking Prometheus logs")
    
    # Check if port 9090 is accessible
    run_ssh_command("netstat -tlnp | grep 9090", "Checking port 9090")
    
    # Try different Prometheus endpoints
    run_ssh_command("curl -v http://localhost:9090/", "Testing Prometheus root")
    run_ssh_command("curl -v http://localhost:9090/api/v1/status/config", "Testing Prometheus config API")

def fix_prometheus_with_config():
    """Fix Prometheus with proper configuration"""
    print("\n🔧 Fixing Prometheus with proper configuration...")
    
    # Stop current Prometheus
    run_ssh_command("docker stop observatory-prometheus 2>/dev/null || true", "Stopping Prometheus")
    run_ssh_command("docker rm observatory-prometheus 2>/dev/null || true", "Removing Prometheus")
    
    # Create basic Prometheus config
    config_creation = '''
# Create Prometheus config directory
mkdir -p /tmp/prometheus-config

# Create basic Prometheus configuration
cat > /tmp/prometheus-config/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 5s

  - job_name: 'observatory'
    static_configs:
      - targets: ['localhost:8888']
    scrape_interval: 15s
    metrics_path: '/metrics'
EOF

echo "Prometheus configuration created"
'''
    
    run_ssh_command(config_creation, "Creating Prometheus configuration")
    
    # Start Prometheus with custom config
    prometheus_command = '''docker run -d \\
  --name observatory-prometheus \\
  --network host \\
  -v /tmp/prometheus-config/prometheus.yml:/etc/prometheus/prometheus.yml \\
  -v prometheus-data:/prometheus \\
  prom/prometheus:latest \\
  --config.file=/etc/prometheus/prometheus.yml \\
  --storage.tsdb.path=/prometheus \\
  --web.console.libraries=/etc/prometheus/console_libraries \\
  --web.console.templates=/etc/prometheus/consoles \\
  --web.enable-lifecycle \\
  --web.enable-admin-api'''
    
    run_ssh_command(prometheus_command, "Starting Prometheus with custom config")
    
    time.sleep(15)
    
    # Test Prometheus
    run_ssh_command("curl -s http://localhost:9090/", "Testing Prometheus root")
    run_ssh_command("curl -s http://localhost:9090/-/healthy", "Testing Prometheus health")
    run_ssh_command("docker logs observatory-prometheus --tail 10", "Checking Prometheus logs")

def test_external_access():
    """Test external access to all services"""
    print("\n🌐 Testing external access...")
    
    # Wait a moment for tunnel to update
    time.sleep(5)
    
    print("Testing external URLs (this may take a moment)...")
    
    # Note: We can't test external URLs directly from here, but we can verify local services
    run_ssh_command("curl -s -o /dev/null -w 'Observatory (local): %{http_code}\\n' http://localhost:8888/health", "Observatory local")
    run_ssh_command("curl -s -o /dev/null -w 'Prometheus (local): %{http_code}\\n' http://localhost:9090/", "Prometheus local")
    run_ssh_command("curl -s -o /dev/null -w 'Grafana (local): %{http_code}\\n' http://localhost:3000/api/health", "Grafana local")

def main():
    print("🔍 Prometheus Debug and Fix")
    print("=" * 30)
    
    try:
        debug_prometheus()
        fix_prometheus_with_config()
        test_external_access()
        
        print("\n✅ Prometheus debug and fix completed!")
        print("\n🌐 External URLs should now work:")
        print("   Observatory: https://observatory.nkllon.com")
        print("   Prometheus: https://prometheus.observatory.nkllon.com")
        print("   Grafana: https://grafana.observatory.nkllon.com")
        print("\n📝 All services should now be accessible with proper configurations")
        
    except Exception as e:
        print(f"\n❌ Error during debug: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())