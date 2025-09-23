#!/usr/bin/env python3
"""
Test Directus Loading - Small Batch with Duplicate Prevention
"""

import sys
import requests
import hashlib
from pathlib import Path

# Add project root to path
sys.path.append('.')

DIRECTUS_URL = "http://localhost:8055"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "d1r3ctu5"

def get_auth_token():
    """Get authentication token from Directus"""
    print("🔐 Authenticating with Directus...")
    
    response = requests.post(f"{DIRECTUS_URL}/auth/login", json={
        'email': ADMIN_EMAIL,
        'password': ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json()['data']['access_token']
        print("✅ Authentication successful")
        return token
    else:
        print(f"❌ Authentication failed: {response.text}")
        return None

def check_existing_items(token):
    """Check what's already in Directus"""
    print("📊 Checking existing items...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Check repository_items
    response = requests.get(f"{DIRECTUS_URL}/items/repository_items?limit=5", headers=headers)
    if response.status_code == 200:
        items = response.json()['data']
        print(f"   Repository items: {len(items)}")
        for item in items:
            print(f"   - {item.get('name', 'NO_NAME')} ({item.get('item_type', 'NO_TYPE')})")
    else:
        print(f"   ❌ Failed to get repository items: {response.text}")
    
    # Check specifications
    response = requests.get(f"{DIRECTUS_URL}/items/specifications?limit=5", headers=headers)
    if response.status_code == 200:
        specs = response.json()['data']
        print(f"   Specifications: {len(specs)}")
        for spec in specs:
            print(f"   - {spec.get('spec_name', 'NO_NAME')} ({spec.get('spec_type', 'NO_TYPE')})")
    else:
        print(f"   ❌ Failed to get specifications: {response.text}")

def get_file_hash(file_path):
    """Get content hash for duplicate detection"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()
    except Exception:
        return None

def load_test_files(token):
    """Load a small batch of test files"""
    print("\n🔍 Loading test files...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Select a few interesting files to test with
    test_files = [
        'README.md',
        'Makefile',
        'requirements.txt',
        '.kiro/specs/reflective-module-architecture-consolidation/requirements.md',
        'src/beast_mode/core/reflective_module.py'
    ]
    
    loaded_count = 0
    skipped_count = 0
    
    for file_path in test_files:
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            print(f"   ⚠️ File not found: {file_path}")
            continue
        
        # Get file info
        stat = path_obj.stat()
        content_hash = get_file_hash(path_obj)
        
        # Check if already exists by path
        response = requests.get(f"{DIRECTUS_URL}/items/repository_items?filter[path][_eq]={file_path}", headers=headers)
        if response.status_code == 200:
            existing = response.json()['data']
            if existing:
                print(f"   ⏭️ Skipping {file_path} (already exists)")
                skipped_count += 1
                continue
        
        # Determine content type
        if file_path.endswith('.md'):
            content_type = 'documentation'
        elif file_path.endswith('.py'):
            content_type = 'code'
        elif file_path in ['Makefile', 'requirements.txt']:
            content_type = 'configuration'
        else:
            content_type = 'unknown'
        
        # Create repository item
        item = {
            'item_type': content_type,
            'path': file_path,
            'name': path_obj.name,
            'content_hash': content_hash or '',
            'file_size': stat.st_size,
            'mime_type': 'text/plain' if content_type != 'unknown' else 'application/octet-stream',
            'encoding': 'utf-8',
            'is_binary': False,
            'line_count': 0  # We'll skip line counting for now
        }
        
        # Load into Directus
        response = requests.post(f"{DIRECTUS_URL}/items/repository_items", json=item, headers=headers)
        
        if response.status_code == 200:
            print(f"   ✅ Loaded: {file_path} ({content_type})")
            loaded_count += 1
        else:
            print(f"   ❌ Failed to load {file_path}: {response.text}")
    
    print(f"\n📊 Loading complete: {loaded_count} loaded, {skipped_count} skipped")
    return loaded_count

def main():
    """Main test function"""
    print("🧪 Directus Loading Test")
    print("=" * 40)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        return 1
    
    # Check existing items
    check_existing_items(token)
    
    # Load test files
    loaded = load_test_files(token)
    
    if loaded > 0:
        print(f"\n🎉 Success! Loaded {loaded} test files")
        print("🌐 Check them in Directus at: http://localhost:8055/admin")
        print("   Go to: Content > Repository Items")
    else:
        print("\n⚠️ No new files loaded (may already exist)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
