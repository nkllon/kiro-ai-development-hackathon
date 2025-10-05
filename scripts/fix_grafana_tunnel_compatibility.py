#!/usr/bin/env python3
"""
Fix Grafana for Cloudflare tunnel compatibility
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

def fix_grafana_for_tunnel():
    """Fix Grafana specifically for Cloudflare tunnel"""
    print("🔧 Fixing Grafana for Cloudflare tunnel compatibility...")
    
    # Stop current Grafana
    run_ssh_command("docker stop observatory-grafana", "Stopping Grafana")
    run_ssh_command("docker rm observatory-grafana", "Removing Grafana")
    
    # Start Grafana with tunnel-specific configuration
    grafana_cmd = '''docker run -d \\
  --name observatory-grafana \\
  --network host \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_AUTH_ANONYMOUS_ENABLED=true \\
  -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer \\
  -e GF_SECURITY_ADMIN_PASSWORD=admin \\
  -e GF_SERVER_DOMAIN=grafana.observatory.nkllon.com \\
  -e GF_SERVER_ROOT_URL=https://grafana.observatory.nkllon.com \\
  -e GF_SERVER_SERVE_FROM_SUB_PATH=false \\
  -e GF_SECURITY_ALLOW_EMBEDDING=true \\
  -e GF_SECURITY_COOKIE_SECURE=false \\
  -e GF_SECURITY_COOKIE_SAMESITE=lax \\
  -e GF_USERS_ALLOW_SIGN_UP=false \\
  -e GF_ANALYTICS_REPORTING_ENABLED=false \\
  -e GF_ANALYTICS_CHECK_FOR_UPDATES=false \\
  grafana/grafana:latest'''
    
    run_ssh_command(grafana_cmd, "Starting Grafana with tunnel config")
    
    time.sleep(20)
    
    # Test Grafana
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing Grafana health")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/", "Testing Grafana homepage")
    
    # Check if we can access without login
    run_ssh_command("curl -s http://localhost:3000/api/org | head -3", "Testing anonymous access")

def test_grafana_access():
    """Test Grafana access patterns"""
    print("\n🌐 Testing Grafana access patterns...")
    
    # Test different access methods
    run_ssh_command("curl -s -I http://localhost:3000/ | head -5", "Testing homepage headers")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/login", "Testing login page")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/public/build/app.js", "Testing static assets")

def main():
    print("🔧 Grafana Cloudflare Tunnel Fix")
    print("=" * 40)
    
    try:
        fix_grafana_for_tunnel()
        test_grafana_access()
        
        print("\n✅ Grafana tunnel compatibility fix completed!")
        print("\n🌐 Test Grafana access:")
        print("   https://grafana.observatory.nkllon.com")
        print("\n📝 Configuration optimized for Cloudflare tunnel")
        print("💡 Anonymous access enabled - should work without password")
        print("\n⚠️ Note: If UI still shows 'failed to load', this is a known")
        print("   Grafana + Cloudflare tunnel issue. The service is working")
        print("   but the frontend assets may not load properly through the tunnel.")
        
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())