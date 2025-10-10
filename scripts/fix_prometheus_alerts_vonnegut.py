#!/usr/bin/env python3
"""
Fix Prometheus alerts configuration on Vonnegut
Add proper alerting rules for Observatory monitoring
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

def create_alert_rules():
    """Create comprehensive alert rules for Observatory monitoring"""
    print("🚨 Creating Prometheus alert rules...")
    
    # Create alert rules configuration
    alert_rules = """groups:
  - name: observatory_alerts
    rules:
      # Service availability alerts
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

      # Performance alerts
      - alert: HighCPUUsage
        expr: (100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes"

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for more than 5 minutes"

      - alert: DiskSpaceLow
        expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk space is running low"
          description: "Disk usage is above 90% for more than 5 minutes"

      # Observatory specific alerts
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

      # Redis specific alerts
      - alert: RedisHighMemoryUsage
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage is high"
          description: "Redis memory usage is above 90%"

      - alert: RedisConnectionsHigh
        expr: redis_connected_clients > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis has too many connections"
          description: "Redis has more than 100 connected clients"

      # Container alerts
      - alert: ContainerDown
        expr: up{job=~".*container.*"} == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Container service is down"
          description: "Container {{ $labels.job }} has been down for more than 2 minutes"

      - alert: ContainerHighCPU
        expr: rate(container_cpu_usage_seconds_total[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Container CPU usage is high"
          description: "Container {{ $labels.name }} CPU usage is above 80%"

      - alert: ContainerHighMemory
        expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Container memory usage is high"
          description: "Container {{ $labels.name }} memory usage is above 90%"

  - name: infrastructure_alerts
    rules:
      # Network connectivity alerts
      - alert: TunnelDown
        expr: up{job="tunnel"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Cloudflare tunnel is down"
          description: "Cloudflare tunnel has been down for more than 2 minutes"

      # Docker alerts
      - alert: DockerDaemonDown
        expr: up{job="docker"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Docker daemon is down"
          description: "Docker daemon has been down for more than 1 minute"

      # System alerts
      - alert: SystemLoadHigh
        expr: node_load1 > 4
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "System load is high"
          description: "1-minute load average is above 4 for more than 5 minutes"

      - alert: TooManyOpenFiles
        expr: node_filefd_allocated / node_filefd_maximum > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Too many open files"
          description: "File descriptor usage is above 80%"
"""

    # Write alert rules to temporary file
    rules_command = f'cat > /tmp/alert_rules.yml << "EOF"\n{alert_rules}\nEOF'
    run_ssh_command(rules_command, "Creating alert rules file")
    
    # Create prometheus config directory if it doesn't exist
    run_ssh_command("sudo mkdir -p /etc/prometheus/rules", "Creating rules directory")
    
    # Move alert rules to proper location
    run_ssh_command("sudo mv /tmp/alert_rules.yml /etc/prometheus/rules/", "Moving alert rules")
    run_ssh_command("sudo chown root:root /etc/prometheus/rules/alert_rules.yml", "Setting rules ownership")
    run_ssh_command("sudo chmod 644 /etc/prometheus/rules/alert_rules.yml", "Setting rules permissions")

def update_prometheus_config():
    """Update Prometheus configuration to include alert rules"""
    print("📝 Updating Prometheus configuration...")
    
    prometheus_config = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "/etc/prometheus/rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

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

  - job_name: 'node'
    static_configs:
      - targets: ['192.168.1.119:9100']
    scrape_interval: 15s

  - job_name: 'docker'
    static_configs:
      - targets: ['192.168.1.119:9323']
    scrape_interval: 15s

  - job_name: 'tunnel'
    static_configs:
      - targets: ['127.0.0.1:20241']
    scrape_interval: 30s
    metrics_path: '/metrics'
"""

    # Write Prometheus config
    config_command = f'cat > /tmp/prometheus.yml << "EOF"\n{prometheus_config}\nEOF'
    run_ssh_command(config_command, "Creating Prometheus configuration")
    
    # Update the container's prometheus config
    run_ssh_command("docker cp /tmp/prometheus.yml observatory-prometheus:/etc/prometheus/prometheus.yml", "Updating container config")
    run_ssh_command("docker cp /etc/prometheus/rules/alert_rules.yml observatory-prometheus:/etc/prometheus/rules/", "Copying alert rules to container")

def restart_prometheus():
    """Restart Prometheus to load new configuration"""
    print("🔄 Restarting Prometheus with new configuration...")
    
    # Restart the Prometheus container
    run_ssh_command("docker restart observatory-prometheus", "Restarting Prometheus container")
    
    # Wait for restart
    time.sleep(10)
    
    # Check if Prometheus is healthy
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/-/healthy", "Testing Prometheus health")
    
    # Check if rules are loaded
    run_ssh_command("curl -s http://localhost:9090/api/v1/rules | jq '.data.groups | length'", "Checking loaded rules")

def main():
    print("🚨 Configuring Prometheus Alerts for Observatory")
    print("=" * 60)
    
    try:
        # Create alert rules
        create_alert_rules()
        
        # Update Prometheus configuration
        update_prometheus_config()
        
        # Restart Prometheus
        restart_prometheus()
        
        print("\n✅ Prometheus alerts configuration completed!")
        print("\n🚨 Alert Rules Configured:")
        print("   • Service availability (Observatory, Prometheus, Redis)")
        print("   • Performance monitoring (CPU, Memory, Disk)")
        print("   • Observatory-specific alerts (Response time, Error rate)")
        print("   • Redis monitoring (Memory, Connections)")
        print("   • Container monitoring (Docker containers)")
        print("   • Infrastructure alerts (Tunnel, Docker daemon)")
        print("\n🌐 Check alerts at:")
        print("   https://prometheus.observatory.nkllon.com/alerts")
        print("   https://prometheus.observatory.nkllon.com/rules")
        
    except Exception as e:
        print(f"\n❌ Error configuring alerts: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())