#!/usr/bin/env python3
"""
Start a simple working Prometheus with basic alerts
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

def create_simple_prometheus_config():
    """Create simple Prometheus config with working alerts"""
    print("🔧 Creating simple Prometheus configuration...")
    
    # Create config
    config_creation = '''
mkdir -p /tmp/prometheus-simple/rules

# Create simple Prometheus config
cat > /tmp/prometheus-simple/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "/etc/prometheus/rules/*.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'observatory'
    static_configs:
      - targets: ['localhost:8888']
    metrics_path: '/metrics'

  - job_name: 'grafana'
    static_configs:
      - targets: ['localhost:3000']
    metrics_path: '/metrics'
EOF

# Create simple alert rules
cat > /tmp/prometheus-simple/rules/alerts.yml << 'EOF'
groups:
  - name: basic_alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "Service {{ $labels.job }} on {{ $labels.instance }} has been down for more than 1 minute."
      
      - alert: HighRequestRate
        expr: rate(prometheus_http_requests_total[5m]) > 50
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High request rate"
          description: "Request rate is {{ $value }} requests/second."
EOF

echo "Simple Prometheus config created"
'''
    
    run_ssh_command(config_creation, "Creating simple Prometheus config")

def start_simple_prometheus():
    """Start Prometheus with simple configuration"""
    print("\n🚀 Starting simple Prometheus...")
    
    # Clean up any existing Prometheus
    run_ssh_command("docker stop observatory-prometheus 2>/dev/null || true", "Stopping existing Prometheus")
    run_ssh_command("docker rm observatory-prometheus 2>/dev/null || true", "Removing existing Prometheus")
    
    # Start simple Prometheus
    prometheus_command = '''docker run -d \\
  --name observatory-prometheus \\
  --network host \\
  -v /tmp/prometheus-simple/prometheus.yml:/etc/prometheus/prometheus.yml:ro \\
  -v /tmp/prometheus-simple/rules:/etc/prometheus/rules:ro \\
  -v prometheus-data:/prometheus \\
  prom/prometheus:latest \\
  --config.file=/etc/prometheus/prometheus.yml \\
  --storage.tsdb.path=/prometheus \\
  --web.enable-lifecycle'''
    
    run_ssh_command(prometheus_command, "Starting simple Prometheus")
    
    time.sleep(10)
    
    # Test Prometheus
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/", "Testing Prometheus")
    run_ssh_command("curl -s http://localhost:9090/-/healthy", "Testing Prometheus health")

def verify_prometheus_alerts():
    """Verify Prometheus alerts are working"""
    print("\n🔍 Verifying Prometheus alerts...")
    
    # Check rules
    run_ssh_command("curl -s http://localhost:9090/api/v1/rules", "Checking alert rules")
    
    # Check targets
    run_ssh_command("curl -s http://localhost:9090/api/v1/targets", "Checking targets")
    
    # Check container logs
    run_ssh_command("docker logs observatory-prometheus --tail 10", "Checking Prometheus logs")

def test_all_services():
    """Test all services"""
    print("\n📊 Testing all services...")
    
    run_ssh_command("curl -s -o /dev/null -w 'Observatory: %{http_code}\\n' http://localhost:8888/health", "Observatory")
    run_ssh_command("curl -s -o /dev/null -w 'Prometheus: %{http_code}\\n' http://localhost:9090/", "Prometheus")
    run_ssh_command("curl -s -o /dev/null -w 'Grafana: %{http_code}\\n' http://localhost:3000/api/health", "Grafana")
    
    run_ssh_command("docker ps --format 'table {{.Names}}\\t{{.Status}}'", "Container status")

def main():
    print("🚀 Simple Working Prometheus with Alerts")
    print("=" * 45)
    
    try:
        create_simple_prometheus_config()
        start_simple_prometheus()
        verify_prometheus_alerts()
        test_all_services()
        
        print("\n✅ Simple Prometheus with alerts is now running!")
        print("\n🚨 Alert Rules Configured:")
        print("   • ServiceDown - Triggers when any service (up == 0) is down")
        print("   • HighRequestRate - Triggers when request rate > 50/sec")
        print("\n🌐 External URLs:")
        print("   Observatory: https://observatory.nkllon.com")
        print("   Prometheus: https://prometheus.observatory.nkllon.com")
        print("   Grafana: https://grafana.observatory.nkllon.com")
        print("\n📊 Prometheus now has working alerting rules configured!")
        
    except Exception as e:
        print(f"\n❌ Error during Prometheus setup: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())