#!/usr/bin/env python3
"""
Simple fix for Grafana anonymous access without problematic quotes
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
    """Fix Grafana with simple anonymous configuration"""
    print("🔧 Fixing Grafana with simple anonymous access...")
    
    # Clean up any existing containers
    run_ssh_command("docker stop observatory-grafana 2>/dev/null || true", "Stopping Grafana")
    run_ssh_command("docker rm observatory-grafana 2>/dev/null || true", "Removing Grafana")
    
    # Start Grafana with corrected environment variables (no problematic quotes)
    grafana_cmd = '''docker run -d \\
  --name observatory-grafana \\
  --network host \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_AUTH_ANONYMOUS_ENABLED=true \\
  -e GF_AUTH_ANONYMOUS_ORG_NAME=MainOrg \\
  -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer \\
  -e GF_AUTH_ANONYMOUS_HIDE_VERSION=false \\
  -e GF_SECURITY_ADMIN_PASSWORD=admin \\
  -e GF_USERS_ALLOW_SIGN_UP=false \\
  -e GF_USERS_AUTO_ASSIGN_ORG=true \\
  -e GF_USERS_AUTO_ASSIGN_ORG_ROLE=Viewer \\
  -e GF_SERVER_DOMAIN=grafana.observatory.nkllon.com \\
  -e GF_SERVER_ROOT_URL=https://grafana.observatory.nkllon.com/ \\
  grafana/grafana:latest'''
    
    run_ssh_command(grafana_cmd, "Starting Grafana with anonymous access")
    
    time.sleep(15)
    
    # Test Grafana
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing Grafana health")
    run_ssh_command("docker logs observatory-grafana --tail 5", "Checking Grafana startup logs")

def test_grafana_access():
    """Test Grafana access"""
    print("\n🌐 Testing Grafana access...")
    
    # Test different endpoints
    endpoints = [
        ("/api/health", "Health endpoint"),
        ("/", "Homepage"),
        ("/api/org", "Organization API (should work with anonymous)")
    ]
    
    for endpoint, description in endpoints:
        run_ssh_command(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:3000{endpoint}", f"Testing {description}")

def main():
    print("🔧 Simple Grafana Anonymous Fix")
    print("=" * 35)
    
    try:
        fix_grafana_simple()
        test_grafana_access()
        
        print("\n✅ Grafana anonymous fix completed!")
        print("\n🌐 Grafana should now be accessible:")
        print("   https://grafana.observatory.nkllon.com")
        print("\n📝 Anonymous access enabled - no password required")
        print("💡 You should be able to access dashboards directly")
        
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())