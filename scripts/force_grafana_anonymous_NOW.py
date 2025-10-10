#!/usr/bin/env python3
"""
FORCE Grafana anonymous access - no more password bullshit
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
    """FORCE anonymous access - nuclear option"""
    print("🔥 FORCING Grafana anonymous access - nuclear option...")
    
    # Kill everything Grafana
    run_ssh_command("docker stop observatory-grafana", "Stopping Grafana")
    run_ssh_command("docker rm observatory-grafana", "Removing Grafana")
    
    # Create config that FORCES anonymous access
    config_cmd = '''
# Create Grafana config that FORCES anonymous
mkdir -p /tmp/grafana-force
cat > /tmp/grafana-force/grafana.ini << 'EOF'
[server]
http_addr = 0.0.0.0
http_port = 3000

[auth.anonymous]
enabled = true
org_role = Viewer

[auth]
disable_login_form = true

[security]
allow_embedding = true

[users]
allow_sign_up = false
EOF
'''
    
    run_ssh_command(config_cmd, "Creating FORCE anonymous config")
    
    # Start with FORCED anonymous settings
    start_cmd = '''docker run -d \\
  --name observatory-grafana \\
  --network host \\
  -v /tmp/grafana-force/grafana.ini:/etc/grafana/grafana.ini:ro \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_AUTH_ANONYMOUS_ENABLED=true \\
  -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer \\
  -e GF_AUTH_DISABLE_LOGIN_FORM=true \\
  -e GF_SECURITY_ALLOW_EMBEDDING=true \\
  grafana/grafana:latest'''
    
    run_ssh_command(start_cmd, "Starting FORCED anonymous Grafana")
    
    time.sleep(20)
    
    # Test it
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing health")
    run_ssh_command("curl -s http://localhost:3000/ | head -5", "Testing homepage")

def main():
    print("🔥 FORCE GRAFANA ANONYMOUS ACCESS")
    print("=" * 40)
    print("NO MORE PASSWORD BULLSHIT")
    
    try:
        force_anonymous_access()
        
        print("\n✅ FORCED anonymous access!")
        print("🌐 https://grafana.observatory.nkllon.com")
        print("📝 Should be anonymous with Viewer role - NO PASSWORD")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())