#!/usr/bin/env python3
"""
Quick Start Observatory
======================

Quick command to start Observatory container.
"""

import subprocess

def quick_start():
    """Quick start Observatory."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    
    print("🚀 Quick starting Observatory...")
    
    # Simple command to start Observatory
    cmd = f"""ssh {ssh_user}@{vonnegut_ip} 'cd /home/lou/observatory && sudo docker run -d --name observatory-app --network host -v $(pwd):/app -w /app -e REDIS_HOST=localhost -e REDIS_PASSWORD=beastmode2025 -e PROMETHEUS_URL=http://localhost:9090 python:3.9-slim bash -c "apt-get update && apt-get install -y gcc curl && pip install -r requirements.txt && python start_observatory.py"'"""
    
    try:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=60)
        
        print("📋 Output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errors:")
            print(result.stderr)
        
        # Check if it's running
        check_cmd = f"""ssh {ssh_user}@{vonnegut_ip} 'sleep 30 && curl -f http://localhost:8888/health'"""
        
        print("\n🔍 Checking if Observatory is running...")
        check_result = subprocess.run(check_cmd, shell=True, text=True, capture_output=True, timeout=45)
        
        if check_result.returncode == 0:
            print("✅ Observatory is running!")
            print(check_result.stdout)
        else:
            print("❌ Observatory not responding yet")
            print(check_result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Quick start failed: {e}")
        return False

if __name__ == "__main__":
    quick_start()