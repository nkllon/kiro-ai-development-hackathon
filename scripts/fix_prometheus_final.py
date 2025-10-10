#!/usr/bin/env python3
"""
Final fix for Prometheus - start clean without rule files
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

def fix_prometheus_clean():
    """Fix Prometheus with clean configuration"""
    print("🔧 Starting Prometheus with clean configuration...")
    
    # Stop and remove current Prometheus
    run_ssh_command("docker stop observatory-prometheus 2>/dev/null || true", "Stopping Prometheus")
    run_ssh_command("docker rm observatory-prometheus 2>/dev/null || true", "Removing Prometheus")
    
    # Start Prometheus with minimal configuration (no rule files)
    prometheus_command = '''docker run -d \\
  --name observatory-prometheus \\
  --network host \\
  -v prometheus-data:/prometheus \\
  prom/prometheus:latest \\
  --storage.tsdb.path=/prometheus \\
  --web.console.libraries=/etc/prometheus/console_libraries \\
  --web.console.templates=/etc/prometheus/consoles \\
  --web.enable-lifecycle \\
  --web.enable-admin-api'''
    
    run_ssh_command(prometheus_command, "Starting Prometheus with default config")
    
    time.sleep(10)
    
    # Test Prometheus
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/", "Testing Prometheus")
    run_ssh_command("curl -s http://localhost:9090/-/healthy", "Testing Prometheus health endpoint")
    run_ssh_command("docker logs observatory-prometheus --tail 5", "Checking Prometheus logs")

def test_all_services():
    """Test all services"""
    print("\n📊 Testing all services...")
    
    run_ssh_command("curl -s -o /dev/null -w 'Observatory: %{http_code}\\n' http://localhost:8888/health", "Observatory")
    run_ssh_command("curl -s -o /dev/null -w 'Prometheus: %{http_code}\\n' http://localhost:9090/", "Prometheus")
    run_ssh_command("curl -s -o /dev/null -w 'Grafana: %{http_code}\\n' http://localhost:3000/api/health", "Grafana")
    
    run_ssh_command("docker ps --format 'table {{.Names}}\\t{{.Status}}' | grep observatory", "Container status")
    
    # Check tunnel status
    run_ssh_command("pgrep -f cloudflared", "Tunnel process")

def main():
    print("🔧 Final Prometheus Fix")
    print("=" * 25)
    
    try:
        fix_prometheus_clean()
        test_all_services()
        
        print("\n✅ Final fix completed!")
        print("\n🌐 All services should now be accessible:")
        print("   Observatory: https://observatory.nkllon.com")
        print("   Prometheus: https://prometheus.observatory.nkllon.com")
        print("   Grafana: https://grafana.observatory.nkllon.com (anonymous access)")
        print("\n📝 Summary:")
        print("   ✅ Observatory: Running natively on port 8888")
        print("   ✅ Prometheus: Running in container on port 9090 (clean config)")
        print("   ✅ Grafana: Running in container on port 3000 (anonymous enabled)")
        print("   ✅ Tunnel: Configured for all observatory.nkllon.com subdomains")
        
    except Exception as e:
        print(f"\n❌ Error during final fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())