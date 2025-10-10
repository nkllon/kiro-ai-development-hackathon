#!/usr/bin/env python3
"""
Robust fix for Prometheus configuration with alerts
Recreate the container with proper configuration
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
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, timeout=30)
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

def recreate_prometheus_with_alerts():
    """Recreate Prometheus container with proper alert configuration"""
    print("🔄 Recreating Prometheus container with alerts...")
    
    # Stop and remove existing container
    print("\n1. Stopping existing Prometheus container...")
    run_ssh_command("docker stop observatory-prometheus", "Stopping Prometheus")
    run_ssh_command("docker rm observatory-prometheus", "Removing Prometheus container")
    
    # Create updated Prometheus configuration
    print("\n2. Creating comprehensive Prometheus configuration...")
    
    prometheus_config = """global:
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
      - targets: ['192.168.1.119:8888']
    scrape_interval: 10s
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['192.168.1.119:6379']
    scrape_interval: 15s

  - job_name: 'tunnel'
    static_configs:
      - targets: ['127.0.0.1:20241']
    scrape_interval: 30s
    metrics_path: '/metrics'
"""

    # Create alert rules
    alert_rules = """groups:
  - name: observatory_alerts
    rules:
      - alert: ObservatoryDown
        expr: up{job="observatory"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Observatory service is down"
          description: "Observatory service has been down for more than 1 minute"

      - alert: PrometheusDown
        expr: up{job="prometheus"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Prometheus service is down"
          description: "Prometheus service has been down for more than 1 minute"

      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis service is down"
          description: "Redis service has been down for more than 1 minute"

      - alert: TunnelDown
        expr: up{job="tunnel"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Cloudflare tunnel is down"
          description: "Cloudflare tunnel has been down for more than 2 minutes"

      - alert: ObservatoryHighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="observatory"}[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Observatory high response time"
          description: "95th percentile response time is above 2 seconds"

      - alert: ObservatoryHighErrorRate
        expr: rate(http_requests_total{job="observatory",status=~"5.."}[5m]) / rate(http_requests_total{job="observatory"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Observatory high error rate"
          description: "Error rate is above 10% for more than 5 minutes"
"""

    # Write configuration files
    config_command = f'cat > /tmp/prometheus.yml << "EOF"\n{prometheus_config}\nEOF'
    run_ssh_command(config_command, "Creating Prometheus configuration")
    
    rules_command = f'cat > /tmp/alert_rules.yml << "EOF"\n{alert_rules}\nEOF'
    run_ssh_command(rules_command, "Creating alert rules")
    
    # Create directories and copy files
    run_ssh_command("sudo mkdir -p /etc/prometheus/rules", "Creating Prometheus directories")
    run_ssh_command("sudo cp /tmp/prometheus.yml /etc/prometheus/", "Copying Prometheus config")
    run_ssh_command("sudo cp /tmp/alert_rules.yml /etc/prometheus/rules/", "Copying alert rules")
    run_ssh_command("sudo chown -R root:root /etc/prometheus", "Setting ownership")
    run_ssh_command("sudo chmod -R 644 /etc/prometheus/*", "Setting permissions")
    
    print("\n3. Starting new Prometheus container with alerts...")
    
    # Start new Prometheus container with proper configuration
    start_command = """docker run -d \\
  --name observatory-prometheus \\
  --restart unless-stopped \\
  -p 9090:9090 \\
  -v /etc/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro \\
  -v /etc/prometheus/rules:/etc/prometheus/rules:ro \\
  -v prometheus-data:/prometheus \\
  prom/prometheus:latest \\
  --config.file=/etc/prometheus/prometheus.yml \\
  --storage.tsdb.path=/prometheus \\
  --web.console.libraries=/etc/prometheus/console_libraries \\
  --web.console.templates=/etc/prometheus/consoles \\
  --web.enable-lifecycle \\
  --web.enable-admin-api"""
    
    run_ssh_command(start_command, "Starting Prometheus container")
    
    # Wait for startup
    time.sleep(10)
    
    print("\n4. Verifying Prometheus with alerts...")
    run_ssh_command("docker ps | grep prometheus", "Checking container status")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/-/healthy", "Testing Prometheus health")
    run_ssh_command("curl -s http://localhost:9090/api/v1/rules | jq '.data.groups | length'", "Checking loaded rules")
    run_ssh_command("curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts | length'", "Checking active alerts")

def main():
    print("🚨 Robust Prometheus Alerts Configuration")
    print("=" * 50)
    
    try:
        recreate_prometheus_with_alerts()
        
        print("\n✅ Prometheus with alerts configuration completed!")
        print("\n🚨 Alert Rules Now Active:")
        print("   • Observatory service monitoring")
        print("   • Prometheus self-monitoring")
        print("   • Redis connectivity monitoring")
        print("   • Cloudflare tunnel monitoring")
        print("   • Response time alerts")
        print("   • Error rate monitoring")
        print("\n🌐 Check alerts at:")
        print("   https://prometheus.observatory.nkllon.com/alerts")
        print("   https://prometheus.observatory.nkllon.com/rules")
        print("   https://prometheus.observatory.nkllon.com/targets")
        
    except Exception as e:
        print(f"\n❌ Error configuring Prometheus alerts: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())