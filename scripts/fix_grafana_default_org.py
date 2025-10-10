#!/usr/bin/env python3
"""
Fix Grafana anonymous access using default organization
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

def fix_grafana_with_default_org():
    """Fix Grafana using default Main Org."""
    print("🔧 Fixing Grafana with default organization...")
    
    # Stop and remove current Grafana
    run_ssh_command("docker stop observatory-grafana", "Stopping Grafana")
    run_ssh_command("docker rm observatory-grafana", "Removing Grafana")
    
    # Start Grafana with default organization (Main Org.)
    grafana_cmd = '''docker run -d \\
  --name observatory-grafana \\
  --network host \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_AUTH_ANONYMOUS_ENABLED=true \\
  -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer \\
  -e GF_SECURITY_ADMIN_PASSWORD=admin \\
  -e GF_USERS_ALLOW_SIGN_UP=false \\
  -e GF_SERVER_DOMAIN=grafana.observatory.nkllon.com \\
  -e GF_SERVER_ROOT_URL=https://grafana.observatory.nkllon.com/ \\
  grafana/grafana:latest'''
    
    run_ssh_command(grafana_cmd, "Starting Grafana with default org")
    
    time.sleep(15)
    
    # Test Grafana
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing Grafana health")
    
    # Check logs for any org errors
    run_ssh_command("docker logs observatory-grafana --tail 10 | grep -i org", "Checking for org errors")

def test_anonymous_access():
    """Test anonymous access"""
    print("\n🌐 Testing anonymous access...")
    
    # Test homepage (should redirect to dashboards or show login)
    run_ssh_command("curl -s -I http://localhost:3000/ | head -5", "Testing homepage response")
    
    # Test if we can access without authentication
    run_ssh_command("curl -s http://localhost:3000/api/org | head -3", "Testing org API access")

def main():
    print("🔧 Grafana Default Organization Fix")
    print("=" * 40)
    
    try:
        fix_grafana_with_default_org()
        test_anonymous_access()
        
        print("\n✅ Grafana default org fix completed!")
        print("\n🌐 Test Grafana access:")
        print("   https://grafana.observatory.nkllon.com")
        print("\n📝 Anonymous access should now work with default organization")
        print("💡 If still prompted for login, the anonymous user should have Viewer access")
        
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())