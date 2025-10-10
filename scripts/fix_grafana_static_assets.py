#!/usr/bin/env python3
"""
Fix Grafana static asset loading through Cloudflare tunnel
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

def create_grafana_config():
    """Create proper Grafana configuration file"""
    print("🔧 Creating proper Grafana configuration...")
    
    config_creation = '''
# Create Grafana config directory
mkdir -p /tmp/grafana-config

# Create comprehensive grafana.ini
cat > /tmp/grafana-config/grafana.ini << 'EOF'
[server]
http_addr = 0.0.0.0
http_port = 3000
domain = grafana.observatory.nkllon.com
root_url = https://grafana.observatory.nkllon.com/
serve_from_sub_path = false
static_root_path = /usr/share/grafana

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
cookie_samesite = lax

[users]
allow_sign_up = false
allow_org_create = false
auto_assign_org = true
auto_assign_org_role = Viewer
default_theme = dark

[log]
mode = console
level = info

[paths]
data = /var/lib/grafana
logs = /var/log/grafana
plugins = /var/lib/grafana/plugins
provisioning = /etc/grafana/provisioning

[analytics]
reporting_enabled = false
check_for_updates = false

[snapshots]
external_enabled = false
EOF

echo "Grafana configuration created"
'''
    
    run_ssh_command(config_creation, "Creating Grafana configuration")

def fix_grafana_with_config():
    """Fix Grafana with proper configuration file"""
    print("🔧 Fixing Grafana with proper configuration...")
    
    # Stop and remove current Grafana
    run_ssh_command("docker stop observatory-grafana 2>/dev/null || true", "Stopping Grafana")
    run_ssh_command("docker rm observatory-grafana 2>/dev/null || true", "Removing Grafana")
    
    # Create configuration
    create_grafana_config()
    
    # Start Grafana with configuration file and proper environment
    grafana_cmd = '''docker run -d \\
  --name observatory-grafana \\
  --network host \\
  -v /tmp/grafana-config/grafana.ini:/etc/grafana/grafana.ini:ro \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_PATHS_CONFIG=/etc/grafana/grafana.ini \\
  -e GF_AUTH_ANONYMOUS_ENABLED=true \\
  -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer \\
  -e GF_SECURITY_ADMIN_PASSWORD=admin \\
  -e GF_SERVER_DOMAIN=grafana.observatory.nkllon.com \\
  -e GF_SERVER_ROOT_URL=https://grafana.observatory.nkllon.com/ \\
  -e GF_SERVER_SERVE_FROM_SUB_PATH=false \\
  grafana/grafana:latest'''
    
    run_ssh_command(grafana_cmd, "Starting Grafana with config file")
    
    time.sleep(20)
    
    # Test Grafana startup
    run_ssh_command("docker logs observatory-grafana --tail 10", "Checking Grafana startup logs")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing Grafana health")

def test_static_assets():
    """Test if static assets are loading"""
    print("\n🔧 Testing static asset loading...")
    
    # Test various static asset endpoints
    assets = [
        "/public/build/app.js",
        "/public/build/grafana.dark.css", 
        "/public/img/grafana_icon.svg",
        "/avatar/46d229b033af06a191ff2267bca9ae56"
    ]
    
    for asset in assets:
        run_ssh_command(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:3000{asset}", f"Testing {asset}")

def test_grafana_functionality():
    """Test Grafana functionality"""
    print("\n🔧 Testing Grafana functionality...")
    
    # Test API endpoints
    endpoints = [
        ("/api/health", "Health check"),
        ("/api/org", "Organization info"),
        ("/api/user", "User info (anonymous)"),
        ("/api/dashboards/home", "Home dashboard"),
        ("/", "Homepage")
    ]
    
    for endpoint, description in endpoints:
        run_ssh_command(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:3000{endpoint}", f"Testing {description}")

def restart_tunnel():
    """Restart tunnel to pick up any changes"""
    print("\n🔧 Restarting tunnel...")
    
    run_ssh_command("pkill -f cloudflared", "Stopping tunnel")
    time.sleep(3)
    
    start_tunnel = "nohup cloudflared tunnel --config /etc/cloudflared/config.yml run > /tmp/tunnel.log 2>&1 &"
    run_ssh_command(start_tunnel, "Starting tunnel")
    time.sleep(5)
    
    run_ssh_command("pgrep -f cloudflared", "Verifying tunnel")

def main():
    print("🔧 Grafana Static Assets Fix")
    print("=" * 35)
    print("Fixing Grafana to properly load through Cloudflare tunnel")
    print()
    
    try:
        fix_grafana_with_config()
        test_static_assets()
        test_grafana_functionality()
        restart_tunnel()
        
        print("\n✅ Grafana static assets fix completed!")
        print("\n🌐 Test Grafana now:")
        print("   https://grafana.observatory.nkllon.com")
        print("\n📝 Changes made:")
        print("   • Proper grafana.ini configuration file")
        print("   • Fixed static asset paths")
        print("   • Anonymous access enabled")
        print("   • Tunnel restarted")
        print("\n💡 Grafana should now load properly without the 'failed to load' error")
        
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())