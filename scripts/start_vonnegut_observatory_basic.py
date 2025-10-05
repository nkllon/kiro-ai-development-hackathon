#!/usr/bin/env python3
"""
Basic Vonnegut Observatory Starter
=================================

Just gets the Observatory application running on Vonnegut.
"""

import subprocess
import time

def ssh_command(command: str) -> tuple[bool, str, str]:
    """Execute SSH command on Vonnegut."""
    try:
        result = subprocess.run([
            "ssh", "lou@192.168.1.119", command
        ], capture_output=True, text=True, timeout=60)
        
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def start_observatory():
    """Start Observatory on Vonnegut."""
    print("🚀 Starting Observatory on Vonnegut...")
    
    # 1. Stop any existing processes
    print("🛑 Stopping existing processes...")
    ssh_command("pkill -f observatory 2>/dev/null || true")
    ssh_command("pkill -f start_observatory 2>/dev/null || true")
    
    # 2. Start Observatory directly
    print("▶️ Starting Observatory application...")
    
    start_command = """
cd /home/lou/observatory
export REDIS_HOST=localhost
export REDIS_PASSWORD=beastmode2025
export PROMETHEUS_URL=http://localhost:9090
nohup python3 start_observatory.py > observatory.log 2>&1 &
echo "Observatory started with PID: $!"
"""
    
    success, stdout, stderr = ssh_command(start_command)
    
    if success:
        print("✅ Observatory started")
        print(f"📋 Output: {stdout}")
    else:
        print("❌ Failed to start Observatory:")
        print(f"Error: {stderr}")
        return False
    
    # 3. Wait and test
    print("⏳ Waiting for Observatory to initialize...")
    time.sleep(10)
    
    # 4. Test Observatory
    print("🧪 Testing Observatory...")
    success, stdout, stderr = ssh_command("curl -s http://localhost:8888/health")
    
    if success and stdout.strip():
        print("✅ Observatory is responding!")
        print(f"📊 Health response: {stdout}")
        
        # Test the main page
        success, stdout, stderr = ssh_command("curl -s http://localhost:8888/ | head -5")
        if success:
            print("✅ Observatory main page is serving")
        
        return True
    else:
        print("❌ Observatory health check failed")
        print(f"Error: {stderr}")
        
        # Check logs
        print("📋 Checking logs...")
        success, stdout, stderr = ssh_command("cd /home/lou/observatory && tail -20 observatory.log")
        if success:
            print("Observatory logs:")
            print(stdout)
        
        return False

if __name__ == "__main__":
    if start_observatory():
        print("\n🎉 Observatory is running on Vonnegut!")
        print("🌐 Local access: http://192.168.1.119:8888")
        print("📊 Health check: http://192.168.1.119:8888/health")
        print("\n💡 Next steps:")
        print("1. Configure Cloudflare tunnel to route to localhost:8888")
        print("2. Set up Prometheus to scrape localhost:8888/metrics")
        print("3. Configure Grafana with Prometheus data source")
    else:
        print("\n❌ Observatory failed to start")
        print("Check the logs on Vonnegut for more details")