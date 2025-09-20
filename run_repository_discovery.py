#!/usr/bin/env python3
"""
Repository Discovery and Directus Data Loading Script
====================================================

This script runs the repository discovery system and loads the discovered data into Directus.

Author: Beast Mode Framework
Date: 2025-09-20
Version: 1.0
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.append('.')

from src.repository_discovery.simple_repository_discovery import SimpleRepositoryDiscovery
from src.repository_discovery.core.content_inventory_manager import ContentInventoryManager

# Directus configuration
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

def load_repository_items_to_directus(token: str, inventory_data: Dict[str, Any]):
    """Load repository items into Directus"""
    print("📁 Loading repository items into Directus...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Convert inventory data to Directus format
    items = []
    for file_path, file_data in inventory_data.get('files', {}).items():
        item = {
            'item_type': file_data.get('content_type', 'unknown'),
            'path': file_path,
            'name': Path(file_path).name,
            'content_hash': file_data.get('content_hash', ''),
            'file_size': file_data.get('file_size', 0),
            'mime_type': file_data.get('mime_type', ''),
            'encoding': file_data.get('encoding', ''),
            'is_binary': file_data.get('is_binary', False),
            'line_count': file_data.get('line_count', 0)
        }
        items.append(item)
    
    # Load items in batches
    batch_size = 50
    loaded_count = 0
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        for item in batch:
            response = requests.post(f"{DIRECTUS_URL}/items/repository_items",
                                   json=item, headers=headers)
            
            if response.status_code == 200:
                loaded_count += 1
                if loaded_count % 10 == 0:
                    print(f"   Loaded {loaded_count}/{len(items)} items...")
            else:
                print(f"⚠️ Failed to load item {item['name']}: {response.text}")
    
    print(f"✅ Loaded {loaded_count} repository items")
    return loaded_count

def load_specifications_to_directus(token: str, inventory_data: Dict[str, Any]):
    """Load specifications into Directus"""
    print("📋 Loading specifications into Directus...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Find specification files
    spec_files = []
    for file_path, file_data in inventory_data.get('files', {}).items():
        if file_data.get('content_type') == 'specification':
            spec_files.append((file_path, file_data))
    
    loaded_count = 0
    
    for file_path, file_data in spec_files:
        # Create a repository item first to get its ID
        repo_item = {
            'item_type': 'specification',
            'path': file_path,
            'name': Path(file_path).name,
            'content_hash': file_data.get('content_hash', ''),
            'file_size': file_data.get('file_size', 0),
            'mime_type': file_data.get('mime_type', ''),
            'encoding': file_data.get('encoding', ''),
            'is_binary': file_data.get('is_binary', False),
            'line_count': file_data.get('line_count', 0)
        }
        
        # Create repository item
        response = requests.post(f"{DIRECTUS_URL}/items/repository_items",
                               json=repo_item, headers=headers)
        
        if response.status_code == 200:
            repo_item_id = response.json()['data']['id']
            
            # Create specification entry
            spec_item = {
                'repository_item_id': repo_item_id,
                'spec_name': Path(file_path).stem,
                'spec_type': 'requirements',
                'priority': 1,
                'status': 'active',
                'content': file_data.get('content', ''),
                'metadata': {
                    'file_path': file_path,
                    'content_type': file_data.get('content_type', ''),
                    'discovered_at': datetime.now().isoformat()
                }
            }
            
            response = requests.post(f"{DIRECTUS_URL}/items/specifications",
                                   json=spec_item, headers=headers)
            
            if response.status_code == 200:
                loaded_count += 1
                print(f"   Loaded specification: {Path(file_path).name}")
            else:
                print(f"⚠️ Failed to load specification {Path(file_path).name}: {response.text}")
        else:
            print(f"⚠️ Failed to create repository item for {file_path}: {response.text}")
    
    print(f"✅ Loaded {loaded_count} specifications")
    return loaded_count

def main():
    """Main repository discovery and loading process"""
    print("🚀 Repository Discovery and Directus Data Loading")
    print("=" * 60)
    
    # Check if Directus is running
    try:
        response = requests.get(f"{DIRECTUS_URL}/server/health", timeout=5)
        if response.status_code != 200:
            print("❌ Directus is not running. Please start it first:")
            print("   cd deployment/local && docker-compose up directus directus-db")
            return 1
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to Directus. Please start it first:")
        print("   cd deployment/local && docker-compose up directus directus-db")
        return 1
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        return 1
    
    # Run repository discovery
    print("\n🔍 Running repository discovery...")
    discovery = SimpleRepositoryDiscovery()
    
    # Discover repository content
    root_path = Path('.')
    inventory = discovery.discover_repository(root_path, max_depth=5)
    
    print(f"✅ Discovery complete: {inventory.total_files} files, {len(inventory.content_types)} types")
    
    # Convert to data format for Directus
    inventory_data = {
        'files': {},
        'content_types': inventory.content_types,
        'total_files': inventory.total_files,
        'scan_duration': inventory.scan_duration,
        'classification_duration': inventory.classification_duration
    }
    
    # Load data into Directus
    print("\n📊 Loading data into Directus...")
    
    # Load repository items
    repo_items_loaded = load_repository_items_to_directus(token, inventory_data)
    
    # Load specifications
    specs_loaded = load_specifications_to_directus(token, inventory_data)
    
    print(f"\n🎉 Data loading complete!")
    print(f"   Repository items: {repo_items_loaded}")
    print(f"   Specifications: {specs_loaded}")
    print(f"   Total files discovered: {inventory.total_files}")
    print(f"\n🌐 View your data at: {DIRECTUS_URL}/admin")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
