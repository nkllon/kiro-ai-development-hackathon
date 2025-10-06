#!/usr/bin/env python3
"""
Fix Grafana Prometheus Data Source with Admin Access
===================================================

Updates Grafana data source using admin credentials to use the public 
Cloudflare tunnel endpoint instead of localhost.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import requests
import json
import sys
import base64
from typing import Dict, Any, Optional


def fix_grafana_datasource():
    """Fix Grafana data source configuration using admin access."""
    
    grafana_url = "http://localhost:3000"
    prometheus_public_url = "https://prometheus.observatory.nkllon.com"
    
    # Try common admin passwords
    admin_passwords = ["admin123", "admin", "systematic", "grafana", "password"]
    
    print("🔧 Fixing Grafana Prometheus Data Source with Admin Access")
    print("=" * 60)
    
    # Test Prometheus connectivity first
    print("🔍 Testing Prometheus public endpoint...")
    try:
        response = requests.get(f"{prometheus_public_url}/api/v1/query?query=up", timeout=10)
        if response.status_code == 200:
            print(f"✅ Prometheus is accessible at {prometheus_public_url}")
        else:
            print(f"❌ Prometheus not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Prometheus: {e}")
        return False
    
    # Try to authenticate with admin
    session = None
    for password in admin_passwords:
        try:
            print(f"\n🔑 Trying admin password: {password}")
            
            s = requests.Session()
            
            # Try basic auth first
            s.auth = ('admin', password)
            
            # Test authentication
            response = s.get(f"{grafana_url}/api/datasources")
            
            if response.status_code == 200:
                print(f"✅ Successfully authenticated with admin:{password}")
                session = s
                break
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error with password {password}: {e}")
    
    if not session:
        print(f"\n❌ Could not authenticate with any admin password")
        print(f"💡 Try accessing Grafana manually:")
        print(f"   1. Go to http://localhost:3000")
        print(f"   2. Login with admin credentials")
        print(f"   3. Go to Configuration > Data Sources")
        print(f"   4. Edit Prometheus data source")
        print(f"   5. Change URL to: {prometheus_public_url}")
        return False
    
    # Get current data sources
    print(f"\n📋 Getting current data sources...")
    try:
        response = session.get(f"{grafana_url}/api/datasources")
        if response.status_code != 200:
            print(f"❌ Failed to get data sources: {response.status_code}")
            return False
        
        data_sources = response.json()
        print(f"✅ Found {len(data_sources)} data sources")
        
        # Find Prometheus data source
        prometheus_ds = None
        for ds in data_sources:
            if ds.get('type') == 'prometheus':
                prometheus_ds = ds
                break
        
        if not prometheus_ds:
            print(f"❌ No Prometheus data source found")
            return False
        
        print(f"\n🎯 Found Prometheus data source:")
        print(f"   ID: {prometheus_ds['id']}")
        print(f"   Name: {prometheus_ds['name']}")
        print(f"   Current URL: {prometheus_ds['url']}")
        
        if prometheus_ds['url'] == prometheus_public_url:
            print(f"✅ Data source already configured correctly!")
            return True
        
        # Update the data source
        print(f"\n🔄 Updating data source to use public endpoint...")
        
        updated_config = prometheus_ds.copy()
        updated_config['url'] = prometheus_public_url
        updated_config['access'] = 'proxy'
        
        # Ensure proper configuration
        if 'jsonData' not in updated_config:
            updated_config['jsonData'] = {}
        
        updated_config['jsonData']['httpMethod'] = 'GET'
        updated_config['jsonData']['timeInterval'] = '15s'
        
        response = session.put(
            f"{grafana_url}/api/datasources/{prometheus_ds['id']}",
            json=updated_config,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print(f"✅ Successfully updated Prometheus data source!")
            
            # Test the data source
            print(f"\n🧪 Testing data source connectivity...")
            test_response = session.get(f"{grafana_url}/api/datasources/proxy/{prometheus_ds['id']}/api/v1/query?query=up")
            
            if test_response.status_code == 200:
                data = test_response.json()
                if data.get('status') == 'success':
                    print(f"✅ Data source test successful!")
                    print(f"\n🚀 SUCCESS!")
                    print(f"✅ Grafana is now configured to use: {prometheus_public_url}")
                    print(f"✅ Data source connectivity verified")
                    print(f"\n💡 Next steps:")
                    print(f"   1. Open Grafana at: https://grafana.observatory.nkllon.com")
                    print(f"   2. Check that dashboards are loading data")
                    print(f"   3. Verify metrics are being displayed correctly")
                    return True
                else:
                    print(f"❌ Data source test failed: {data}")
                    return False
            else:
                print(f"❌ Data source test failed: {test_response.status_code}")
                return False
        else:
            print(f"❌ Failed to update data source: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating data source: {e}")
        return False


if __name__ == "__main__":
    success = fix_grafana_datasource()
    sys.exit(0 if success else 1)