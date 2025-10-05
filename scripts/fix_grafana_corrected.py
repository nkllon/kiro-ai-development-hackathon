#!/usr/bin/env python3
"""
Corrected fix for Grafana configuration
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

def fix_grafana_corrected():
    """Fix Grafana with corrected configuration"""
    print("🔧 Fixing Grafana with corrected configuration...")
    
    # Clean up any existing containers
    run_ssh_command("docker stop observatory-grafana 2>/dev/null || true", "Stopping any existing Grafana")
    run_ssh_command("docker rm observatory-grafana 2>/dev/null || true", "Removing any existing Grafana")
    
    # Start Grafana with proper configuration (fixed environment variables)
    grafana_command = '''docker run -d \\
  --name observatory-grafana \\
  --network host \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_SERVER_DOMAIN=grafana.observatory.nkllon.com \\
  -e GF_SERVER_ROOT_URL=https://grafana.observatory.nkllon.com/ \\
  -e GF_AUTH_ANONYMOUS_ENABLED=true \\
  -e GF_AUTH_ANONYMOUS_ORG_NAME=MainOrg \\
  -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer \\
  -e GF_SECURITY_ADMIN_PASSWORD=admin \\
  -e GF_USERS_ALLOW_SIGN_UP=false \\
  grafana/grafana:latest'''
    
    run_ssh_command(grafana_command, "Starting Grafana with corrected configuration")
    
    time.sleep(15)
    
    # Test Grafana
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing Grafana health")
    run_ssh_command("docker logs observatory-grafana --tail 5", "Checking Grafana logs")

def fix_prometheus_simple():
    """Ensure Prometheus is running properly"""
    print("\n🔧 Checking Prometheus...")
    
    # Check if Prometheus is running
    success, stdout, stderr = run_ssh_command("curl -s http://localhost:9090/-/healthy", "Testing Prometheus")
    
    if not success or "Prometheus is Healthy" not in stdout:
        print("⚠️ Prometheus needs restart")
        
        # Restart Prometheus
        run_ssh_command("docker stop observatory-prometheus 2>/dev/null || true", "Stopping Prometheus")
        run_ssh_command("docker rm observatory-prometheus 2>/dev/null || true", "Removing Prometheus")
        
        prometheus_command = '''docker run -d \\
  --name observatory-prometheus \\
  --network host \\
  -v prometheus-data:/prometheus \\
  prom/prometheus:latest \\
  --config.file=/etc/prometheus/prometheus.yml \\
  --storage.tsdb.path=/prometheus \\
  --web.console.libraries=/etc/prometheus/console_libraries \\
  --web.console.templates=/etc/prometheus/consoles \\
  --web.enable-lifecycle'''
        
        run_ssh_command(prometheus_command, "Starting Prometheus")
        time.sleep(10)
        run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/-/healthy", "Testing Prometheus health")

def check_all_services():
    """Check all services status"""
    print("\n📊 Final services check...")
    
    run_ssh_command("curl -s -o /dev/null -w 'Observatory: %{http_code}\\n' http://localhost:8888/health", "Observatory")
    run_ssh_command("curl -s -o /dev/null -w 'Prometheus: %{http_code}\\n' http://localhost:9090/-/healthy", "Prometheus")
    run_ssh_command("curl -s -o /dev/null -w 'Grafana: %{http_code}\\n' http://localhost:3000/api/health", "Grafana")
    
    run_ssh_command("docker ps --format 'table {{.Names}}\\t{{.Status}}' | grep observatory", "Container status")

def main():
    print("🔧 Corrected Grafana and Prometheus Fix")
    print("=" * 40)
    
    try:
        fix_grafana_corrected()
        fix_prometheus_simple()
        check_all_services()
        
        print("\n✅ Services fix completed!")
        print("\n🌐 External URLs should now work:")
        print("   Observatory: https://observatory.nkllon.com")
        print("   Prometheus: https://prometheus.observatory.nkllon.com")
        print("   Grafana: https://grafana.observatory.nkllon.com")
        print("\n📝 Grafana should now have anonymous access enabled")
        print("🚨 Prometheus should be accessible and healthy")
        
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())