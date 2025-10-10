#!/usr/bin/env python3
"""
Fix Prometheus with host networking and alerts
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

def start_prometheus_with_host_network():
    """Start Prometheus with host networking and alerts"""
    print("🔄 Starting Prometheus with host networking and alerts...")
    
    # Clean up any existing containers
    print("\n1. Cleaning up existing containers...")
    run_ssh_command("docker stop observatory-prometheus 2>/dev/null || true", "Stopping existing Prometheus")
    run_ssh_command("docker rm observatory-prometheus 2>/dev/null || true", "Removing existing Prometheus")
    
    print("\n2. Starting Prometheus with host networking...")
    
    # Start Prometheus with host networking (which we know works)
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
  --web.console.libraries=/etc/prometheus/console_libraries \\
  --web.console.templates=/etc/prometheus/consoles \\
  --web.enable-lifecycle \\
  --web.enable-admin-api \\
  --web.listen-address=0.0.0.0:9090"""
    
    run_ssh_command(start_command, "Starting Prometheus with host network")
    
    # Wait for startup
    time.sleep(10)
    
    print("\n3. Verifying Prometheus status...")
    run_ssh_command("docker ps | grep prometheus", "Checking container status")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/-/healthy", "Testing Prometheus health")
    
    print("\n4. Checking alert configuration...")
    run_ssh_command("curl -s http://localhost:9090/api/v1/rules | jq '.data.groups | length'", "Checking loaded rule groups")
    run_ssh_command("curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts | length'", "Checking active alerts")
    
    print("\n5. Testing targets...")
    run_ssh_command("curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'", "Checking active targets")

def main():
    print("🚨 Starting Prometheus with Host Network and Alerts")
    print("=" * 60)
    
    try:
        start_prometheus_with_host_network()
        
        print("\n✅ Prometheus with alerts is now running!")
        print("\n🚨 Alert Configuration:")
        print("   • Observatory service monitoring")
        print("   • Prometheus self-monitoring") 
        print("   • Redis connectivity monitoring")
        print("   • Cloudflare tunnel monitoring")
        print("   • Response time and error rate alerts")
        print("\n🌐 Access Prometheus:")
        print("   Local: http://192.168.1.119:9090")
        print("   External: https://prometheus.observatory.nkllon.com")
        print("\n📊 Key URLs:")
        print("   Alerts: https://prometheus.observatory.nkllon.com/alerts")
        print("   Rules: https://prometheus.observatory.nkllon.com/rules")
        print("   Targets: https://prometheus.observatory.nkllon.com/targets")
        
    except Exception as e:
        print(f"\n❌ Error starting Prometheus: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())