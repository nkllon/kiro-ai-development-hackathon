#!/usr/bin/env python3
"""
Simple Repository Discovery with Progress Logging
"""

import sys
import requests
from pathlib import Path

# Add project root to path
sys.path.append('.')

def test_directus_connection():
    """Test Directus connection and get credentials"""
    print("🔍 Testing Directus connection...")
    
    try:
        response = requests.get("http://localhost:8055/server/health", timeout=5)
        if response.status_code == 200:
            print("✅ Directus is running")
            
            # Try to get server info
            response = requests.get("http://localhost:8055/server/info")
            if response.status_code == 200:
                info = response.json()
                print(f"📊 Directus project: {info['data']['project']['project_name']}")
            
            return True
        else:
            print(f"❌ Directus health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Directus: {e}")
        return False

def get_directus_credentials():
    """Get Directus login credentials"""
    print("\n🔐 Directus Login Credentials:")
    print("=" * 40)
    print("🌐 URL: http://localhost:8055/admin")
    print("📧 Email: admin@example.com")
    print("🔑 Password: d1r3ctu5")
    print("=" * 40)

def test_simple_discovery():
    """Test simple file discovery without the complex system"""
    print("\n🔍 Testing simple file discovery...")
    
    try:
        # Simple file discovery
        root_path = Path('.')
        discovered_files = []
        
        print("   Scanning for files...")
        for i, file_path in enumerate(root_path.rglob('*')):
            if file_path.is_file():
                discovered_files.append(str(file_path))
                if i % 1000 == 0 and i > 0:
                    print(f"   Found {i} files...")
        
        print(f"✅ Found {len(discovered_files)} files")
        
        # Show some examples
        print("\n📁 Sample files:")
        for file_path in discovered_files[:10]:
            print(f"   - {file_path}")
        
        if len(discovered_files) > 10:
            print(f"   ... and {len(discovered_files) - 10} more")
        
        return discovered_files
        
    except Exception as e:
        print(f"❌ File discovery failed: {e}")
        return []

def test_directus_collections():
    """Test Directus collections"""
    print("\n📊 Testing Directus collections...")
    
    try:
        # Get auth token
        response = requests.post("http://localhost:8055/auth/login", json={
            'email': 'admin@example.com',
            'password': 'd1r3ctu5'
        })
        
        if response.status_code != 200:
            print(f"❌ Authentication failed: {response.text}")
            return False
        
        token = response.json()['data']['access_token']
        print("✅ Authentication successful")
        
        # Get collections
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get("http://localhost:8055/collections", headers=headers)
        
        if response.status_code == 200:
            collections = response.json()['data']
            print(f"✅ Found {len(collections)} collections:")
            
            for col in collections:
                if not col['collection'].startswith('directus_'):
                    print(f"   - {col['collection']}")
            
            return True
        else:
            print(f"❌ Failed to get collections: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Collection test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Directus and Repository Discovery Test")
    print("=" * 50)
    
    # Test Directus connection
    if not test_directus_connection():
        print("\n❌ Directus is not accessible. Please start it first:")
        print("   cd deployment/local && docker-compose up directus directus-db")
        return 1
    
    # Show credentials
    get_directus_credentials()
    
    # Test collections
    if not test_directus_collections():
        print("\n❌ Cannot access Directus collections")
        return 1
    
    # Test simple discovery
    files = test_simple_discovery()
    if not files:
        print("\n❌ File discovery failed")
        return 1
    
    print(f"\n🎉 All tests passed!")
    print(f"📊 Ready to load {len(files)} files into Directus")
    print(f"🌐 Login at: http://localhost:8055/admin")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
