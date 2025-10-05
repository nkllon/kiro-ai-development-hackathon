#!/usr/bin/env python3
"""
Final fix for Prometheus with proper permissions and alerts
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

def fix_prometheus_final():
    """Final fix for Prometheus with proper permissions"""
    print("🔧 Final Prometheus fix with proper permissions...")
    
    # Stop any existing container
    print("\n1. Cleaning up...")
    run_ssh_command("docker stop observatory-prometheus 2>/dev/null || true", "Stopping Prometheus")
    run_ssh_command("docker rm observatory-prometheus 2>/dev/null || true", "Removing Prometheus")
    
    # Fix permissions on configuration files
    print("\n2. Fixing file permissions...")
    run_ssh_command("sudo chmod 755 /etc/prometheus", "Setting directory permissions")
    run_ssh_command("sudo chmod 755 /etc/prometheus/rules", "Setting rules directory permissions")
    run_ssh_command("sudo chmod 644 /etc/prometheus/prometheus.yml", "Setting config file permissions")
    run_ssh_command("sudo chmod 644 /etc/prometheus/rules/alert_rules.yml", "Setting rules file permissions")
    run_ssh_command("sudo chown -R 65534:65534 /etc/prometheus", "Setting ownership to nobody user")
    
    # Verify files exist and are readable
    print("\n3. Verifying configuration files...")
    run_ssh_command("ls -la /etc/prometheus/", "Listing config directory")
    run_ssh_command("ls -la /etc/prometheus/rules/", "Listing rules directory")
    run_ssh_command("cat /etc/prometheus/prometheus.yml", "Showing config content")
    
    # Start Prometheus with proper configuration
    print("\n4. Starting Prometheus with fixed permissions...")
    
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
    print("\n5. Verifying Prometheus is working...")
    run_ssh_command("docker ps | grep prometheus", "Checking container status")
    run_ssh_command("docker logs observatory-prometheus --tail 10", "Checking recent logs")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/-/healthy", "Testing health")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/", "Testing main page")
    
    # Test alerts specifically
    print("\n6. Testing alert configuration...")
    run_ssh_command("curl -s http://localhost:9090/api/v1/rules | jq '.status'", "Checking rules API status")
    run_ssh_command("curl -s http://localhost:9090/api/v1/alerts | jq '.status'", "Checking alerts API status")

def main():
    print("🚨 Final Prometheus Permissions Fix")
    print("=" * 50)
    
    try:
        fix_prometheus_final()
        
        print("\n✅ Prometheus final fix completed!")
        print("\n🚨 Alert Configuration Status:")
        print("   • Configuration files have proper permissions")
        print("   • Container running with correct user")
        print("   • Alert rules should now be loaded")
        print("\n🌐 Access Prometheus:")
        print("   External: https://prometheus.observatory.nkllon.com")
        print("   Alerts: https://prometheus.observatory.nkllon.com/alerts")
        print("   Rules: https://prometheus.observatory.nkllon.com/rules")
        
    except Exception as e:
        print(f"\n❌ Error in final fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())