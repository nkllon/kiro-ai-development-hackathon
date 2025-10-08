#!/usr/bin/env python3
"""
Fix Redis Grafana Connection
Creates properly configured Redis datasource
"""

import requests
import json
import os

def create_redis_datasource():
    """Create Redis datasource with proper configuration."""
    
    # Try different Redis configurations
    configs_to_try = [
        {
            "name": "Redis-Observatory-NoAuth",
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
            "secureJsonData": {}
        },
        {
            "name": "Redis-Observatory-WithAuth",
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
                "password": os.getenv('REDIS_PASSWORD', '')
            }
        },
        {
            "name": "Redis-Observatory-Host",
            "type": "redis-datasource",
            "access": "proxy",
            "url": "redis://host.docker.internal:6379", 
            "database": "0",
            "jsonData": {
                "client": "standalone",
                "poolSize": 5,
                "timeout": 10,
                "pingInterval": 0,
                "pipelineWindow": 0
            },
            "secureJsonData": {}
        }
    ]
    
    grafana_password = os.getenv('GRAFANA_PASSWORD', 'admin')
    
    for i, config in enumerate(configs_to_try):
        print(f"🔧 Trying configuration {i+1}: {config['name']}")
        
        try:
            response = requests.post(
                'http://localhost:3000/api/datasources',
                json=config,
                auth=('admin', grafana_password),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Successfully created datasource: {config['name']}")
                
                # Test the datasource
                datasource_id = response.json().get('id')
                if test_datasource(datasource_id, grafana_password):
                    print(f"✅ Datasource {config['name']} is working!")
                    return datasource_id
                else:
                    print(f"❌ Datasource {config['name']} created but not working")
                    
            elif response.status_code == 409:
                print(f"⚠️ Datasource {config['name']} already exists")
            else:
                print(f"❌ Failed to create {config['name']}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating {config['name']}: {e}")
    
    return None

def test_datasource(datasource_id, grafana_password):
    """Test if datasource is working."""
    try:
        response = requests.post(
            f'http://localhost:3000/api/datasources/{datasource_id}/health',
            auth=('admin', grafana_password),
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('status') == 'success'
        else:
            print(f"Health check failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing datasource: {e}")
        return False

def list_datasources():
    """List current datasources."""
    try:
        response = requests.get(
            'http://localhost:3000/api/datasources',
            auth=('admin', os.getenv('GRAFANA_PASSWORD', 'admin'))
        )
        
        if response.status_code == 200:
            datasources = response.json()
            print(f"📊 Current datasources:")
            for ds in datasources:
                print(f"   - {ds['name']} ({ds['type']}) - ID: {ds['id']}")
            return datasources
        else:
            print(f"Failed to list datasources: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error listing datasources: {e}")
        return []

def main():
    """Main function."""
    print("🔧 Fixing Redis Grafana Connection")
    print("=" * 40)
    
    # List current datasources
    list_datasources()
    
    # Create working Redis datasource
    datasource_id = create_redis_datasource()
    
    if datasource_id:
        print(f"\n🎉 Successfully configured Redis datasource (ID: {datasource_id})")
        print("📊 You can now use Redis data in Grafana dashboards")
    else:
        print("\n❌ Failed to configure working Redis datasource")
        print("🔍 Check Redis container connectivity and authentication")
    
    return datasource_id is not None

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)