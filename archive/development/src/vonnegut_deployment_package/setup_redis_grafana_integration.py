#!/usr/bin/env python3
"""
Setup Redis Grafana Integration
Installs Redis plugin and configures dashboards
"""

import subprocess
import time
import requests
import json
import os

def install_redis_plugin():
    """Install Redis datasource plugin in Grafana container."""
    print("🔌 Installing Redis datasource plugin...")
    
    try:
        # Install plugin in Grafana container
        result = subprocess.run([
            'docker', 'exec', 'observatory-grafana',
            'grafana-cli', 'plugins', 'install', 'redis-datasource'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Redis plugin installed successfully")
            return True
        else:
            print(f"❌ Plugin installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing plugin: {e}")
        return False

def restart_grafana():
    """Restart Grafana container to load the plugin."""
    print("🔄 Restarting Grafana to load Redis plugin...")
    
    try:
        subprocess.run(['docker', 'restart', 'observatory-grafana'], check=True)
        print("✅ Grafana restarted")
        
        # Wait for Grafana to be ready
        print("⏳ Waiting for Grafana to be ready...")
        for i in range(30):
            try:
                response = requests.get('http://localhost:3000/api/health', timeout=5)
                if response.status_code == 200:
                    print("✅ Grafana is ready")
                    return True
            except:
                pass
            time.sleep(2)
        
        print("⚠️ Grafana may still be starting up")
        return True
        
    except Exception as e:
        print(f"❌ Error restarting Grafana: {e}")
        return False

def configure_redis_datasource():
    """Configure Redis datasource in Grafana."""
    print("🔧 Configuring Redis datasource...")
    
    datasource_config = {
        "name": "Redis-Observatory",
        "type": "redis-datasource",
        "access": "proxy",
        "url": "redis://msp-ssl-redis:6379",
        "database": "0",
        "jsonData": {
            "client": "standalone",
            "poolSize": 5,
            "timeout": 10,
            "pingInterval": 0,
            "pipelineWindow": 0
        },
        "secureJsonData": {
            "password": ""
        }
    }
    
    try:
        # Use Grafana API to create datasource
        response = requests.post(
            'http://localhost:3000/api/datasources',
            json=datasource_config,
            auth=('admin', os.getenv('GRAFANA_PASSWORD', 'admin')),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 409]:  # 409 = already exists
            print("✅ Redis datasource configured")
            return True
        else:
            print(f"⚠️ Datasource config response: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error configuring datasource: {e}")
        return False

def test_redis_connection():
    """Test Redis connection from Grafana."""
    print("🧪 Testing Redis connection...")
    
    try:
        # Test Redis connection directly
        result = subprocess.run([
            'docker', 'exec', 'observatory-grafana',
            'redis-cli', '-h', 'msp-ssl-redis', '-p', '6379', 'ping'
        ], capture_output=True, text=True)
        
        if 'PONG' in result.stdout:
            print("✅ Redis connection test successful")
            return True
        else:
            print(f"❌ Redis connection test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Redis connection: {e}")
        return False

def check_dashboards():
    """Check if dashboards are loaded."""
    print("📊 Checking dashboard status...")
    
    try:
        response = requests.get(
            'http://localhost:3000/api/search?type=dash-db',
            auth=('admin', os.getenv('GRAFANA_PASSWORD', 'admin'))
        )
        
        if response.status_code == 200:
            dashboards = response.json()
            redis_dashboards = [d for d in dashboards if 'redis' in d.get('title', '').lower() or 'beast-mode' in d.get('title', '').lower()]
            
            print(f"✅ Found {len(dashboards)} total dashboards")
            print(f"📊 Found {len(redis_dashboards)} Redis/Beast Mode dashboards")
            
            for dashboard in redis_dashboards:
                print(f"   - {dashboard.get('title', 'Unknown')}")
            
            return len(redis_dashboards) > 0
        else:
            print(f"❌ Error checking dashboards: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking dashboards: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Redis Grafana Integration")
    print("=" * 50)
    
    # Step 1: Install Redis plugin
    if not install_redis_plugin():
        print("❌ Failed to install Redis plugin")
        return False
    
    # Step 2: Restart Grafana
    if not restart_grafana():
        print("❌ Failed to restart Grafana")
        return False
    
    # Step 3: Test Redis connection
    if not test_redis_connection():
        print("⚠️ Redis connection test failed, but continuing...")
    
    # Step 4: Configure datasource
    if not configure_redis_datasource():
        print("⚠️ Datasource configuration failed, but continuing...")
    
    # Step 5: Check dashboards
    check_dashboards()
    
    print("\n🎉 Redis Grafana integration setup complete!")
    print("📊 Access dashboards at: https://grafana.observatory.nkllon.com")
    print("🔍 Look for these dashboards:")
    print("   - Beast Mode Observatory - Redis Data")
    print("   - LLM Cost Analytics") 
    print("   - Component Health Monitoring")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)