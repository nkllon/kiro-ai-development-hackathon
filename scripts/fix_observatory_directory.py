#!/usr/bin/env python3
"""
Fix Observatory directory and startup issues
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

def find_observatory_directory():
    """Find where Observatory is actually located"""
    print("🔍 Finding Observatory directory...")
    
    # Check common locations
    locations = [
        "/home/lou/observatory",
        "/home/lou/kiro-ai-development-hackathon", 
        "/home/lou",
        "/opt/observatory"
    ]
    
    for location in locations:
        run_ssh_command(f"ls -la {location}/start_observatory* 2>/dev/null || echo 'Not found'", f"Checking {location}")
    
    # Find any Observatory files
    run_ssh_command("find /home/lou -name 'start_observatory*' 2>/dev/null", "Finding Observatory files")

def fix_observatory_startup():
    """Fix Observatory startup in correct directory"""
    print("\n🔧 Fixing Observatory startup...")
    
    # Kill any existing processes
    run_ssh_command("pkill -f observatory", "Stopping Observatory processes")
    time.sleep(3)
    
    # Check what's actually in the observatory directory
    run_ssh_command("ls -la /home/lou/observatory/", "Checking Observatory directory")
    
    # Start Observatory from correct directory
    start_cmd = """
cd /home/lou/observatory
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=beastmode2025
nohup python3 start_observatory.py > observatory.log 2>&1 &
echo "Observatory started from correct directory"
"""
    
    run_ssh_command(start_cmd, "Starting Observatory from correct directory")
    time.sleep(10)
    
    # Verify it's working
    run_ssh_command("netstat -tlnp | grep 8888", "Checking port 8888")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8888/health", "Testing Observatory health")
    run_ssh_command("ps aux | grep start_observatory", "Checking Observatory process")

def test_all_services():
    """Test all services after fix"""
    print("\n📊 Testing all services...")
    
    services = [
        ("Observatory", "http://localhost:8888/health"),
        ("Prometheus", "http://localhost:9090/"),
        ("Grafana", "http://localhost:3000/api/health")
    ]
    
    for name, url in services:
        run_ssh_command(f"curl -s -o /dev/null -w '{name}: %{{http_code}}\\n' {url}", f"Testing {name}")
    
    # Check tunnel
    run_ssh_command("pgrep -f cloudflared", "Tunnel status")

def main():
    print("🔧 Observatory Directory Fix")
    print("=" * 30)
    
    try:
        find_observatory_directory()
        fix_observatory_startup()
        test_all_services()
        
        print("\n✅ Observatory directory fix completed!")
        print("\n📝 Now run validation to confirm everything works:")
        print("   python scripts/validate_observatory_deployment.py")
        
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())