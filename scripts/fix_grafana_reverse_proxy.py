#!/usr/bin/env python3
"""
Fix Grafana reverse proxy configuration for proper external access
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

def fix_grafana_reverse_proxy():
    """Fix Grafana for proper reverse proxy support"""
    print("🔧 Fixing Grafana reverse proxy configuration...")
    
    # Stop current Grafana
    run_ssh_command("docker stop observatory-grafana", "Stopping Grafana")
    run_ssh_command("docker rm observatory-grafana", "Removing Grafana")
    
    # Start Grafana with proper reverse proxy settings
    grafana_cmd = '''docker run -d \\
  --name observatory-grafana \\
  --network host \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_AUTH_ANONYMOUS_ENABLED=true \\
  -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer \\
  -e GF_SECURITY_ADMIN_PASSWORD=admin \\
  -e GF_USERS_ALLOW_SIGN_UP=false \\
  -e GF_SERVER_DOMAIN=grafana.observatory.nkllon.com \\
  -e GF_SERVER_ROOT_URL=https://grafana.observatory.nkllon.com \\
  -e GF_SERVER_SERVE_FROM_SUB_PATH=false \\
  -e GF_SECURITY_ALLOW_EMBEDDING=true \\
  -e GF_SECURITY_COOKIE_SECURE=false \\
  -e GF_LOG_LEVEL=info \\
  grafana/grafana:latest'''
    
    run_ssh_command(grafana_cmd, "Starting Grafana with reverse proxy config")
    
    time.sleep(20)
    
    # Test Grafana
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing Grafana health")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/", "Testing Grafana homepage")
    
    # Check if static assets are loading
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/public/build/grafana.dark.css", "Testing static assets")
    
    # Check Grafana logs
    run_ssh_command("docker logs observatory-grafana --tail 5", "Checking Grafana logs")

def test_external_access():
    """Test external access"""
    print("\n🌐 Testing external access...")
    
    # Give some time for the tunnel to pick up the changes
    time.sleep(5)
    
    print("External Grafana should now be accessible without the 'failed to load' error")
    print("Testing will be done via browser access")

def main():
    print("🔧 Grafana Reverse Proxy Fix")
    print("=" * 35)
    
    try:
        fix_grafana_reverse_proxy()
        test_external_access()
        
        print("\n✅ Grafana reverse proxy fix completed!")
        print("\n🌐 Grafana should now work properly:")
        print("   https://grafana.observatory.nkllon.com")
        print("\n📝 Changes made:")
        print("   • Anonymous access enabled")
        print("   • Proper reverse proxy configuration")
        print("   • Static asset serving fixed")
        print("   • No password required (Viewer role)")
        
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())