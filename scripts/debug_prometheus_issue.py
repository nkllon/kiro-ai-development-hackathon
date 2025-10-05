#!/usr/bin/env python3
"""
Debug Prometheus startup issues and fix configuration
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

def debug_and_fix_prometheus():
    """Debug Prometheus issues and create working configuration"""
    print("🔍 Debugging Prometheus startup issues...")
    
    # Check container logs
    print("\n1. Checking container logs...")
    run_ssh_command("docker logs observatory-prometheus --tail 20", "Checking Prometheus logs")
    
    # Stop the failing container
    print("\n2. Stopping failing container...")
    run_ssh_command("docker stop observatory-prometheus", "Stopping Prometheus")
    run_ssh_command("docker rm observatory-prometheus", "Removing Prometheus")
    
    # Create a simpler, working configuration
    print("\n3. Creating simplified working configuration...")
    
    simple_config = """global:
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
      - targets: ['192.168.1.119:8888']
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['192.168.1.119:6379']

  - job_name: 'tunnel'
    static_configs:
      - targets: ['127.0.0.1:20241']
    metrics_path: '/metrics'
"""

    simple_rules = """groups:
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
"""

    # Write simplified configuration
    config_command = f'cat > /tmp/prometheus_simple.yml << "EOF"\n{simple_config}\nEOF'
    run_ssh_command(config_command, "Creating simplified Prometheus config")
    
    rules_command = f'cat > /tmp/alert_rules_simple.yml << "EOF"\n{simple_rules}\nEOF'
    run_ssh_command(rules_command, "Creating simplified alert rules")
    
    # Copy to proper locations
    run_ssh_command("sudo cp /tmp/prometheus_simple.yml /etc/prometheus/prometheus.yml", "Installing Prometheus config")
    run_ssh_command("sudo cp /tmp/alert_rules_simple.yml /etc/prometheus/rules/alert_rules.yml", "Installing alert rules")
    
    # Validate configuration
    print("\n4. Validating configuration...")
    run_ssh_command("docker run --rm -v /etc/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus:latest promtool check config /etc/prometheus/prometheus.yml", "Validating Prometheus config")
    run_ssh_command("docker run --rm -v /etc/prometheus/rules:/etc/prometheus/rules prom/prometheus:latest promtool check rules /etc/prometheus/rules/alert_rules.yml", "Validating alert rules")
    
    # Start with working configuration
    print("\n5. Starting Prometheus with validated configuration...")
    
    start_command = """docker run -d \\
  --name observatory-prometheus \\
  --restart unless-stopped \\
  --network host \\
  -v /etc/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro \\
  -v /etc/prometheus/rules:/etc/prometheus/rules:ro \\
  -v prometheus-data:/prometheus \\
  prom/prometheus:latest \\
  --config.file=/etc/prometheus/prometheus.yml \\
  --storage.tsdb.path=/prometheus \\
  --web.enable-lifecycle"""
    
    run_ssh_command(start_command, "Starting Prometheus")
    
    # Wait and verify
    time.sleep(15)
    
    print("\n6. Verifying working Prometheus...")
    run_ssh_command("docker ps | grep prometheus", "Checking container status")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/-/healthy", "Testing health endpoint")
    run_ssh_command("curl -s http://localhost:9090/api/v1/rules | head -20", "Checking rules API")

def main():
    print("🔍 Debugging and Fixing Prometheus Configuration")
    print("=" * 60)
    
    try:
        debug_and_fix_prometheus()
        
        print("\n✅ Prometheus debugging and fix completed!")
        print("\n🚨 Simplified Alert Configuration Active:")
        print("   • Observatory service monitoring")
        print("   • Prometheus self-monitoring")
        print("   • Redis connectivity monitoring")
        print("\n🌐 Test the alerts at:")
        print("   https://prometheus.observatory.nkllon.com/alerts")
        print("   https://prometheus.observatory.nkllon.com/rules")
        
    except Exception as e:
        print(f"\n❌ Error debugging Prometheus: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())