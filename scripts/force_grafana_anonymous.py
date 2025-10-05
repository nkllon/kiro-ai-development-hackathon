#!/usr/bin/env python3
"""
Force Grafana anonymous access - disable login completely
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

def force_anonymous_access():
    """Force Grafana to use anonymous access without login"""
    print("🔧 Forcing Grafana anonymous access...")
    
    # Stop current Grafana
    run_ssh_command("docker stop observatory-grafana", "Stopping Grafana")
    run_ssh_command("docker rm observatory-grafana", "Removing Grafana")
    
    # Create Grafana config that forces anonymous access
    config_cmd = '''
mkdir -p /tmp/grafana-force-anon

cat > /tmp/grafana-force-anon/grafana.ini << 'EOF'
[server]
http_addr = 0.0.0.0
http_port = 3000
domain = grafana.observatory.nkllon.com
root_url = https://grafana.observatory.nkllon.com
serve_from_sub_path = false

[auth.anonymous]
enabled = true
org_role = Admin
hide_version = false

[auth]
disable_login_form = true
disable_signout_menu = true

[security]
admin_user = admin
admin_password = admin
allow_embedding = true
cookie_secure = false

[users]
allow_sign_up = false
allow_org_create = false
auto_assign_org = true
auto_assign_org_role = Admin
default_theme = dark

[log]
mode = console
level = info
EOF
'''
    
    run_ssh_command(config_cmd, "Creating force anonymous config")
    
    # Start Grafana with forced anonymous access
    grafana_cmd = '''docker run -d \\
  --name observatory-grafana \\
  --network host \\
  -v /tmp/grafana-force-anon/grafana.ini:/etc/grafana/grafana.ini:ro \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_AUTH_ANONYMOUS_ENABLED=true \\
  -e GF_AUTH_ANONYMOUS_ORG_ROLE=Admin \\
  -e GF_AUTH_DISABLE_LOGIN_FORM=true \\
  -e GF_AUTH_DISABLE_SIGNOUT_MENU=true \\
  -e GF_SECURITY_ADMIN_PASSWORD=admin \\
  -e GF_USERS_ALLOW_SIGN_UP=false \\
  -e GF_SERVER_DOMAIN=grafana.observatory.nkllon.com \\
  -e GF_SERVER_ROOT_URL=https://grafana.observatory.nkllon.com \\
  grafana/grafana:latest'''
    
    run_ssh_command(grafana_cmd, "Starting Grafana with forced anonymous access")
    
    time.sleep(20)
    
    # Test Grafana
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing Grafana health")
    run_ssh_command("curl -s -I http://localhost:3000/ | head -3", "Testing homepage response")
    
    # Check logs for anonymous access
    run_ssh_command("docker logs observatory-grafana --tail 10 | grep -i anon", "Checking anonymous logs")

def test_forced_access():
    """Test that login is completely bypassed"""
    print("\n🌐 Testing forced anonymous access...")
    
    # Test that we get content without login
    run_ssh_command("curl -s http://localhost:3000/api/user | head -3", "Testing user API (should work anonymously)")
    run_ssh_command("curl -s http://localhost:3000/api/dashboards/home | head -3", "Testing dashboard API")

def main():
    print("🔧 Force Grafana Anonymous Access")
    print("=" * 40)
    print("This will completely disable login and force anonymous Admin access")
    
    try:
        force_anonymous_access()
        test_forced_access()
        
        print("\n✅ Grafana forced anonymous access completed!")
        print("\n🌐 Grafana should now be accessible WITHOUT any login:")
        print("   https://grafana.observatory.nkllon.com")
        print("\n📝 Changes made:")
        print("   • Login form completely disabled")
        print("   • Anonymous access with Admin role")
        print("   • No password required anywhere")
        print("   • Signout menu disabled")
        
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())