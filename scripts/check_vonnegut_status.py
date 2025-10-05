#!/usr/bin/env python3
"""
Check Vonnegut Observatory Status
===============================

Check the current status of Observatory services on Vonnegut.
"""

import subprocess
import sys

def check_status():
    """Check the status of services on Vonnegut."""
    print("🔍 Checking Vonnegut Observatory Status")
    print("=" * 45)
    
    try:
        # Check processes
        print("📊 Checking running processes...")
        result = subprocess.run([
            "ssh", "lou@192.168.1.119", 
            "ps aux | grep -E '(observatory|prometheus|grafana|cloudflared)' | grep -v grep"
        ], text=True, capture_output=True, timeout=30)
        
        if result.stdout.strip():
            print("✅ Running processes:")
            print(result.stdout)
        else:
            print("❌ No Observatory processes found")
        
        # Check ports
        print("\n🔌 Checking listening ports...")
        result = subprocess.run([
            "ssh", "lou@192.168.1.119",
            "netstat -tlnp | grep -E '(8888|9090|3000)'"
        ], text=True, capture_output=True, timeout=30)
        
        if result.stdout.strip():
            print("✅ Listening ports:")
            print(result.stdout)
        else:
            print("❌ No Observatory ports listening")
        
        # Test local connectivity
        print("\n🧪 Testing local connectivity...")
        services = [
            ("Observatory", "http://localhost:8888/health"),
            ("Prometheus", "http://localhost:9090/-/healthy"),
            ("Grafana", "http://localhost:3000/api/health")
        ]
        
        for service, url in services:
            result = subprocess.run([
                "ssh", "lou@192.168.1.119",
                f"curl -s -f {url}"
            ], text=True, capture_output=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ {service}: Healthy")
                if "observatory" in service.lower():
                    print(f"   Response: {result.stdout[:100]}...")
            else:
                print(f"❌ {service}: Unhealthy")
        
        # Check external access
        print("\n🌐 Checking external access...")
        external_urls = [
            "https://observatory.niclon.com/health",
            "https://prometheus.observatory.niclon.com/-/healthy",
            "https://grafana.observatory.niclon.com/api/health"
        ]
        
        for url in external_urls:
            try:
                import requests
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {url}: Accessible")
                else:
                    print(f"❌ {url}: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {url}: {str(e)[:50]}...")
        
        # Summary
        print("\n📋 Summary:")
        print("If Observatory is running locally but not externally accessible,")
        print("the Cloudflare tunnel may need to be restarted.")
        print("\n🔧 To restart services:")
        print("ssh lou@192.168.1.119")
        print("cd /home/lou/observatory")
        print("REDIS_PASSWORD=beastmode2025 python3 start_observatory.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

if __name__ == "__main__":
    success = check_status()
    sys.exit(0 if success else 1)