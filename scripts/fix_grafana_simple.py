#!/usr/bin/env python3
"""
Simple fix for Grafana configuration
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

def fix_grafana_simple():
    """Fix Grafana with simple configuration"""
    print("🔧 Fixing Grafana with simple configuration...")
    
    # Clean up any existing containers
    run_ssh_command("docker stop observatory-grafana 2>/dev/null || true", "Stopping any existing Grafana")
    run_ssh_command("docker rm observatory-grafana 2>/dev/null || true", "Removing any existing Grafana")
    
    # Start Grafana with proper configuration
    grafana_command = '''docker run -d \\
  --name observatory-grafana \\
  --network host \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_SERVER_DOMAIN=grafana.observatory.nkllon.com \\
  -e GF_SERVER_ROOT_URL=https://grafana.observatory.nkllon.com/ \\
  -e GF_AUTH_ANONYMOUS_ENABLED=true \\
  -e GF_AUTH_ANONYMOUS_ORG_NAME="Main Org" \\
  -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer \\
  -e GF_SECURITY_ADMIN_PASSWORD=admin \\
  -e GF_USERS_ALLOW_SIGN_UP=false \\
  grafana/grafana:latest'''
    
    run_ssh_command(grafana_command, "Starting Grafana with proper configuration")
    
    time.sleep(15)
    
    # Test Grafana
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing Grafana health")
    run_ssh_command("docker logs observatory-grafana --tail 10", "Checking Grafana logs")

def check_services():
    """Check all services status"""
    print("\n📊 Checking all services...")
    
    run_ssh_command("curl -s -o /dev/null -w 'Observatory: %{http_code}\\n' http://localhost:8888/health", "Testing Observatory")
    run_ssh_command("curl -s -o /dev/null -w 'Prometheus: %{http_code}\\n' http://localhost:9090/-/healthy", "Testing Prometheus")
    run_ssh_command("curl -s -o /dev/null -w 'Grafana: %{http_code}\\n' http://localhost:3000/api/health", "Testing Grafana")
    
    run_ssh_command("docker ps | grep observatory", "Checking containers")

def main():
    print("🔧 Simple Grafana Fix")
    print("=" * 30)
    
    try:
        fix_grafana_simple()
        check_services()
        
        print("\n✅ Grafana fix completed!")
        print("\n🌐 External URLs:")
        print("   Observatory: https://observatory.nkllon.com")
        print("   Prometheus: https://prometheus.observatory.nkllon.com")
        print("   Grafana: https://grafana.observatory.nkllon.com")
        print("\n📝 Grafana should now have anonymous access enabled")
        
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())