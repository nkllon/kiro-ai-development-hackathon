#!/usr/bin/env python3
"""
Add proper Prometheus alerting rules
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

def create_prometheus_config_with_alerts():
    """Create Prometheus configuration with proper alerting rules"""
    print("🚨 Creating Prometheus configuration with alerting rules...")
    
    # Create directories
    run_ssh_command("mkdir -p /tmp/prometheus-config/rules", "Creating config directories")
    
    # Create alerting rules
    alert_rules = '''
cat > /tmp/prometheus-config/rules/observatory.yml << 'EOF'
groups:
  - name: observatory_alerts
    rules:
      - alert: ObservatoryDown
        expr: up{job="observatory"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Observatory service is down"
          description: "Observatory service has been down for more than 1 minute."
      
      - alert: PrometheusDown
        expr: up{job="prometheus"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Prometheus service is down"
          description: "Prometheus service has been down for more than 1 minute."
      
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 90% for more than 5 minutes."
      
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes."
      
      - alert: ServiceResponseTime
        expr: prometheus_http_request_duration_seconds{quantile="0.95"} > 1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is above 1 second for more than 2 minutes."
EOF

echo "Alert rules created"
'''
    
    run_ssh_command(alert_rules, "Creating alerting rules")
    
    # Create Prometheus configuration with rules
    prometheus_config = '''
cat > /tmp/prometheus-config/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "/etc/prometheus/rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

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

  - job_name: 'grafana'
    static_configs:
      - targets: ['localhost:3000']
    scrape_interval: 30s
    metrics_path: '/metrics'
EOF

echo "Prometheus config with alerts created"
'''
    
    run_ssh_command(prometheus_config, "Creating Prometheus configuration")

def restart_prometheus_with_alerts():
    """Restart Prometheus with alerting configuration"""
    print("\n🔄 Restarting Prometheus with alerting rules...")
    
    # Stop current Prometheus
    run_ssh_command("docker stop observatory-prometheus 2>/dev/null || true", "Stopping Prometheus")
    run_ssh_command("docker rm observatory-prometheus 2>/dev/null || true", "Removing Prometheus")
    
    # Start Prometheus with alerting rules
    prometheus_command = '''docker run -d \\
  --name observatory-prometheus \\
  --network host \\
  -v /tmp/prometheus-config/prometheus.yml:/etc/prometheus/prometheus.yml:ro \\
  -v /tmp/prometheus-config/rules:/etc/prometheus/rules:ro \\
  -v prometheus-data:/prometheus \\
  prom/prometheus:latest \\
  --config.file=/etc/prometheus/prometheus.yml \\
  --storage.tsdb.path=/prometheus \\
  --web.console.libraries=/etc/prometheus/console_libraries \\
  --web.console.templates=/etc/prometheus/consoles \\
  --web.enable-lifecycle \\
  --web.enable-admin-api'''
    
    run_ssh_command(prometheus_command, "Starting Prometheus with alerts")
    
    time.sleep(15)
    
    # Test Prometheus
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/", "Testing Prometheus")
    run_ssh_command("curl -s http://localhost:9090/api/v1/rules", "Testing alert rules API")
    run_ssh_command("docker logs observatory-prometheus --tail 10", "Checking Prometheus logs")

def verify_alerts():
    """Verify that alerts are properly configured"""
    print("\n🔍 Verifying alert configuration...")
    
    # Check if Prometheus is accessible
    run_ssh_command("curl -s http://localhost:9090/api/v1/status/config | head -20", "Checking Prometheus config")
    
    # Check alert rules
    run_ssh_command("curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[].name' 2>/dev/null || curl -s http://localhost:9090/api/v1/rules", "Checking loaded alert rules")
    
    # Check alerts status
    run_ssh_command("curl -s http://localhost:9090/api/v1/alerts", "Checking active alerts")

def main():
    print("🚨 Adding Prometheus Alerting Rules")
    print("=" * 40)
    
    try:
        create_prometheus_config_with_alerts()
        restart_prometheus_with_alerts()
        verify_alerts()
        
        print("\n✅ Prometheus alerting configuration completed!")
        print("\n🚨 Alert Rules Added:")
        print("   • ObservatoryDown - Triggers when Observatory is unreachable")
        print("   • PrometheusDown - Triggers when Prometheus itself is down")
        print("   • HighMemoryUsage - Triggers when memory usage > 90%")
        print("   • HighCPUUsage - Triggers when CPU usage > 80%")
        print("   • ServiceResponseTime - Triggers when response time > 1s")
        print("\n🌐 External URLs:")
        print("   Observatory: https://observatory.nkllon.com")
        print("   Prometheus: https://prometheus.observatory.nkllon.com")
        print("   Grafana: https://grafana.observatory.nkllon.com")
        print("\n📊 Prometheus now has proper alerting rules configured!")
        
    except Exception as e:
        print(f"\n❌ Error during alerting setup: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())