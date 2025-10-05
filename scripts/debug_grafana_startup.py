#!/usr/bin/env python3
"""
Debug Grafana startup issues
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

def debug_grafana():
    """Debug Grafana startup issues"""
    print("🔍 Debugging Grafana startup...")
    
    # Check if container is running
    run_ssh_command("docker ps | grep grafana", "Checking Grafana container")
    
    # Check container logs
    run_ssh_command("docker logs observatory-grafana --tail 20", "Checking Grafana logs")
    
    # Check if port 3000 is bound
    run_ssh_command("netstat -tlnp | grep 3000", "Checking port 3000")
    
    # Check container status
    run_ssh_command("docker inspect observatory-grafana --format='{{.State.Status}}'", "Container status")
    
    # Try to restart with simpler config
    print("\n🔧 Trying simpler Grafana configuration...")
    
    run_ssh_command("docker stop observatory-grafana", "Stopping Grafana")
    run_ssh_command("docker rm observatory-grafana", "Removing Grafana")
    
    # Start with minimal configuration
    simple_cmd = '''docker run -d \\
  --name observatory-grafana \\
  --network host \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_AUTH_ANONYMOUS_ENABLED=true \\
  -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer \\
  -e GF_SECURITY_ADMIN_PASSWORD=admin \\
  grafana/grafana:latest'''
    
    run_ssh_command(simple_cmd, "Starting Grafana with minimal config")
    
    time.sleep(15)
    
    # Test again
    run_ssh_command("docker ps | grep grafana", "Checking container after restart")
    run_ssh_command("docker logs observatory-grafana --tail 10", "Checking logs after restart")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing health after restart")

def main():
    print("🔍 Grafana Startup Debug")
    print("=" * 30)
    
    try:
        debug_grafana()
        
        print("\n📊 Debug completed!")
        print("Check the output above to identify the Grafana startup issue")
        
    except Exception as e:
        print(f"\n❌ Error during debug: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())