#!/usr/bin/env python3
"""
Simple Vonnegut Status Check
============================

Quick check of what's running on Vonnegut.
"""

import subprocess

def simple_check():
    """Simple status check."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    
    print("🔍 Simple Vonnegut status check...")
    
    check_script = f"""
echo "🌐 What's listening on ports..."
sudo netstat -tlnp | grep -E ':(8888|9090|3000|6379)' || echo "No services on expected ports"

echo ""
echo "🐳 Docker containers..."
sudo docker ps -a || echo "Docker not available"

echo ""
echo "🔄 Running processes..."
ps aux | grep -E "(python|redis|prometheus|grafana)" | grep -v grep || echo "No relevant processes"

echo ""
echo "📁 Observatory directory..."
ls -la /home/lou/observatory/ | head -10 || echo "Observatory directory not found"

echo ""
echo "🌐 Quick connectivity test..."
curl -f http://localhost:8888/health 2>&1 | head -3 || echo "Observatory not responding"
"""
    
    try:
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            check_script
        ], text=True, capture_output=True, timeout=30)
        
        print("📋 Status:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Check failed: {e}")
        return False

if __name__ == "__main__":
    simple_check()