#!/usr/bin/env python3
"""
Fix Grafana to properly enable anonymous access without password
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

def fix_grafana_anonymous():
    """Fix Grafana for proper anonymous access"""
    print("🔧 Fixing Grafana for anonymous access...")
    
    # Stop current Grafana
    run_ssh_command("docker stop observatory-grafana", "Stopping Grafana")
    run_ssh_command("docker rm observatory-grafana", "Removing Grafana")
    
    # Create proper Grafana configuration file
    grafana_config = '''
# Create Grafana config directory
mkdir -p /tmp/grafana-config

# Create custom grafana.ini with anonymous access
cat > /tmp/grafana-config/grafana.ini << 'EOF'
[server]
http_addr = 0.0.0.0
http_port = 3000
domain = grafana.observatory.nkllon.com
root_url = https://grafana.observatory.nkllon.com/
serve_from_sub_path = false

[auth.anonymous]
enabled = true
org_name = Main Org.
org_role = Viewer
hide_version = false

[auth]
disable_login_form = false
disable_signout_menu = false

[security]
admin_user = admin
admin_password = admin
allow_embedding = true
cookie_secure = false

[users]
allow_sign_up = false
allow_org_create = false
auto_assign_org = true
auto_assign_org_role = Viewer
default_theme = dark

[log]
mode = console
level = info
EOF

echo "Grafana config created"
'''
    
    run_ssh_command(grafana_config, "Creating Grafana configuration")
    
    # Start Grafana with proper anonymous configuration
    grafana_start = '''docker run -d \\
  --name observatory-grafana \\
  --network host \\
  -v /tmp/grafana-config/grafana.ini:/etc/grafana/grafana.ini:ro \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_AUTH_ANONYMOUS_ENABLED=true \\
  -e GF_AUTH_ANONYMOUS_ORG_NAME="Main Org." \\
  -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer \\
  -e GF_AUTH_ANONYMOUS_HIDE_VERSION=false \\
  -e GF_AUTH_DISABLE_LOGIN_FORM=false \\
  -e GF_SECURITY_ADMIN_PASSWORD=admin \\
  -e GF_USERS_ALLOW_SIGN_UP=false \\
  -e GF_USERS_AUTO_ASSIGN_ORG=true \\
  -e GF_USERS_AUTO_ASSIGN_ORG_ROLE=Viewer \\
  -e GF_SERVER_DOMAIN=grafana.observatory.nkllon.com \\
  -e GF_SERVER_ROOT_URL=https://grafana.observatory.nkllon.com/ \\
  grafana/grafana:latest'''
    
    run_ssh_command(grafana_start, "Starting Grafana with anonymous access")
    
    time.sleep(20)
    
    # Test Grafana
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing Grafana health")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/", "Testing Grafana homepage")
    
    # Check Grafana logs for any issues
    run_ssh_command("docker logs observatory-grafana --tail 10", "Checking Grafana logs")

def test_anonymous_access():
    """Test that anonymous access is working"""
    print("\n🌐 Testing anonymous access...")
    
    # Test local access
    run_ssh_command("curl -s http://localhost:3000/api/org", "Testing anonymous API access")
    
    # Check if login is bypassed
    run_ssh_command("curl -s -I http://localhost:3000/ | grep -i location", "Checking for redirects")

def main():
    print("🔧 Grafana Anonymous Access Fix")
    print("=" * 35)
    
    try:
        fix_grafana_anonymous()
        test_anonymous_access()
        
        print("\n✅ Grafana anonymous access fix completed!")
        print("\n🌐 Grafana should now be accessible without password:")
        print("   https://grafana.observatory.nkllon.com")
        print("\n📝 Anonymous access should be enabled with Viewer role")
        print("💡 If login is still required, try accessing directly without /login")
        
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())