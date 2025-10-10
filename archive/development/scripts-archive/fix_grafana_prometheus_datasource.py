#!/usr/bin/env python3
"""
Fix Grafana Prometheus Data Source Configuration
===============================================

Updates Grafana data source to use the public Cloudflare tunnel endpoint
instead of localhost, so it can properly connect through the tunnel.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional


class GrafanaDataSourceFixer:
    """Fixes Grafana Prometheus data source configuration for Cloudflare tunnel access."""
    
    def __init__(self, grafana_url: str = "http://localhost:3000"):
        self.grafana_url = grafana_url.rstrip('/')
        self.prometheus_public_url = "https://prometheus.observatory.nkllon.com"
        self.prometheus_local_url = "http://localhost:9090"
        
        # Grafana API credentials (using anonymous access)
        self.session = requests.Session()
        
    def get_data_sources(self) -> Optional[list]:
        """Get all data sources from Grafana."""
        try:
            response = self.session.get(f"{self.grafana_url}/api/datasources")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get data sources: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting data sources: {e}")
            return None
    
    def find_prometheus_datasource(self, data_sources: list) -> Optional[Dict[str, Any]]:
        """Find the Prometheus data source."""
        for ds in data_sources:
            if ds.get('type') == 'prometheus':
                return ds
        return None
    
    def update_prometheus_datasource(self, datasource_id: int, current_config: Dict[str, Any]) -> bool:
        """Update Prometheus data source to use public URL."""
        try:
            # Update the URL to use public endpoint
            updated_config = current_config.copy()
            updated_config['url'] = self.prometheus_public_url
            updated_config['access'] = 'proxy'  # Use proxy access for external URLs
            
            # Ensure proper configuration for external access
            if 'jsonData' not in updated_config:
                updated_config['jsonData'] = {}
            
            updated_config['jsonData']['httpMethod'] = 'GET'
            updated_config['jsonData']['timeInterval'] = '15s'
            
            response = self.session.put(
                f"{self.grafana_url}/api/datasources/{datasource_id}",
                json=updated_config,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print(f"✅ Successfully updated Prometheus data source")
                return True
            else:
                print(f"❌ Failed to update data source: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating data source: {e}")
            return False
    
    def test_prometheus_connectivity(self) -> bool:
        """Test connectivity to Prometheus through public endpoint."""
        try:
            print("🔍 Testing Prometheus connectivity...")
            
            # Test public endpoint
            response = requests.get(f"{self.prometheus_public_url}/api/v1/query?query=up", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    print(f"✅ Prometheus public endpoint is accessible")
                    print(f"   URL: {self.prometheus_public_url}")
                    return True
                else:
                    print(f"❌ Prometheus returned error: {data}")
                    return False
            else:
                print(f"❌ Prometheus not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing Prometheus connectivity: {e}")
            return False
    
    def create_prometheus_datasource(self) -> bool:
        """Create a new Prometheus data source with correct configuration."""
        try:
            datasource_config = {
                "name": "Prometheus-Public",
                "type": "prometheus",
                "url": self.prometheus_public_url,
                "access": "proxy",
                "isDefault": True,
                "jsonData": {
                    "httpMethod": "GET",
                    "timeInterval": "15s",
                    "queryTimeout": "60s"
                },
                "secureJsonFields": {},
                "version": 1,
                "readOnly": False
            }
            
            response = self.session.post(
                f"{self.grafana_url}/api/datasources",
                json=datasource_config,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print(f"✅ Successfully created new Prometheus data source")
                return True
            else:
                print(f"❌ Failed to create data source: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating data source: {e}")
            return False
    
    def fix_datasource_configuration(self) -> bool:
        """Main method to fix Grafana Prometheus data source configuration."""
        print("🔧 Fixing Grafana Prometheus Data Source Configuration")
        print("=" * 60)
        
        # Test Prometheus connectivity first
        if not self.test_prometheus_connectivity():
            print("❌ Cannot proceed - Prometheus is not accessible")
            return False
        
        # Get current data sources
        print("\n📋 Getting current Grafana data sources...")
        data_sources = self.get_data_sources()
        
        if data_sources is None:
            print("❌ Cannot get data sources from Grafana")
            return False
        
        print(f"✅ Found {len(data_sources)} data sources")
        
        # Find Prometheus data source
        prometheus_ds = self.find_prometheus_datasource(data_sources)
        
        if prometheus_ds:
            print(f"\n🎯 Found Prometheus data source:")
            print(f"   ID: {prometheus_ds['id']}")
            print(f"   Name: {prometheus_ds['name']}")
            print(f"   Current URL: {prometheus_ds['url']}")
            
            if prometheus_ds['url'] == self.prometheus_public_url:
                print(f"✅ Data source already configured correctly!")
                return True
            
            # Update existing data source
            print(f"\n🔄 Updating data source to use public endpoint...")
            return self.update_prometheus_datasource(prometheus_ds['id'], prometheus_ds)
        
        else:
            print(f"\n➕ No Prometheus data source found, creating new one...")
            return self.create_prometheus_datasource()
    
    def verify_configuration(self) -> bool:
        """Verify the data source configuration is working."""
        try:
            print("\n🧪 Verifying Grafana data source configuration...")
            
            # Test data source via Grafana API
            response = self.session.get(f"{self.grafana_url}/api/datasources/proxy/1/api/v1/query?query=up")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    print(f"✅ Grafana can successfully query Prometheus!")
                    return True
                else:
                    print(f"❌ Grafana query failed: {data}")
                    return False
            else:
                print(f"❌ Grafana proxy request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying configuration: {e}")
            return False


def main():
    """Main execution function."""
    print("🔧 Grafana Prometheus Data Source Configuration Fixer")
    print("=" * 60)
    print("This script fixes Grafana to use the public Prometheus endpoint")
    print("through Cloudflare tunnel instead of localhost.")
    print("=" * 60)
    
    fixer = GrafanaDataSourceFixer()
    
    try:
        # Fix the configuration
        success = fixer.fix_datasource_configuration()
        
        if success:
            # Verify it's working
            time.sleep(2)  # Give Grafana a moment to update
            verification_success = fixer.verify_configuration()
            
            if verification_success:
                print(f"\n🚀 SUCCESS!")
                print(f"✅ Grafana is now configured to use: https://prometheus.observatory.nkllon.com")
                print(f"✅ Data source connectivity verified")
                print(f"\n💡 Next steps:")
                print(f"   1. Open Grafana at: https://grafana.observatory.nkllon.com")
                print(f"   2. Check that dashboards are loading data")
                print(f"   3. Verify metrics are being displayed correctly")
                return True
            else:
                print(f"\n⚠️ Configuration updated but verification failed")
                print(f"💡 Try refreshing Grafana and check the data source manually")
                return False
        else:
            print(f"\n❌ Failed to fix data source configuration")
            print(f"\n💡 Manual steps:")
            print(f"   1. Open Grafana at: https://grafana.observatory.nkllon.com")
            print(f"   2. Go to Configuration > Data Sources")
            print(f"   3. Edit Prometheus data source")
            print(f"   4. Change URL to: https://prometheus.observatory.nkllon.com")
            print(f"   5. Set Access to 'Server (default)'")
            print(f"   6. Save & Test")
            return False
            
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)