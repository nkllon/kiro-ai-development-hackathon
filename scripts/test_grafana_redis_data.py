#!/usr/bin/env python3
"""
Test Grafana Redis Data Access
Verifies that Grafana can query Redis data
"""

import requests
import json
import time

def test_redis_datasource():
    """Test Redis datasource connectivity."""
    print("🔧 Testing Redis datasource...")
    
    try:
        response = requests.post(
            'http://localhost:3000/api/datasources/8/health',
            auth=('admin', 'admin'),
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'OK':
                print("✅ Redis datasource is healthy")
                return True
            else:
                print(f"❌ Redis datasource unhealthy: {result}")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing datasource: {e}")
        return False

def test_redis_query():
    """Test querying Redis data through Grafana."""
    print("📊 Testing Redis data query...")
    
    # Test query for Redis keys
    query_data = {
        "queries": [
            {
                "datasource": {
                    "type": "redis-datasource",
                    "uid": "fezw0en2pd2pse"
                },
                "command": "keys",
                "keyName": "*",
                "refId": "A"
            }
        ],
        "range": {
            "from": "now-1h",
            "to": "now"
        }
    }
    
    try:
        response = requests.post(
            'http://localhost:3000/api/ds/query',
            json=query_data,
            auth=('admin', 'admin'),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful: {len(result.get('results', {}))} results")
            return True
        else:
            print(f"❌ Query failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error querying Redis: {e}")
        return False

def test_stream_data():
    """Test querying Redis stream data."""
    print("📈 Testing Redis stream data...")
    
    query_data = {
        "queries": [
            {
                "datasource": {
                    "type": "redis-datasource", 
                    "uid": "fezw0en2pd2pse"
                },
                "command": "xlen",
                "keyName": "observatory_metrics",
                "refId": "A"
            }
        ],
        "range": {
            "from": "now-1h",
            "to": "now"
        }
    }
    
    try:
        response = requests.post(
            'http://localhost:3000/api/ds/query',
            json=query_data,
            auth=('admin', 'admin'),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Stream query successful")
            return True
        else:
            print(f"❌ Stream query failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error querying stream: {e}")
        return False

def check_dashboards():
    """Check if dashboards are available."""
    print("📊 Checking dashboard availability...")
    
    try:
        response = requests.get(
            'http://localhost:3000/api/search?type=dash-db',
            auth=('admin', 'admin')
        )
        
        if response.status_code == 200:
            dashboards = response.json()
            redis_dashboards = [d for d in dashboards if 'redis' in d.get('title', '').lower() or 'beast-mode' in d.get('title', '').lower()]
            
            print(f"✅ Found {len(dashboards)} total dashboards")
            print(f"📊 Found {len(redis_dashboards)} Redis/Beast Mode dashboards:")
            
            for dashboard in redis_dashboards:
                print(f"   - {dashboard.get('title', 'Unknown')} (UID: {dashboard.get('uid', 'N/A')})")
            
            return len(redis_dashboards) > 0
        else:
            print(f"❌ Error checking dashboards: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking dashboards: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing Grafana Redis Integration")
    print("=" * 40)
    
    # Test datasource health
    datasource_ok = test_redis_datasource()
    
    # Test basic query
    query_ok = test_redis_query() if datasource_ok else False
    
    # Test stream data
    stream_ok = test_stream_data() if datasource_ok else False
    
    # Check dashboards
    dashboards_ok = check_dashboards()
    
    print(f"\n📊 Test Results:")
    print(f"   Redis Datasource: {'✅' if datasource_ok else '❌'}")
    print(f"   Basic Queries: {'✅' if query_ok else '❌'}")
    print(f"   Stream Data: {'✅' if stream_ok else '❌'}")
    print(f"   Dashboards: {'✅' if dashboards_ok else '❌'}")
    
    if all([datasource_ok, dashboards_ok]):
        print(f"\n🎉 Grafana Redis integration is working!")
        print(f"🌐 Access dashboards at: https://grafana.observatory.nkllon.com")
        return True
    else:
        print(f"\n❌ Some tests failed - check configuration")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)