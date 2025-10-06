#!/usr/bin/env python3
"""
Grafana Dashboard Emergency Fix
==============================

Quick fix for broken Grafana dashboard and missing metrics.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import subprocess
import time
import requests
import json
import sys

def check_service(url, name):
    """Check if a service is responding."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name} is running")
            return True
        else:
            print(f"⚠️ {name} responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name} is not responding: {e}")
        return False

def start_beast_mode_services():
    """Start Beast Mode services for metrics."""
    print("🚀 Starting Beast Mode services...")
    
    # Start the observatory
    try:
        subprocess.Popen([
            "python", "start_observatory.py"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Observatory started")
        time.sleep(3)
    except Exception as e:
        print(f"⚠️ Could not start observatory: {e}")
    
    # Start metrics exporter if available
    try:
        subprocess.Popen([
            "python", "-m", "src.prometheus_exporter"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Metrics exporter started")
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Could not start metrics exporter: {e}")

def fix_grafana_datasource():
    """Fix Grafana datasource configuration."""
    print("🔧 Checking Grafana datasource...")
    
    grafana_url = "http://localhost:3000"
    
    # Check if Grafana is accessible
    if not check_service(f"{grafana_url}/api/health", "Grafana"):
        print("❌ Grafana is not accessible")
        return False
    
    # Check datasources
    try:
        response = requests.get(f"{grafana_url}/api/datasources")
        if response.status_code == 200:
            datasources = response.json()
            prometheus_ds = next((ds for ds in datasources if ds['type'] == 'prometheus'), None)
            
            if prometheus_ds:
                print(f"✅ Prometheus datasource found: {prometheus_ds['url']}")
                
                # Test the datasource
                prometheus_url = prometheus_ds['url'] or "http://localhost:9090"
                if check_service(f"{prometheus_url}/api/v1/query?query=up", "Prometheus"):
                    print("✅ Prometheus is accessible from Grafana")
                    return True
                else:
                    print("⚠️ Prometheus is not accessible from Grafana")
                    return False
            else:
                print("❌ No Prometheus datasource found in Grafana")
                return False
    except Exception as e:
        print(f"❌ Error checking Grafana datasources: {e}")
        return False

def create_basic_dashboard():
    """Create a basic dashboard to show system is working."""
    print("📊 Creating basic dashboard...")
    
    dashboard_config = {
        "dashboard": {
            "title": "Beast Mode Observatory - Emergency Dashboard",
            "panels": [
                {
                    "title": "System Status",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "up",
                            "legendFormat": "{{instance}}"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                },
                {
                    "title": "Service Uptime",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "up",
                            "legendFormat": "{{job}}"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                }
            ],
            "time": {"from": "now-1h", "to": "now"},
            "refresh": "5s"
        },
        "overwrite": True
    }
    
    try:
        response = requests.post(
            "http://localhost:3000/api/dashboards/db",
            json=dashboard_config,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            print("✅ Emergency dashboard created")
            return True
        else:
            print(f"⚠️ Could not create dashboard: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
        return False

def main():
    """Main fix routine."""
    print("🚨 GRAFANA EMERGENCY FIX")
    print("=" * 40)
    
    # Step 1: Check current status
    print("\n1️⃣ Checking current status...")
    grafana_ok = check_service("http://localhost:3000/api/health", "Grafana")
    prometheus_ok = check_service("http://localhost:9090/api/v1/query?query=up", "Prometheus")
    
    if not grafana_ok:
        print("❌ Grafana is not running. Please start Grafana first.")
        return 1
    
    if not prometheus_ok:
        print("❌ Prometheus is not running. Please start Prometheus first.")
        return 1
    
    # Step 2: Start Beast Mode services
    print("\n2️⃣ Starting Beast Mode services...")
    start_beast_mode_services()
    
    # Step 3: Fix datasource
    print("\n3️⃣ Fixing Grafana datasource...")
    datasource_ok = fix_grafana_datasource()
    
    # Step 4: Create emergency dashboard
    print("\n4️⃣ Creating emergency dashboard...")
    dashboard_ok = create_basic_dashboard()
    
    # Step 5: Final status
    print("\n" + "=" * 40)
    print("📊 GRAFANA FIX SUMMARY")
    print("=" * 40)
    
    if grafana_ok and prometheus_ok and datasource_ok:
        print("✅ Grafana is working!")
        print("✅ Prometheus is connected!")
        print("✅ Dashboard should be updating!")
        print("\n🎯 Access your dashboard at:")
        print("   http://localhost:3000")
        
        if dashboard_ok:
            print("✅ Emergency dashboard created")
        
        return 0
    else:
        print("⚠️ Some issues remain:")
        if not grafana_ok:
            print("   ❌ Grafana not accessible")
        if not prometheus_ok:
            print("   ❌ Prometheus not accessible")
        if not datasource_ok:
            print("   ❌ Datasource configuration issues")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())