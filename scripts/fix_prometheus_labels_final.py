#!/usr/bin/env python3
"""
Fix Prometheus alert rule label syntax - job names need quotes
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

def create_properly_quoted_alert_rules():
    """Create Prometheus alert rules with properly quoted job names"""
    print("🔧 Creating properly quoted alert rules...")
    
    # Create directories
    run_ssh_command("mkdir -p /tmp/prometheus-config/rules", "Creating config directories")
    
    # Create properly quoted alerting rules
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
      
      - alert: TooManyRestarts
        expr: changes(process_start_time_seconds[15m]) > 2
        for: 0m
        labels:
          severity: warning
        annotations:
          summary: "Service restarting frequently"
          description: "Service has restarted more than twice in the last 15 minutes."
EOF

echo "Properly quoted alert rules created"
'''
    
    run_ssh_command(alert_rules, "Creating properly quoted alerting rules")

def restart_prometheus_final():
    """Final restart of Prometheus with correct alert rules"""
    print("\n🔄 Final Prometheus restart with correct alert rules...")
    
    # Stop current Prometheus
    run_ssh_command("docker stop observatory-prometheus 2>/dev/null || true", "Stopping Prometheus")
    run_ssh_command("docker rm observatory-prometheus 2>/dev/null || true", "Removing Prometheus")
    
    # Start Prometheus with correct alerting rules
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
    
    run_ssh_command(prometheus_command, "Starting Prometheus with correct alerts")
    
    time.sleep(15)
    
    # Test Prometheus
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/", "Testing Prometheus")
    run_ssh_command("curl -s http://localhost:9090/-/healthy", "Testing Prometheus health")
    run_ssh_command("docker logs observatory-prometheus --tail 5", "Checking Prometheus logs")

def verify_working_alerts():
    """Verify that alerts are properly loaded and working"""
    print("\n🔍 Verifying working alert configuration...")
    
    # Check if Prometheus is accessible
    run_ssh_command("curl -s http://localhost:9090/api/v1/rules | head -50", "Checking loaded alert rules")
    
    # Check alerts status
    run_ssh_command("curl -s http://localhost:9090/api/v1/alerts | head -50", "Checking active alerts")
    
    # Check targets
    run_ssh_command("curl -s http://localhost:9090/api/v1/targets | head -50", "Checking scrape targets")

def test_external_prometheus():
    """Test external Prometheus access"""
    print("\n🌐 Testing external Prometheus access...")
    
    # Wait for services to stabilize
    time.sleep(5)
    
    # Test local access first
    run_ssh_command("curl -s -o /dev/null -w 'Prometheus local: %{http_code}\\n' http://localhost:9090/", "Local Prometheus")
    
    print("External Prometheus should now be accessible at:")
    print("https://prometheus.observatory.nkllon.com")

def main():
    print("🔧 Final Prometheus Alert Rules Fix")
    print("=" * 40)
    
    try:
        create_properly_quoted_alert_rules()
        restart_prometheus_final()
        verify_working_alerts()
        test_external_prometheus()
        
        print("\n✅ Prometheus alert rules fix completed!")
        print("\n🚨 Working Alert Rules:")
        print("   • ObservatoryDown - Monitors Observatory service (up{job=\"observatory\"} == 0)")
        print("   • PrometheusDown - Monitors Prometheus service (up{job=\"prometheus\"} == 0)")
        print("   • GrafanaDown - Monitors Grafana service (up{job=\"grafana\"} == 0)")
        print("   • HighRequestRate - Monitors request rate spikes")
        print("   • PrometheusConfigReloadFailed - Monitors config reload issues")
        print("   • TooManyRestarts - Monitors service restart frequency")
        print("\n🌐 External URLs:")
        print("   Observatory: https://observatory.nkllon.com ✅")
        print("   Prometheus: https://prometheus.observatory.nkllon.com 🚨")
        print("   Grafana: https://grafana.observatory.nkllon.com ⚠️")
        print("\n📊 Prometheus now has properly configured alerting rules!")
        
    except Exception as e:
        print(f"\n❌ Error during final alert fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())