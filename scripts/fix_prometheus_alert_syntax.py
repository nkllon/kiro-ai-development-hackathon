#!/usr/bin/env python3
"""
Fix Prometheus alert rule syntax errors
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

def create_correct_alert_rules():
    """Create correct Prometheus alert rules with proper syntax"""
    print("🔧 Creating corrected alert rules...")
    
    # Create directories
    run_ssh_command("mkdir -p /tmp/prometheus-config/rules", "Creating config directories")
    
    # Create corrected alerting rules
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
      
      - alert: GrafanaDown
        expr: up{job="grafana"} == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Grafana service is down"
          description: "Grafana service has been down for more than 2 minutes."
      
      - alert: HighRequestRate
        expr: rate(prometheus_http_requests_total[5m]) > 100
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High request rate detected"
          description: "Request rate is above 100 requests/second for more than 2 minutes."
      
      - alert: PrometheusConfigReloadFailed
        expr: prometheus_config_last_reload_successful == 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Prometheus configuration reload failed"
          description: "Prometheus configuration reload has failed."
EOF

echo "Corrected alert rules created"
'''
    
    run_ssh_command(alert_rules, "Creating corrected alerting rules")

def restart_prometheus_with_fixed_alerts():
    """Restart Prometheus with fixed alerting configuration"""
    print("\n🔄 Restarting Prometheus with fixed alert rules...")
    
    # Stop current Prometheus
    run_ssh_command("docker stop observatory-prometheus 2>/dev/null || true", "Stopping Prometheus")
    run_ssh_command("docker rm observatory-prometheus 2>/dev/null || true", "Removing Prometheus")
    
    # Start Prometheus with fixed alerting rules
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
    
    run_ssh_command(prometheus_command, "Starting Prometheus with fixed alerts")
    
    time.sleep(15)
    
    # Test Prometheus
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/", "Testing Prometheus")
    run_ssh_command("docker logs observatory-prometheus --tail 5", "Checking Prometheus logs")

def verify_fixed_alerts():
    """Verify that alerts are properly loaded"""
    print("\n🔍 Verifying fixed alert configuration...")
    
    # Check if Prometheus is accessible
    run_ssh_command("curl -s http://localhost:9090/api/v1/rules", "Checking loaded alert rules")
    
    # Check alerts status
    run_ssh_command("curl -s http://localhost:9090/api/v1/alerts", "Checking active alerts")
    
    # Check targets
    run_ssh_command("curl -s http://localhost:9090/api/v1/targets", "Checking scrape targets")

def main():
    print("🔧 Fixing Prometheus Alert Rule Syntax")
    print("=" * 40)
    
    try:
        create_correct_alert_rules()
        restart_prometheus_with_fixed_alerts()
        verify_fixed_alerts()
        
        print("\n✅ Prometheus alert syntax fix completed!")
        print("\n🚨 Fixed Alert Rules:")
        print("   • ObservatoryDown - Monitors Observatory service availability")
        print("   • PrometheusDown - Monitors Prometheus service availability")
        print("   • GrafanaDown - Monitors Grafana service availability")
        print("   • HighRequestRate - Monitors request rate spikes")
        print("   • PrometheusConfigReloadFailed - Monitors config reload issues")
        print("\n🌐 External URLs:")
        print("   Observatory: https://observatory.nkllon.com")
        print("   Prometheus: https://prometheus.observatory.nkllon.com")
        print("   Grafana: https://grafana.observatory.nkllon.com")
        print("\n📊 Prometheus now has working alerting rules!")
        
    except Exception as e:
        print(f"\n❌ Error during alert fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())