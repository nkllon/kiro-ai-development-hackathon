#!/usr/bin/env python3
"""
Fix alert rules syntax errors in Prometheus
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

def fix_alert_rules_syntax():
    """Fix the syntax errors in alert rules"""
    print("🔧 Fixing alert rules syntax...")
    
    # Create corrected alert rules with proper syntax
    corrected_rules = """groups:
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
"""

    # Stop container
    print("\n1. Stopping Prometheus to update rules...")
    run_ssh_command("docker stop observatory-prometheus", "Stopping Prometheus")
    run_ssh_command("docker rm observatory-prometheus", "Removing container")
    
    # Write corrected rules
    print("\n2. Creating corrected alert rules...")
    rules_command = f'cat > /tmp/alert_rules_corrected.yml << "EOF"\n{corrected_rules}\nEOF'
    run_ssh_command(rules_command, "Creating corrected alert rules")
    
    # Install corrected rules
    run_ssh_command("sudo cp /tmp/alert_rules_corrected.yml /etc/prometheus/rules/alert_rules.yml", "Installing corrected rules")
    run_ssh_command("sudo chown 65534:65534 /etc/prometheus/rules/alert_rules.yml", "Setting ownership")
    run_ssh_command("sudo chmod 644 /etc/prometheus/rules/alert_rules.yml", "Setting permissions")
    
    # Verify the corrected rules
    print("\n3. Verifying corrected rules syntax...")
    run_ssh_command("cat /etc/prometheus/rules/alert_rules.yml", "Showing corrected rules")
    
    # Start Prometheus with corrected rules
    print("\n4. Starting Prometheus with corrected rules...")
    
    start_command = """docker run -d \\
  --name observatory-prometheus \\
  --restart unless-stopped \\
  --network host \\
  --user 65534:65534 \\
  -v /etc/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro \\
  -v /etc/prometheus/rules:/etc/prometheus/rules:ro \\
  -v prometheus-data:/prometheus \\
  prom/prometheus:latest \\
  --config.file=/etc/prometheus/prometheus.yml \\
  --storage.tsdb.path=/prometheus \\
  --web.enable-lifecycle"""
    
    run_ssh_command(start_command, "Starting Prometheus")
    
    # Wait for startup
    time.sleep(15)
    
    # Verify it's working
    print("\n5. Verifying Prometheus with corrected rules...")
    run_ssh_command("docker ps | grep prometheus", "Checking container status")
    run_ssh_command("docker logs observatory-prometheus --tail 5", "Checking recent logs")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/-/healthy", "Testing health")
    
    # Test rules and alerts APIs
    print("\n6. Testing rules and alerts...")
    run_ssh_command("curl -s http://localhost:9090/api/v1/rules | jq '.status'", "Checking rules API")
    run_ssh_command("curl -s http://localhost:9090/api/v1/alerts | jq '.status'", "Checking alerts API")
    run_ssh_command("curl -s http://localhost:9090/api/v1/rules | jq '.data.groups | length'", "Counting rule groups")

def main():
    print("🚨 Fixing Prometheus Alert Rules Syntax")
    print("=" * 50)
    
    try:
        fix_alert_rules_syntax()
        
        print("\n✅ Alert rules syntax fix completed!")
        print("\n🚨 Working Alert Rules:")
        print("   • ObservatoryDown - monitors Observatory service")
        print("   • PrometheusDown - monitors Prometheus service")
        print("   • RedisDown - monitors Redis service")
        print("   • TunnelDown - monitors Cloudflare tunnel")
        print("\n🌐 Check alerts at:")
        print("   https://prometheus.observatory.nkllon.com/alerts")
        print("   https://prometheus.observatory.nkllon.com/rules")
        
    except Exception as e:
        print(f"\n❌ Error fixing alert rules: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())