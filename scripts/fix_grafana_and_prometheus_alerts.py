#!/usr/bin/env python3
"""
Fix Grafana configuration and add Prometheus alerts
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

def fix_grafana_configuration():
    """Fix Grafana configuration for proper subdomain access"""
    print("🔧 Fixing Grafana configuration...")
    
    # Stop Grafana container
    run_ssh_command("docker stop observatory-grafana", "Stopping Grafana container")
    time.sleep(2)
    
    # Create proper Grafana configuration
    grafana_config = """
# Create Grafana configuration directory
mkdir -p /tmp/grafana-config

# Create custom Grafana configuration
cat > /tmp/grafana-config/grafana.ini << 'EOF'
[server]
http_addr = 0.0.0.0
http_port = 3000
domain = grafana.observatory.nkllon.com
root_url = https://grafana.observatory.nkllon.com/
serve_from_sub_path = false

[auth.anonymous]
enabled = true
org_name = Main Org.
org_role = Viewer
hide_version = false

[security]
admin_user = admin
admin_password = admin
allow_embedding = true
cookie_secure = false

[users]
allow_sign_up = false
allow_org_create = false
auto_assign_org = true
auto_assign_org_role = Viewer

[log]
mode = console
level = info
EOF

echo "Grafana configuration created"
"""
    
    run_ssh_command(grafana_config, "Creating Grafana configuration")
    
    # Restart Grafana with new configuration
    restart_command = """
docker run -d \\
  --name observatory-grafana-new \\
  --network host \\
  -v /tmp/grafana-config/grafana.ini:/etc/grafana/grafana.ini \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_SERVER_DOMAIN=grafana.observatory.nkllon.com \\
  -e GF_SERVER_ROOT_URL=https://grafana.observatory.nkllon.com/ \\
  -e GF_AUTH_ANONYMOUS_ENABLED=true \\
  -e GF_AUTH_ANONYMOUS_ORG_NAME="Main Org." \\
  -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer \\
  -e GF_SECURITY_ADMIN_PASSWORD=admin \\
  grafana/grafana:latest
"""
    
    run_ssh_command(restart_command, "Starting Grafana with new configuration")
    
    # Remove old container
    run_ssh_command("docker rm observatory-grafana", "Removing old Grafana container")
    run_ssh_command("docker rename observatory-grafana-new observatory-grafana", "Renaming new container")
    
    time.sleep(10)
    
    # Test Grafana
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing Grafana health")

def add_prometheus_alerts():
    """Add basic Prometheus alerting rules"""
    print("\n🚨 Adding Prometheus alerting rules...")
    
    # Create alerting rules
    alert_rules = """
# Create Prometheus alerting rules directory
mkdir -p /tmp/prometheus-rules

# Create basic alerting rules
cat > /tmp/prometheus-rules/observatory.yml << 'EOF'
groups:
  - name: observatory.rules
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
      
      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Redis service is down"
          description: "Redis service has been down for more than 1 minute."
      
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
EOF

echo "Prometheus alerting rules created"
"""
    
    run_ssh_command(alert_rules, "Creating Prometheus alerting rules")
    
    # Update Prometheus configuration to include alerting rules
    prometheus_config = """
# Create updated Prometheus configuration
cat > /tmp/prometheus.yml << 'EOF'
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

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']
    scrape_interval: 30s
EOF

echo "Updated Prometheus configuration created"
"""
    
    run_ssh_command(prometheus_config, "Creating updated Prometheus configuration")
    
    # Restart Prometheus with new configuration and rules
    restart_prometheus = """
# Stop current Prometheus
docker stop observatory-prometheus

# Start Prometheus with alerting rules
docker run -d \\
  --name observatory-prometheus-new \\
  --network host \\
  -v /tmp/prometheus.yml:/etc/prometheus/prometheus.yml \\
  -v /tmp/prometheus-rules:/etc/prometheus/rules \\
  -v prometheus-data:/prometheus \\
  prom/prometheus:latest \\
  --config.file=/etc/prometheus/prometheus.yml \\
  --storage.tsdb.path=/prometheus \\
  --web.console.libraries=/etc/prometheus/console_libraries \\
  --web.console.templates=/etc/prometheus/consoles \\
  --web.enable-lifecycle \\
  --web.enable-admin-api

# Remove old container and rename new one
docker rm observatory-prometheus
docker rename observatory-prometheus-new observatory-prometheus
"""
    
    run_ssh_command(restart_prometheus, "Restarting Prometheus with alerting rules")
    
    time.sleep(10)
    
    # Test Prometheus
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/-/healthy", "Testing Prometheus health")

def main():
    print("🔧 Fixing Grafana Configuration and Adding Prometheus Alerts")
    print("=" * 70)
    
    try:
        fix_grafana_configuration()
        add_prometheus_alerts()
        
        print("\n✅ Configuration fixes completed!")
        print("\n🌐 External URLs should now work properly:")
        print("   Observatory: https://observatory.nkllon.com")
        print("   Prometheus: https://prometheus.observatory.nkllon.com")
        print("   Grafana: https://grafana.observatory.nkllon.com (anonymous access)")
        print("\n🚨 Prometheus now has basic alerting rules configured")
        print("📊 Grafana should now load properly with anonymous access")
        print("\n⏰ Note: Allow 1-2 minutes for services to fully start")
        
    except Exception as e:
        print(f"\n❌ Error during configuration: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())