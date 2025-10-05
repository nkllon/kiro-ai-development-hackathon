#!/usr/bin/env python3
"""
Fix Redis Configuration and Restart Observatory
==============================================

Fixes Redis authentication and restarts the Observatory.
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

def fix_redis():
    """Fix Redis configuration."""
    print("🔧 Fixing Redis configuration...")
    
    # Stop and reconfigure Redis
    redis_commands = """
# Stop existing Redis
sudo systemctl stop redis-server 2>/dev/null || true
pkill -f redis-server 2>/dev/null || true

# Start Redis with password
redis-server --daemonize yes --requirepass beastmode2025 --port 6379

# Test Redis connection
redis-cli -a beastmode2025 ping
"""
    
    success, stdout, stderr = ssh_command(redis_commands)
    
    if success and "PONG" in stdout:
        print("✅ Redis is running with authentication")
        return True
    else:
        print("❌ Redis setup failed:")
        print(f"Error: {stderr}")
        return False

def start_observatory():
    """Start Observatory with proper environment variables."""
    print("🚀 Starting Observatory...")
    
    # Stop existing Observatory
    ssh_command("pkill -f observatory 2>/dev/null || true")
    ssh_command("pkill -f start_observatory 2>/dev/null || true")
    
    # Start Observatory with proper environment
    start_command = """
cd /home/lou/observatory
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=beastmode2025
export PROMETHEUS_URL=http://localhost:9090

# Start Observatory
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
    
    # Wait and test
    time.sleep(15)
    
    success, stdout, stderr = ssh_command("curl -s http://localhost:8888/health")
    
    if success and stdout.strip():
        print("✅ Observatory is healthy!")
        print(f"📊 Health response: {stdout}")
        return True
    else:
        print("❌ Observatory health check failed")
        
        # Check logs
        success, stdout, stderr = ssh_command("cd /home/lou/observatory && tail -20 observatory.log")
        if success:
            print("📋 Observatory logs:")
            print(stdout)
        
        return False

def main():
    """Main fix process."""
    print("🔧 Fixing Redis and Observatory on Vonnegut")
    print("=" * 50)
    
    # Fix Redis
    if not fix_redis():
        return False
    
    # Start Observatory
    if not start_observatory():
        return False
    
    print("\n🎉 Observatory is now running properly!")
    print("🌐 Local access: http://192.168.1.119:8888")
    print("📊 Health check: http://192.168.1.119:8888/health")
    print("\n💡 Ready for monitoring stack setup!")
    
    return True

if __name__ == "__main__":
    main()