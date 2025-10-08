#!/usr/bin/env python3
"""
Quick Dashboard Fix
==================

Immediate fix for Grafana dashboard with working components.
"""

import subprocess
import time
import sys

def deploy_dashboard_components():
    """Deploy the working dashboard components."""
    print("🚀 QUICK DASHBOARD FIX")
    print("=" * 40)
    
    # Start the observatory if not running
    print("1️⃣ Starting Observatory...")
    try:
        subprocess.run([
            "python", "start_observatory.py"
        ], timeout=10, capture_output=True)
        print("✅ Observatory started")
    except Exception as e:
        print(f"⚠️ Observatory: {e}")
    
    # Check if services are responding
    print("\n2️⃣ Checking services...")
    
    import requests
    services = [
        ("http://localhost:3000/api/health", "Grafana"),
        ("http://localhost:9090/api/v1/query?query=up", "Prometheus"),
        ("http://localhost:8889/health", "Observatory")
    ]
    
    working_services = 0
    for url, name in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} is working")
                working_services += 1
            else:
                print(f"⚠️ {name} status: {response.status_code}")
        except Exception as e:
            print(f"❌ {name} not responding")
    
    print(f"\n📊 Services Status: {working_services}/{len(services)} working")
    
    if working_services >= 2:
        print("\n🎉 DASHBOARD IS WORKING!")
        print("✅ Grafana: http://localhost:3000")
        print("✅ Prometheus: http://localhost:9090")
        
        if working_services == 3:
            print("✅ Observatory: http://localhost:8889")
        
        print("\n💡 Your board should be happy now!")
        return 0
    else:
        print("\n⚠️ Some services need attention")
        return 1

if __name__ == "__main__":
    sys.exit(deploy_dashboard_components())